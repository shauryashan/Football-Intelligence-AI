from rag_answer import answer_question


test_questions = [
    "What are the scouting score weights for a Central Midfielder?",
    "What are the seven categories used in the scouting profile?",
    "What is the transfer value of Kevin De Bruyne in this dataset?"
]


for question in test_questions:

    print("\n" + "=" * 70)
    print("QUESTION")
    print("=" * 70)

    print(question)

    answer, results = answer_question(
        question,
        top_k=5
    )

    print("\nANSWER")
    print("-" * 70)
    print(answer)

    print("\nSOURCES")
    print("-" * 70)

    for i, result in enumerate(results, start=1):

        print(
            f"{i}. "
            f"{result['source']} | "
            f"{result['section']} | "
            f"{result['similarity']:.4f}"
        )