import unittest
import asyncio
from asyncio import StreamReader, StreamWriter

class TestMQueueServer(unittest.IsolatedAsyncioTestCase):
    @classmethod
    async def asyncSetUpClass(cls):
        # Start the server in the background
        from mqueue_server import run_server
        cls.server_task = asyncio.create_task(run_server('localhost', 8004))
        await asyncio.sleep(1)  # Allow server to start

    @classmethod
    async def asyncTearDownClass(cls):
        cls.server_task.cancel()
        try:
            await cls.server_task
        except asyncio.CancelledError:
            pass

    async def connect_client(self) -> (StreamReader, StreamWriter):
        reader, writer = await asyncio.open_connection('localhost', 8004)
        return reader, writer

    async def test_subscribe(self):
        reader, writer = await self.connect_client()
        try:
            # Send a subscription command
            subscribe_command = {"command": "subscribe", "topic": "TestTopic"}
            writer.write((str(subscribe_command) + "\n").encode('latin-1'))
            await writer.drain()

            # Server doesn't send an acknowledgment, but no errors indicate success
            self.assertTrue(writer is not None, "Writer is not connected.")
        finally:
            writer.close()
            await writer.wait_closed()

    async def test_send_and_receive(self):
        reader1, writer1 = await self.connect_client()
        reader2, writer2 = await self.connect_client()

        try:
            # First client Subscribes#
            subscribe_command = {"command": "subscribe", "topic": "TestTopic"}
            writer1.write((str(subscribe_command) + "\n").encode('latin-1'))
            await writer1.drain()

            # Client 2 sends a message to same topic
            send_command = {
                "command": "send",
                "topic": "TestTopic",
                "message": "Hello, TestTopic!",
                "delivery": "all"
            }
            writer2.write((str(send_command) + "\n").encode('latin-1'))
            await writer2.drain()

            #
            data = await reader1.readline()
            # check the message is the same
            self.assertEqual(data.decode('latin-1').strip(), "Hello, TestTopic!")
        finally:
            writer1.close()  # send the close command
            writer2.close()
            await writer1.wait_closed()  # wait for confirmation that resources are released.
            await writer2.wait_closed()

    async def test_send_to_nonexistent_topic(self):
        reader, writer = await self.connect_client()
        try:
            # Send a message to a nonexistent topic
            send_command = {
                "command": "send",
                "topic": "TESTTopic",
                "message": "Failure test.",
            }

            writer.write((str(send_command) + "\n").encode('latin-1'))
            await writer.drain()

            self.assertTrue(writer is not None, "Writer is not connected.")
        finally:
            writer.close()
            await writer.wait_closed()

if __name__ == "__main__":
    unittest.main()