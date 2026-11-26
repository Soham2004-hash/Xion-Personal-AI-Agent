from agent.brain import understand_command


TEST_COMMANDS = [
    "Open YouTube",

    "Can you bring up my GitHub?",

    "What should I work on?",

    "What should I work on next?",

    "Add updating protocol loader to my tasks",

    "Add an important task to finish my project",

    "Complete the protocol task",

    "Delete the data task",

    "Remember that my current project is XION",

    "What is my current project?",

    "What time is it?",

    "Search Wikipedia for artificial intelligence",

    "Hello Xion",

    "Goodbye Xion"
]


print("\n" + "=" * 60)
print("XION INTENT DETECTION TEST")
print("=" * 60)


for command in TEST_COMMANDS:

    print("\n" + "-" * 60)

    print(f"USER: {command}")

    result = understand_command(command)

    print("XION BRAIN:")
    print(result)


print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)