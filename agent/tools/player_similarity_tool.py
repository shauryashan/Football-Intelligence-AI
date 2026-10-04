import sys
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ML_DIR = PROJECT_ROOT / "ml"

if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))


# --------------------------------------------------
# IMPORT VALIDATED SIMILARITY MODEL
# --------------------------------------------------

import player_similarity


# --------------------------------------------------
# PLAYER SIMILARITY TOOL
# --------------------------------------------------

def find_similar_players_for_agent(player_name, top_n=5):

    df = player_similarity.df
    similarity_matrix = player_similarity.similarity_matrix

    # ----------------------------------------------
    # Find player
    # ----------------------------------------------

    matches = df[
        df["player_name"].str.lower()
        == player_name.lower()
    ]

    if matches.empty:
        return {
            "error": f"Player not found: {player_name}"
        }

    player_index = matches.index[0]

    player_role = df.loc[
        player_index,
        "role_group"
    ]

    # ----------------------------------------------
    # Restrict to same role
    # ----------------------------------------------

    role_mask = (
        df["role_group"] == player_role
    )

    role_indices = df.index[role_mask]

    player_position = (
        df.index.get_loc(player_index)
    )

    similarities = similarity_matrix[
        player_position
    ]

    results = []

    for index in role_indices:

        if index == player_index:
            continue

        matrix_position = (
            df.index.get_loc(index)
        )

        results.append({
            "player_name":
                df.loc[index, "player_name"],

            "role_group":
                df.loc[index, "role_group"],

            "similarity":
                round(
                    float(
                        similarities[matrix_position]
                    ),
                    6
                )
        })

    results_df = (
        pd.DataFrame(results)
        .sort_values(
            "similarity",
            ascending=False
        )
        .head(top_n)
        .reset_index(drop=True)
    )

    return {
        "player": player_name,
        "role_group": player_role,
        "results":
            results_df.to_dict(
                orient="records"
            )
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    result = find_similar_players_for_agent(
        "Kevin De Bruyne",
        top_n=5
    )

    print("\n" + "=" * 60)
    print("PLAYER SIMILARITY TOOL")
    print("=" * 60)

    print(result)