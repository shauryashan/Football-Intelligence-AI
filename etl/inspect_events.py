import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EVENT_FILE = PROJECT_ROOT / "open-data-master" / "data" / "events" / "3753972.json"

with open(EVENT_FILE, "r", encoding="utf-8") as f:
    events = json.load(f)

print("Number of events:", len(events))


# ---------------------------------------------------------
# Count event types
# ---------------------------------------------------------

event_types = {}

for event in events:
    event_type = event.get("type", {}).get("name")

    if event_type:
        event_types[event_type] = event_types.get(event_type, 0) + 1


print("\n--- Event Types ---")

for event_type, count in sorted(
    event_types.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{event_type}: {count}")


# ---------------------------------------------------------
# Inspect representative event structures
# ---------------------------------------------------------

events_to_inspect = [
    "Pass",
    "Shot",
    "Carry",
    "Pressure",
    "Duel",
    "Dribble",
    "Interception",
    "Ball Recovery",
    "Foul Committed",
    "Clearance",
]


print("\n\n========================================")
print("REPRESENTATIVE EVENT STRUCTURES")
print("========================================")


for event_type in events_to_inspect:

    example = next(
        (
            event
            for event in events
            if event.get("type", {}).get("name") == event_type
        ),
        None
    )

    print(f"\n\n{'=' * 60}")
    print(f"{event_type}")
    print(f"{'=' * 60}")

    if example:
        print(example)
    else:
        print("No example found.")

# ---------------------------------------------------------
# Inspect important outcome examples
# ---------------------------------------------------------

print("\n\n========================================")
print("IMPORTANT OUTCOME EXAMPLES")
print("========================================")


# Find a pass with an outcome
pass_with_outcome = next(
    (
        event
        for event in events
        if event.get("type", {}).get("name") == "Pass"
        and event.get("pass", {}).get("outcome")
    ),
    None
)

print("\n--- Pass with outcome ---")

if pass_with_outcome:
    print(pass_with_outcome)
else:
    print("No pass with outcome found.")


# Find a shot that resulted in a goal
goal_shot = next(
    (
        event
        for event in events
        if event.get("type", {}).get("name") == "Shot"
        and event.get("shot", {}).get("outcome", {}).get("name") == "Goal"
    ),
    None
)

print("\n--- Goal shot ---")

if goal_shot:
    print(goal_shot)
else:
    print("No goal shot found in this match.")