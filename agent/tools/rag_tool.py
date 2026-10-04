import json
import sys
from pathlib import Path


# Add project root to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from rag.rag_answer import answer_question


def rag_tool(question):

    answer, results = answer_question(question)

    return {
        "question": question,
        "answer": answer,
        "retrieved_sources": results
    }

if __name__ == "__main__":

    test_question = (
        "How is the role-aware scouting score calculated?"
    )

    result = rag_tool(test_question)

    print("\n" + "=" * 60)
    print("RAG TOOL")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )