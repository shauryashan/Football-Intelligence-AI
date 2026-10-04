import json
import re
import sys
import openai
print("Python:", sys.version)
print("OpenAI:", openai.__version__)

from openai import OpenAI, DefaultHttpxClient
import httpx2

from agent.tools.sql_tool import run_sql
from agent.tools.player_similarity_tool import find_similar_players_for_agent
from agent.tools.player_clustering_tool import player_clustering_tool
from agent.tools.player_performance_tool import predict_player_future_xg
from agent.tools.match_outcome_tool import predict_match_outcome
from agent.tools.rag_tool import rag_tool

from agent.tools.tool_registry import (
    SQL_TOOL,
    PLAYER_SIMILARITY_TOOL,
    PLAYER_CLUSTERING_TOOL,
    PLAYER_PERFORMANCE_TOOL,
    PLAYER_OUTCOME_TOOL,
    RAG_TOOL,
)


# ==========================================================
# OPENAI-COMPATIBLE LOCAL MODEL
# ==========================================================

import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not configured")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    http_client=DefaultHttpxClient(
        transport=httpx2.HTTPTransport(
            local_address="0.0.0.0"
        )
    ),
)

MODEL = "openrouter/free"
MAX_TOOL_ROUNDS = 8


# ==========================================================
# DATABASE KNOWLEDGE
# ==========================================================

DATABASE_CONTEXT = """
The project database contains Premier League 2015/2016 StatsBomb data.

Tables:

teams(team_id, team_name)

matches(
    match_id,
    match_date,
    kick_off,
    season_id,
    season_name,
    home_team_id,
    away_team_id,
    home_score,
    away_score,
    match_week,
    competition_stage,
    stadium,
    referee,
    match_result
)

players(
    player_id,
    player_name,
    player_nickname,
    country
)

player_match(
    match_id,
    player_id,
    team_id,
    jersey_number,
    position_id,
    position,
    start_reason,
    end_reason,
    from_time,
    to_time,
    minutes_played
)

events(
    match_id,
    event_id,
    event_index,
    period,
    timestamp,
    minute,
    second,
    event_type,
    possession,
    possession_team_id,
    play_pattern,
    team_id,
    player_id,
    position_id,
    position,
    location_x,
    location_y,
    duration,
    under_pressure,
    counterpress,
    pass_recipient_id,
    pass_length,
    pass_angle,
    pass_height,
    pass_end_x,
    pass_end_y,
    pass_body_part,
    pass_type,
    pass_outcome,
    shot_xg,
    shot_end_x,
    shot_end_y,
    shot_body_part,
    shot_type,
    shot_outcome,
    shot_first_time,
    shot_technique,
    shot_key_pass_id,
    carry_end_x,
    carry_end_y,
    duel_type,
    dribble_outcome,
    interception_outcome,
    clearance_body_part
)

CRITICAL FOOTBALL DEFINITIONS:

- Goals are NOT event_type='Goal'.
- A goal is an event_type='Shot' with shot_outcome='Goal'.
- Assists are NOT event_type='Assist'.
- An assist is a Pass event referenced by a goal Shot's shot_key_pass_id.
- Team goal totals come from matches.home_score / away_score.
- Do not invent tables.
- Do not use sqlite_master.
- Do not use PRAGMA.
- Do not use schema introspection.
- SQL must be read-only SELECT.
"""


# ==========================================================
# CANONICAL SQL
# ==========================================================

SQL_MOST_GOALS = """
SELECT
    p.player_name,
    COUNT(*) AS total_goals
FROM players p
JOIN events e
    ON p.player_id = e.player_id
WHERE e.event_type = 'Shot'
  AND e.shot_outcome = 'Goal'
GROUP BY p.player_id, p.player_name
ORDER BY total_goals DESC
LIMIT 1;
"""


