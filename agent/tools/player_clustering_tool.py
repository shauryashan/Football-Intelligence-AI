from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data"

CLUSTERS_FILE = DATA_DIR / "player_clusters.csv"


def player_clustering_tool(player_name):

    clusters = pd.read_csv(
        CLUSTERS_FILE
    )

    matches = clusters[
        clusters["player_name"].str.lower()
        == player_name.lower()
    ]

    if matches.empty:

        return {
            "error": f"Player not found: {player_name}"
        }

    player = matches.iloc[0]

    return {
        "player": player["player_name"],
        "cluster": int(player["cluster"]),
        "archetype": player["archetype"]
    }


if __name__ == "__main__":

    player = "Kevin De Bruyne"

    result = player_clustering_tool(
        player
    )

    print("\n" + "=" * 60)
    print("PLAYER CLUSTERING TOOL")
    print("=" * 60)

    print(result)