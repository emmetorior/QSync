from flask import Flask
import asyncio
import json
from threading import Thread

app = Flask(__name__)

# Cache to store news stories
news_cache = []

@app.route('/fetchnews', methods=['GET'])
def get_news():
    #return jsonify(news_cache)
    return json.dumps(news_cache)
# Function to run the subscriber in a separate thread
def run_subscriber():
    asyncio.run(subscribe_to_news())

async def subscribe_to_news():
    host = "localhost"
    port = 8004
    topic = "Breaking News"

    reader, writer = await asyncio.open_connection(host, port)
    print(f"Connected to {host}:{port} as subscriber for front-end")

    # Send subscription command
    subscribe_command = {'command': 'subscribe', 'topic': topic}
    writer.write((str(subscribe_command) + "\n").encode('latin-1'))
    await writer.drain()
    print(f'Subscribed to topic: {topic}')

    try:
        while True:
            data = await reader.readline()
            message = data.decode('latin-1').strip()
            if message:
                print(f'New message for {topic}: {message}')
                # Append to cache
                news_cache.append({'topic': topic, 'message': message})
                # Optionally limit cache size
                if len(news_cache) > 50:  # Keep the last 50 messages
                    news_cache.pop(0)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

# Start the subscriber in a separate thread
subscriber_thread = Thread(target=run_subscriber)
subscriber_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
