from memory.database import (
    initialize_database,
    save_memory,
    get_memory,
    delete_memory,
    get_all_memories
)


# Initialize database
initialize_database()


print("\n--- SAVING MEMORY ---")

save_memory(
    "current project",
    "Micro Expression Recognition"
)

print("Memory saved.")


print("\n--- RECALLING MEMORY ---")

memory = get_memory("current project")

print("Current Project:", memory)


print("\n--- UPDATING MEMORY ---")

save_memory(
    "current project",
    "Meta-Learning for Micro Expression Recognition"
)

memory = get_memory("current project")

print("Updated Project:", memory)


print("\n--- ALL MEMORIES ---")

memories = get_all_memories()

for key, value, updated_at in memories:
    print(f"{key}: {value}")
    print(f"Updated: {updated_at}")


print("\n--- DELETING MEMORY ---")

deleted = delete_memory("current project")

print("Deleted:", deleted)


print("\n--- VERIFYING ---")

memory = get_memory("current project")

print("Current Project:", memory)