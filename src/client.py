#!/usr/bin/env python

import sys
import ssl
import argparse
import asyncio
import websockets
import logging

FORMAT = '%(asctime)-15s %(filename)s - [line:%(lineno)d] %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

# if sys.platform == 'win32':
#     logging.error("this client does not support on windows, because add_reader is not implemented in event loop")
#     exit(1)

TASKS = set()


def got_stdin_data(queue):
    queue.put_nowait(sys.stdin.readline())


def get_message(message):
    return f"{ message }"


async def handle_server_message(websocket):
    while True:
        try:
            message = await websocket.recv()
            print(f"{ message }")
            #logging.info(f"got>{ message }")
        except Exception as ex:
            logging.info(f'exception { ex }')
            break


async def handle_input_message(websocket, name,queue):
    while True:
        message = await queue.get()
        send_message = get_message(message)
        await websocket.send(send_message)


async def handle(queue, args):
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(args.ca_file)
    # close ping/pong for unexcept connection close
    async with websockets.connect(f'wss://{args.host}:{args.port}', ssl=ssl_context, ping_interval=None) as websocket:
        await websocket.send(args.user_name)
        handle_message_task = asyncio.create_task(
            handle_server_message(websocket))
        handle_input_task = asyncio.create_task(
            handle_input_message(websocket, args.user_name, queue))
        await handle_message_task
        await handle_input_task
        # cancel tasks
        handle_message_task.cancel()
        handle_input_task.cancel()


def main(argv=None):
    parser = argparse.ArgumentParser(prog='chat client', description='websocket chat client')
    parser.add_argument('--user-name', default='Username', help='user name')
    parser.add_argument('--host', default='localhost', help='bind ip')
    parser.add_argument('--port', default=8567, help='bind port')
    parser.add_argument('--ca-file', required=False, help='ca file')
    parser.add_argument('--client-cert', required=False, help='client certificate')
    args = parser.parse_args(argv)

    queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin.fileno(), got_stdin_data, queue)
    try:
        loop.run_until_complete(handle(queue, args))
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, 
            limit=2, file=sys.stdout)
    finally:
        loop.close()


if __name__ == '__main__':
    main(sys.argv[1:])
