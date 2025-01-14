import sys, asyncio, ast, random
from collections import defaultdict

topics = defaultdict(lambda: [])
topics_reverse = defaultdict(lambda: [])



async def handle_client(reader, writer):
    print('New client connected...')
    try:
        while True:
            line = (await reader.readline()).decode('latin-1').strip()
            if not line:
                break  #Disconnect if no data
            print(f'Received: {line}')
            cmd = ast.literal_eval(line)

            if cmd['command'] == 'subscribe':
                topics[cmd['topic']].append(writer)
                topics_reverse[writer].append(cmd['topic'])
                print(f'Subscribed to topic: {cmd["topic"]}')
            elif cmd['command'] == 'send':
                if cmd['delivery'] == 'all':
                    writers = topics[cmd['topic']]
                else:  # "one" delivery
                    writers = (
                        [random.choice(topics[cmd['topic']])]
                        if topics[cmd['topic']]
                        else []
                    )

                for w in writers:
                    # Send the message with a newline to delimit
                    message = f"{cmd['message']}\n"
                    w.write(message.encode('latin-1'))
                    await w.drain()  # Ensure message is fully sent
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if writer in topics_reverse:
            for topic in topics_reverse[writer]:
                topics[topic].remove(writer)
                print(f'Removing writer from topic {topic}')
            del topics_reverse[writer]
        writer.close()
        await writer.wait_closed()
        print('Client disconnected...')
async def run_server(host, port):
    server = await asyncio.start_server(handle_client, host, port)
    print(f'Listening on {host}:{port}...')
    async with server:
        await server.serve_forever()

#asyncio.run(run_server(host='localhost', port=int(sys.argv[1])))
asyncio.run(run_server(host='localhost', port=8004))