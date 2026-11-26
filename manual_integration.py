from agent.brain import understand_command
from agent.router import process_intent


TEST_COMMANDS = [
    "Open YouTube",

    "What time is it?",

    "What should I work on?",

    "Show my tasks",

    "Add an important task to finish my project",

    "Complete the protocol task",

    "Remember that my current project is XION",

    "What is my current project?",

    "Search Wikipedia for artificial intelligence",

    "Goodbye Xion"
]


print("\n" + "=" * 60)
print("XION BRAIN -> ROUTER INTEGRATION TEST")
print("=" * 60)


for command in TEST_COMMANDS:

    print("\n" + "-" * 60)

    print(f"USER: {command}")


    # --------------------------------------------------------
    # STEP 1: BRAIN
    # --------------------------------------------------------

    intent_data = understand_command(command)

    print("\nBRAIN:")
    print(intent_data)


    # --------------------------------------------------------
    # STEP 2: ROUTER
    # --------------------------------------------------------

    result = process_intent(intent_data)

    print("\nROUTER RESULT:")
    print(result)


print("\n" + "=" * 60)
print("INTEGRATION TEST COMPLETE")
print("=" * 60)