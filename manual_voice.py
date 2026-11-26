
from voice.listener import listen

print("\nXION VOICE RECOGNITION TEST")
print("Say: yes, no, okay, do it, goodbye")

while True:

    text = listen()

    if text:
        print("RECOGNIZED:", text)

        if text in {"goodbye", "exit", "stop"}:
            break
