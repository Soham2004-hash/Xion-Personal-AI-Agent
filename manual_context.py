from agent.context import (
    update_context,
    get_context,
    clear_context,
)


print("=" * 60)
print("XION CONTEXT TEST")
print("=" * 60)

print("\nInitial context:")
print(get_context())


print("\nUpdating context...")

update_context(
    intent="RECALL_MEMORY",
    parameters={
        "key": "current project"
    },
    response="current project is XION."
)


print("\nCurrent context:")
print(get_context())


print("\nClearing context...")

clear_context()


print("\nContext after clearing:")
print(get_context())


print("\n" + "=" * 60)
print("CONTEXT TEST COMPLETE")
print("=" * 60)