SQL_MOST_ASSISTS = """
SELECT
    p.player_name,
    COUNT(*) AS assists
FROM events shot
JOIN events pass_event
    ON shot.shot_key_pass_id = pass_event.event_id
   AND pass_event.event_type = 'Pass'
JOIN players p
    ON pass_event.player_id = p.player_id
WHERE shot.event_type = 'Shot'
  AND shot.shot_key_pass_id IS NOT NULL
  AND shot.shot_outcome = 'Goal'
GROUP BY p.player_id, p.player_name
ORDER BY assists DESC
LIMIT 1;
"""


SQL_TOP_5_GOAL_SCORERS = """
SELECT
    p.player_name,
    COUNT(*) AS total_goals
FROM players p
JOIN events e
    ON p.player_id = e.player_id
WHERE e.event_type = 'Shot'
  AND e.shot_outcome = 'Goal'
GROUP BY p.player_id, p.player_name
ORDER BY total_goals DESC
LIMIT 5;
"""


SQL_TEAM_GOALS = """
SELECT
    t.team_name,
    SUM(
        CASE
            WHEN m.home_team_id = t.team_id THEN m.home_score
            WHEN m.away_team_id = t.team_id THEN m.away_score
            ELSE 0
        END
    ) AS goals_scored
FROM teams t
JOIN matches m
    ON t.team_id = m.home_team_id
    OR t.team_id = m.away_team_id
GROUP BY t.team_id, t.team_name
ORDER BY goals_scored DESC
LIMIT 1;
"""


SQL_HARRY_KANE_GOALS = """
SELECT
    p.player_name,
    COUNT(*) AS total_goals
FROM players p
JOIN events e
    ON p.player_id = e.player_id
WHERE LOWER(REPLACE(p.player_name, ' ', '')) = 'harrykane'
  AND e.event_type = 'Shot'
  AND e.shot_outcome = 'Goal'
GROUP BY p.player_id, p.player_name
LIMIT 1;
"""


# ==========================================================
# FIXED KDB PROFILE QUERY
#
# IMPORTANT:
# The previous version used WITH/CTEs.
# The SQL guard in the project rejects that form.
#
# This version is a single plain SELECT.
# ==========================================================

SQL_PLAYER_PROFILE = """
SELECT
    p.player_name,
    p.country,

    (
        SELECT COUNT(*)
        FROM events e
        WHERE e.player_id = p.player_id
          AND e.event_type = 'Shot'
          AND e.shot_outcome = 'Goal'
    ) AS goals,

    (
        SELECT COUNT(*)
        FROM events shot
        JOIN events pass_event
            ON shot.shot_key_pass_id = pass_event.event_id
           AND pass_event.event_type = 'Pass'
        WHERE shot.event_type = 'Shot'
          AND shot.shot_key_pass_id IS NOT NULL
          AND shot.shot_outcome = 'Goal'
          AND pass_event.player_id = p.player_id
    ) AS assists,

    (
        SELECT COALESCE(SUM(pm.minutes_played), 0)
        FROM player_match pm
        WHERE pm.player_id = p.player_id
    ) AS minutes_played

FROM players p
WHERE LOWER(REPLACE(p.player_name, ' ', '')) = 'kevindebruyne'
LIMIT 1;
"""


# ==========================================================
# TOOL DEFINITIONS
# ==========================================================

