import asyncio
import random

# Random titles and messages for publishing
titles = [
    "Breaking News",
    "Product Updates",
    "Highlights",
    "Tech Trends",
    "Daily Motivation"
]

messages = [
    "Product Sales are at an all time high",
    "Expect showers in the evening with a slight chill.",
    "Unexpected results from recent study",
    "AI is transforming industries worldwide.",
    "Diverse teams perform better in the long run"
]
#("Customer Feedback", "New rating received for order #{}")
async def publish_messages(host: str, port: int):
    reader, writer = await asyncio.open_connection(host, port)
    print(f"Connected to server at {host}:{port}")

    try:
        while True:
            title = random.choice(titles)
            message = random.choice(messages)

            #
            cmd = {
                "command": "send",
                "topic": title,
                "message": message,
                "delivery": "all"
            }

            # Send the command to serv
            writer.write((str(cmd) + "\n").encode('utf8'))
            await writer.drain()
            print(f"Published to topic '{title}': {message}")

            # Wait before sending next
            await asyncio.sleep(random.randint(1, 5))
    except KeyboardInterrupt:
        print("Stopping publisher...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        print("Disconnected from server.")

if __name__ == "__main__":
    host = "localhost"
    port = 8004
    asyncio.run(publish_messages(host, port))
