import asyncio

async def subscribe_to_topic(host, port, topic = "*"):
    reader, writer = await asyncio.open_connection(host, port)
    print(f'Connected to {host}:{port} as subscriber')

    # Send subscription command
    subscribe_command = {'command': 'subscribe', 'topic': topic}
    writer.write((str(subscribe_command) + "\n").encode('latin-1'))
    await writer.drain()
    print(f'Subscribed to topic: {topic}')

    try:
        while True:
            # Read and decode incoming messages
            data = await reader.readline()
            message = data.decode('latin-1').strip()
            if message:
                print(f'New message for {topic}: {message}')
    except KeyboardInterrupt:
        print("Stopping subscriber...")
    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    host = "localhost"
    port = 8004
    topic = "*"  # Change as needed
    asyncio.run(subscribe_to_topic(host, port, topic))
