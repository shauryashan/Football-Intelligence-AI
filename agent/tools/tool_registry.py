# --------------------------------------------------
# SQL TOOL
# --------------------------------------------------

SQL_TOOL = {
    "name": "sql_tool",
    "description": (
        "Execute read-only SQL queries against the "
        "Football Intelligence AI SQLite database to "
        "retrieve exact structured football statistics."
    ),
    "input_schema": {
        "type": "string",
        "description": "A read-only SQL query."
    }
}


# --------------------------------------------------
# PLAYER SIMILARITY TOOL
# --------------------------------------------------

PLAYER_SIMILARITY_TOOL = {
    "name": "player_similarity_tool",
    "description": (
        "Find players statistically similar to a specified "
        "player using the validated 15-feature role-aware "
        "player similarity model."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "player_name": {
                "type": "string",
                "description": "The player's name."
            },
            "top_n": {
                "type": "integer",
                "description": (
                    "Number of similar players to return."
                ),
                "minimum": 1,
                "maximum": 10
            }
        },
        "required": ["player_name"],
        "additionalProperties": False
    }
}


# --------------------------------------------------
# PLAYER CLUSTERING TOOL
# --------------------------------------------------

PLAYER_CLUSTERING_TOOL = {
    "name": "player_clustering_tool",
    "description": (
        "Identify the statistical player archetype assigned "
        "to a player by the validated K-Means clustering model."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "player_name": {
                "type": "string",
                "description": "The player's name."
            }
        },
        "required": ["player_name"],
        "additionalProperties": False
    }
}


# --------------------------------------------------
# PLAYER PERFORMANCE TOOL
# --------------------------------------------------

PLAYER_PERFORMANCE_TOOL = {
    "name": "player_performance_tool",
    "description": (
        "Predict a player's total expected goals (xG) "
        "across their next five appearances using the "
        "validated Random Forest performance prediction "
        "methodology."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "player_name": {
                "type": "string",
                "description": "The player's name."
            }
        },
        "required": ["player_name"],
        "additionalProperties": False
    }
}


# --------------------------------------------------
# MATCH OUTCOME TOOL
# --------------------------------------------------

PLAYER_OUTCOME_TOOL = {
    "name": "match_outcome_tool",
    "description": (
        "Predict the outcome of a historical match in the "
        "validated ML5 held-out test period using the "
        "12-feature compact Random Forest model."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "match_id": {
                "type": "integer",
                "description": (
                    "The historical match ID from the "
                    "validated ML5 feature dataset."
                )
            }
        },
        "required": ["match_id"],
        "additionalProperties": False
    }
}

# --------------------------------------------------
# RAG TOOL
# --------------------------------------------------

RAG_TOOL = {
    "name": "rag_tool",
    "description": (
        "Answer questions about the Football Intelligence AI project's "
        "documented methodology using grounded retrieval from the validated "
        "RAG corpus. USE THIS TOOL for explanations of how the project works, "
        "including scouting methodology, role-aware scoring methodology, "
        "category definitions, role-specific weights, percentile methodology, "
        "statistical archetypes, similarity methodology, ML methodology, "
        "dataset definitions, interpretation guidelines, and limitations. "
        "For role-specific scouting methodology questions, retrieve the exact "
        "documented weights and category definitions when available. For "
        "example, a question about how Central Midfielders are scored should "
        "retrieve the Central Midfielder scouting weights. Do NOT use RAG as "
        "the primary source for numerical player rankings or player-specific "
        "database statistics when a specialized analytical or SQL tool can "
        "provide the result."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": (
                    "A question about the project's documented methodology, "
                    "scouting framework, role-specific weights, football "
                    "metrics, dataset definitions, ML methodology, or "
                    "interpretation guidelines."
                )
            }
        },
        "required": ["question"],
        "additionalProperties": False
    }
}


# --------------------------------------------------
# TOOL REGISTRY
# --------------------------------------------------
TOOLS = [
    SQL_TOOL,
    PLAYER_SIMILARITY_TOOL,
    PLAYER_CLUSTERING_TOOL,
    PLAYER_PERFORMANCE_TOOL,
    PLAYER_OUTCOME_TOOL,
    RAG_TOOL
]


# --------------------------------------------------
# DISPLAY REGISTRY
# --------------------------------------------------

if __name__ == "__main__":

    print("Available tools:\n")

    for tool in TOOLS:

        print(
            f"Tool: {tool['name']}"
        )

        print(
            f"Description: {tool['description']}"
        )

        print(
            f"Input: {tool['input_schema']}"
        )

        print()