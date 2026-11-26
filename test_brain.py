from ollama import chat


SYSTEM_PROMPT = """
You are XION, a personal AI assistant for Soham.

Your name is XION.

You should behave as Soham's personal AI assistant.

You can help with:
- managing tasks
- remembering information
- opening applications and websites
- answering questions
- helping with programming and research

Be concise, helpful, and professional.

Never introduce yourself as Qwen or as an underlying language model.
Always introduce yourself as XION.
"""


def ask_xion(user_message):
    response = chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return response["message"]["content"]


if __name__ == "__main__":

    print("\nTesting XION Brain...\n")

    response = ask_xion(
        "Hello Xion. Introduce yourself and tell me what you can do."
    )

    print("XION:")
    print(response)