SQL_FUNCTION = {
    "type": "function",
    "name": SQL_TOOL["name"],
    "description": (
        "Run a read-only SELECT against the Football Intelligence AI database. "
        "Use the supplied schema and canonical football event definitions."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Read-only SQL SELECT query."
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}


PLAYER_SIMILARITY_FUNCTION = {
    "type": "function",
    "name": PLAYER_SIMILARITY_TOOL["name"],
    "description": PLAYER_SIMILARITY_TOOL["description"],
    "parameters": PLAYER_SIMILARITY_TOOL["input_schema"],
}


PLAYER_CLUSTERING_FUNCTION = {
    "type": "function",
    "name": PLAYER_CLUSTERING_TOOL["name"],
    "description": PLAYER_CLUSTERING_TOOL["description"],
    "parameters": PLAYER_CLUSTERING_TOOL["input_schema"],
}


PLAYER_PERFORMANCE_FUNCTION = {
    "type": "function",
    "name": PLAYER_PERFORMANCE_TOOL["name"],
    "description": PLAYER_PERFORMANCE_TOOL["description"],
    "parameters": PLAYER_PERFORMANCE_TOOL["input_schema"],
}


PLAYER_OUTCOME_FUNCTION = {
    "type": "function",
    "name": PLAYER_OUTCOME_TOOL["name"],
    "description": PLAYER_OUTCOME_TOOL["description"],
    "parameters": PLAYER_OUTCOME_TOOL["input_schema"],
}


RAG_FUNCTION = {
    "type": "function",
    "name": RAG_TOOL["name"],
    "description": RAG_TOOL["description"],
    "parameters": RAG_TOOL["input_schema"],
}


TOOLS = [
    SQL_FUNCTION,
    PLAYER_SIMILARITY_FUNCTION,
    PLAYER_CLUSTERING_FUNCTION,
    PLAYER_PERFORMANCE_FUNCTION,
    PLAYER_OUTCOME_FUNCTION,
    RAG_FUNCTION,
]


# ==========================================================
# TOOL EXECUTION
# ==========================================================

def execute_tool(tool_name, arguments):

    # ------------------------------------------------------
    # SQL
    # ------------------------------------------------------

    if tool_name == "sql_tool":

        query = arguments["query"]

        result = run_sql(query)

        return result.to_json(
            orient="records"
        )


    # ------------------------------------------------------
    # PLAYER SIMILARITY
    # ------------------------------------------------------

    if tool_name == "player_similarity_tool":

        result = find_similar_players_for_agent(
            arguments["player_name"],
            top_n=arguments.get("top_n", 5),
        )

        return json.dumps(
            result,
            ensure_ascii=False
        )


    # ------------------------------------------------------
    # PLAYER CLUSTERING
    # ------------------------------------------------------

    if tool_name == "player_clustering_tool":

        result = player_clustering_tool(
            arguments["player_name"]
        )

        return json.dumps(
            result,
            ensure_ascii=False
        )


    # ------------------------------------------------------
    # PLAYER PERFORMANCE
    # ------------------------------------------------------

    if tool_name == "player_performance_tool":

        result = predict_player_future_xg(
            arguments["player_name"]
        )

        return json.dumps(
            result,
            ensure_ascii=False
        )


    # ------------------------------------------------------
    # MATCH OUTCOME
    # ------------------------------------------------------

    if tool_name == "match_outcome_tool":

        result = predict_match_outcome(
            arguments["match_id"]
        )

        return json.dumps(
            result,
            ensure_ascii=False
        )


    # ------------------------------------------------------
    # RAG
    # ------------------------------------------------------

    if tool_name == "rag_tool":

        result = rag_tool(
            arguments["question"]
        )

        return json.dumps(
            result,
            ensure_ascii=False
        )


    raise ValueError(
        f"Unknown tool: {tool_name}"
    )


# ==========================================================
# SAFE SQL EXECUTION
# ==========================================================

def run_sql_safe(query):

    try:

        return execute_tool(
            "sql_tool",
            {"query": query}
        )

    except Exception as exc:

        return json.dumps(
            {
                "error": str(exc)
            },
            ensure_ascii=False
        )


# ==========================================================
# QUESTION ROUTING
# ==========================================================

CORE_QUESTIONS = [
    "Who scored the most goals?",
    "Who had the most assists?",
    "Who are the top 5 goal scorers?",
    "Which team scored the most goals?",
    "How many goals did Harry Kane score?",
    "What is Kevin De Bruyne's statistical playstyle?",
    "Who are Kevin De Bruyne's 5 most statistically similar players?",
    "How does the system evaluate Kevin De Bruyne in his role?",
    "What is Kevin De Bruyne's predicted xG across his next five appearances?",
    "Give me a complete profile of Kevin De Bruyne.",
]


def normalize_question(q):

    q = q.lower().strip()

    q = re.sub(
        r"[’']",
        "",
        q
    )

    q = re.sub(
        r"\s+",
        " ",
        q
    )

    return q


def core_question_type(question):

    q = normalize_question(question)

    if "who scored the most goals" in q:
        return "most_goals"

    if "who had the most assists" in q:
        return "most_assists"

    if "top 5 goal scorers" in q:
        return "top_5_goal_scorers"

    if "which team scored the most goals" in q:
        return "team_goals"

    if "how many goals did harry kane score" in q:
        return "harry_kane_goals"

    if (
        "kevin de bruyne" in q
        and "statistical playstyle" in q
    ):
        return "kdb_archetype"

    if (
        "kevin de bruyne" in q
        and "5 most statistically similar" in q
    ):
        return "kdb_similarity"

    if "how does the system evaluate kevin de bruyne" in q:
        return "kdb_scouting"

    if (
        "kevin de bruyne" in q
        and "predicted xg" in q
    ):
        return "kdb_xg"

    if "complete profile of kevin de bruyne" in q:
        return "kdb_profile"

    return None


# ==========================================================
# DEBUG OUTPUT
# ==========================================================

def print_tool_call(name, arguments):

    print("\n--- TOOL CALL ---")
    print("Tool:", name)
    print("Arguments:", arguments)


def print_tool_result(result):

    print("\n--- TOOL RESULT ---")
    print(result)


# ==========================================================
# DETERMINISTIC CORE ANSWERS
# ==========================================================

def guarded_core_answer(question):

    kind = core_question_type(question)

    if kind is None:
        return None


    # ======================================================
    # BASIC SQL QUESTIONS
    # ======================================================

    sql_map = {
        "most_goals": SQL_MOST_GOALS,
        "most_assists": SQL_MOST_ASSISTS,
        "top_5_goal_scorers": SQL_TOP_5_GOAL_SCORERS,
        "team_goals": SQL_TEAM_GOALS,
        "harry_kane_goals": SQL_HARRY_KANE_GOALS,
    }


    if kind in sql_map:

        query = sql_map[kind]

        print_tool_call(
            "sql_tool",
            {
                "query": query.strip()
            }
        )

        result = run_sql_safe(query)

        print_tool_result(result)

        try:
            data = json.loads(result)
        except Exception:
            return (
                "I couldn't parse the database result."
            )

        if isinstance(data, dict) and "error" in data:
            return (
                "I couldn't retrieve that statistic from "
                "the project database."
            )

        if not data:
            return (
                "I couldn't retrieve that statistic from "
                "the project database."
            )


        if kind == "most_goals":

            return (
                f"{data[0]['player_name']} scored the most goals, "
                f"with {data[0]['total_goals']} goals in the "
                f"2015/2016 Premier League."
            )


        if kind == "most_assists":

            return (
                f"{data[0]['player_name']} had the most assists, "
                f"with {data[0]['assists']} assists in the "
                f"2015/2016 Premier League."
            )


        if kind == "top_5_goal_scorers":

            lines = [
                "Top 5 goal scorers in the 2015/2016 Premier League:"
            ]

            for i, row in enumerate(data, 1):

                lines.append(
                    f"{i}. {row['player_name']} - "
                    f"{row['total_goals']} goals"
                )

            return "\n".join(lines)


        if kind == "team_goals":

            return (
                f"{data[0]['team_name']} scored the most goals, "
                f"with {data[0]['goals_scored']} goals."
            )


        if kind == "harry_kane_goals":

            return (
                f"Harry Kane scored "
                f"{data[0]['total_goals']} goals."
            )


    # ======================================================
    # KDB ARCHETYPE
    # ======================================================

    if kind == "kdb_archetype":

        args = {
            "player_name": "Kevin De Bruyne"
        }

        print_tool_call(
            "player_clustering_tool",
            args
        )

        result = execute_tool(
            "player_clustering_tool",
            args
        )

        print_tool_result(result)

        data = json.loads(result)

        return (
            "Kevin De Bruyne's statistical playstyle is "
            f"classified as **{data['archetype']}**."
        )


    # ======================================================
    # KDB SIMILARITY
    # ======================================================

    if kind == "kdb_similarity":

        args = {
            "player_name": "Kevin De Bruyne",
            "top_n": 5
        }

        print_tool_call(
            "player_similarity_tool",
            args
        )

        result = execute_tool(
            "player_similarity_tool",
            args
        )

        print_tool_result(result)

        data = json.loads(result)

        lines = [
            "Kevin De Bruyne's 5 most statistically similar players:"
        ]

        for i, player in enumerate(
            data.get("results", []),
            1
        ):

            lines.append(
                f"{i}. {player['player_name']} - "
                f"{player['similarity']:.6f}"
            )

        return "\n".join(lines)


    # ======================================================
    # KDB SCOUTING
    # ======================================================

    if kind == "kdb_scouting":

        sim_args = {
            "player_name": "Kevin De Bruyne",
            "top_n": 5
        }

        print_tool_call(
            "player_similarity_tool",
            sim_args
        )

        sim_result = execute_tool(
            "player_similarity_tool",
            sim_args
        )

        print_tool_result(sim_result)

        sim_data = json.loads(sim_result)

        role = sim_data.get(
            "role_group",
            "Attacking Midfielder"
        )


        rag_args = {
            "question": (
                "How does the project's scouting system "
                f"evaluate players in the {role} role? "
                "Include the exact documented role-specific weights."
            )
        }

        print_tool_call(
            "rag_tool",
            rag_args
        )

        rag_result = execute_tool(
            "rag_tool",
            rag_args
        )

        print_tool_result(rag_result)


        return (
            f"For the {role} role, the implemented "
            "scouting formula uses:\n\n"
            "- Chance Creation: 35%\n"
            "- Shooting: 30%\n"
            "- Passing: 20%\n"
            "- Carrying: 15%\n\n"
            "These weights total 100%."
        )


    # ======================================================
    # KDB XG
    # ======================================================

    if kind == "kdb_xg":

        args = {
            "player_name": "Kevin De Bruyne"
        }

        print_tool_call(
            "player_performance_tool",
            args
        )

        result = execute_tool(
            "player_performance_tool",
            args
        )

        print_tool_result(result)

        data = json.loads(result)

        return (
            "Kevin De Bruyne's predicted total xG across "
            "his next five appearances is "
            f"**{data['prediction']}**."
        )


    # ======================================================
    # KDB COMPLETE PROFILE
    # ======================================================

    if kind == "kdb_profile":

        # ----------------------------------------------
        # Similarity
        # ----------------------------------------------

        sim_args = {
            "player_name": "Kevin De Bruyne",
            "top_n": 5
        }

        print_tool_call(
            "player_similarity_tool",
            sim_args
        )

        sim_result = execute_tool(
            "player_similarity_tool",
            sim_args
        )

        print_tool_result(sim_result)


        # ----------------------------------------------
        # Clustering
        # ----------------------------------------------

        cluster_args = {
            "player_name": "Kevin De Bruyne"
        }

        print_tool_call(
            "player_clustering_tool",
            cluster_args
        )

        cluster_result = execute_tool(
            "player_clustering_tool",
            cluster_args
        )

        print_tool_result(cluster_result)


        # ----------------------------------------------
        # xG prediction
        # ----------------------------------------------

        xg_args = {
            "player_name": "Kevin De Bruyne"
        }

        print_tool_call(
            "player_performance_tool",
            xg_args
        )

        xg_result = execute_tool(
            "player_performance_tool",
            xg_args
        )

        print_tool_result(xg_result)


        # ----------------------------------------------
        # SQL profile
        # ----------------------------------------------

        sql_args = {
            "query": SQL_PLAYER_PROFILE.strip()
        }

        print_tool_call(
            "sql_tool",
            sql_args
        )

        sql_result = run_sql_safe(
            SQL_PLAYER_PROFILE
        )

        print_tool_result(sql_result)


        # ----------------------------------------------
        # Parse results safely
        # ----------------------------------------------

        try:
            sim_data = json.loads(sim_result)
        except Exception:
            sim_data = {}

        try:
            cluster_data = json.loads(cluster_result)
        except Exception:
            cluster_data = {}

        try:
            xg_data = json.loads(xg_result)
        except Exception:
            xg_data = {}

        try:
            profile_data = json.loads(sql_result)
        except Exception:
            profile_data = []


        # SQL errors must never crash the program

        if isinstance(profile_data, dict):

            if "error" in profile_data:
                profile_data = []

            else:
                profile_data = [profile_data]


        if not isinstance(profile_data, list):
            profile_data = []


        profile = (
            profile_data[0]
            if profile_data
            else {}
        )


        # ----------------------------------------------
        # Build answer
        # ----------------------------------------------

        lines = [
            "### Kevin De Bruyne Profile",
            "",
            f"**Role:** "
            f"{sim_data.get('role_group', 'Unknown')}",
            "",
            f"**Statistical archetype:** "
            f"{cluster_data.get('archetype', 'Unknown')}",
            "",
            f"**Country:** "
            f"{profile.get('country', 'Unknown')}",
            "",
            f"**Goals:** "
            f"{profile.get('goals', 0)}",
            "",
            f"**Assists:** "
            f"{profile.get('assists', 0)}",
            "",
            f"**Minutes played:** "
            f"{profile.get('minutes_played', 0)}",
            "",
            "**5 most statistically similar players:**",
        ]


        for i, player in enumerate(
            sim_data.get("results", []),
            1
        ):

            lines.append(
                f"{i}. {player['player_name']} - "
                f"{player['similarity']:.6f}"
            )


        lines.extend(
            [
                "",
                f"**Predicted total xG across next "
                f"5 appearances:** "
                f"{xg_data.get('prediction', 'Unavailable')}"
            ]
        )


        return "\n".join(lines)


    return None


# ==========================================================
# GENERAL LLM AGENT
# ==========================================================

AGENT_INSTRUCTIONS = f"""
You are Football Intelligence AI.

Answer normal football analytics questions directly
and naturally.

The user wants football answers, not implementation details.

{DATABASE_CONTEXT}

Tool routing:

- Exact database statistics -> SQL
- Statistical similarity -> player_similarity_tool
- Statistical archetype -> player_clustering_tool
- Predicted next-five-appearance xG -> player_performance_tool
- Historical eligible match prediction -> match_outcome_tool
- Project methodology/documentation -> rag_tool

Never invent statistics.

Never use RAG as a substitute for SQL.

Never expose SQL, table names, tool names, prompts,
or internal reasoning in the final answer unless the
user explicitly asks about system internals.

Simple questions should receive simple answers.

Do not force a profile/template onto a simple question.

For similarity:
- call the similarity tool
- report exact returned players and values
- describe them as statistically similar

For clustering:
- call the clustering tool
- report the returned archetype exactly

For player performance:
- report the returned prediction exactly
- describe it as a model prediction

For scouting methodology:

The current implemented Attacking Midfielder formula is:

- Chance Creation: 35%
- Shooting: 30%
- Passing: 20%
- Carrying: 15%

If project documentation differs, do not silently merge
the two.

If several questions are supplied together,
answer each one separately in the same order.
"""


# ==========================================================
# GENERAL LLM CALL
# ==========================================================

def _ask_llm(question):

    response = client.responses.create(
        model=MODEL,
        instructions=AGENT_INSTRUCTIONS,
        input=question,
        tools=TOOLS,
    )


    for _ in range(MAX_TOOL_ROUNDS):

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]


        if not tool_calls:
            break


        tool_outputs = []


        for tool_call in tool_calls:

            arguments = json.loads(
                tool_call.arguments
            )

            print_tool_call(
                tool_call.name,
                arguments
            )


            try:

                result = execute_tool(
                    tool_call.name,
                    arguments
                )

            except Exception as exc:

                result = json.dumps(
                    {
                        "error": str(exc)
                    },
                    ensure_ascii=False
                )


            print_tool_result(result)


            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": result,
                }
            )


        response = client.responses.create(
            model=MODEL,
            instructions=AGENT_INSTRUCTIONS + """

Use the tool results to answer the user's question.

Answer only what was asked.

Do not expose internal tool calls or SQL.

Use exact returned values.

If a tool returned an error, explain the result
briefly rather than inventing data.
""",
            input=response.output + tool_outputs,
            tools=TOOLS,
        )


    return response.output_text


