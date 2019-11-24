#!/usr/bin/env python

import sys
import asyncio
import websockets
import logging

FORMAT = '%(asctime)-15s %(filename)s - [line:%(lineno)d] %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

if sys.platform == 'win32':
    logging.error("this client does not support on windows, because add_reader is not implemented in event loop")
    exit(1)

URI = "ws://localhost:8765"
USER_NAME = ''
TASKS = set()


def got_stdin_data(queue):
    queue.put(sys.stdin.readline())


def get_message(name, message):
    return "{}> {}".format(name, message)


async def handle_server_message(websocket):
    while True:
        try:
            message = await websocket.recv()
            logging.info(f"got>{message}")
        except Exception as ex:
            logging.info('exception {}'.format(ex))
            break

        # await asyncio.sleep(1)


async def handle_input_message(websocket, name,queue):
    while True:
        message = await queue.get()
        send_message = get_message(name, message)
        await websocket.send(send_message)

        # await asyncio.sleep(1)


async def handle(queue):
    # close ping/pong for unexcept connection close
    async with websockets.connect(URI, ping_interval=None) as websocket:
        await websocket.send(USER_NAME)
        handle_message_task = asyncio.create_task(
            handle_server_message(websocket))
        handle_input_task = asyncio.create_task(
            handle_input_message(websocket, USER_NAME, queue))
        await handle_message_task
        await handle_input_task
        # cancel tasks
        handle_message_task.cancel()
        handle_input_task.cancel()


if __name__ == '__main__':
    USER_NAME = input("What's your name? ")
    queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin.fileno(), got_stdin_data, queue)
    try:
        loop.run_until_complete(handle(queue))
    except KeyboardInterrupt:
        logging.info("interrupt")
    finally:
        loop.close()