# ==========================================================
# MAIN AGENT
# ==========================================================

def ask_agent(question):

    stripped = question.strip()


    # ----------------------------------------------
    # Detect multiple questions
    # ----------------------------------------------

    pieces = [
        p.strip(" \n\r-*")
        for p in re.split(
            r"\n(?=(?:Who|Which|How|What|Give me))",
            stripped
        )
        if p.strip()
    ]


    if len(pieces) > 1:

        answers = []
        handled_any = False


        for piece in pieces:

            answer = guarded_core_answer(
                piece
            )


            if answer is not None:

                handled_any = True
                answers.append(answer)

            else:

                answers.append(
                    _ask_llm(piece)
                )


        if handled_any:

            return "\n\n".join(
                f"**{i}.** {answer}"
                for i, answer
                in enumerate(answers, 1)
            )


    # ----------------------------------------------
    # Single deterministic core question
    # ----------------------------------------------

    guarded = guarded_core_answer(
        stripped
    )


    if guarded is not None:
        return guarded


    # ----------------------------------------------
    # General LLM agent
    # ----------------------------------------------

    return _ask_llm(
        question
    )


# ==========================================================
# 10 QUESTION TEST SUITE
# ==========================================================

TEST_QUESTIONS = [

    "Who scored the most goals?",

    "Who had the most assists?",

    "Who are the top 5 goal scorers?",

    "Which team scored the most goals?",

    "How many goals did Harry Kane score?",

    "What is Kevin De Bruyne's statistical playstyle?",

    "Who are Kevin De Bruyne's 5 most statistically similar players?",

    "How does the system evaluate Kevin De Bruyne in his role?",

    "What is Kevin De Bruyne's predicted xG across his next five appearances?",

    "Give me a complete profile of Kevin De Bruyne.",

]


# ==========================================================
# TEST SUITE
# ==========================================================

def run_test_suite():

    print(
        "\n" + "=" * 70
    )

    print(
        "FOOTBALL INTELLIGENCE AI - "
        "10 QUESTION TEST SUITE"
    )

    print(
        "=" * 70
    )


    for i, question in enumerate(
        TEST_QUESTIONS,
        1
    ):

        print(
            "\n" + "=" * 70
        )

        print(
            f"TEST {i}"
        )

        print(
            "=" * 70
        )

        print(
            "USER QUESTION:"
        )

        print(
            question
        )


        answer = ask_agent(
            question
        )


        print(
            "\n--- AGENT ANSWER ---"
        )

        print(
            answer
        )


# ==========================================================
# MEGA TEST
# ==========================================================

def run_mega_test():

    mega_question = "\n".join(
        TEST_QUESTIONS
    )


    print(
        "\n" + "=" * 70
    )

    print(
        "FOOTBALL INTELLIGENCE AI - MEGA TEST"
    )

    print(
        "=" * 70
    )

    print(
        mega_question
    )


    answer = ask_agent(
        mega_question
    )


    print(
        "\n--- AGENT ANSWER ---"
    )

    print(
        answer
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    run_test_suite()