#!/usr/bin/env python

import sys
import ssl
import argparse
import asyncio
import websockets
import logging
from datetime import datetime

LIST_CLIENTS = {}

def add_timestamp(func):
    def warp(*args, **kwargs):
        new_result = f'{ datetime.now().strftime("%Y-%m-%d %H:%M") } { func(*args, **kwargs) }'
        return new_result
    return warp

@add_timestamp
def get_welcome_message(name):
    return f'Welcome to websocket-chat, { name }'

@add_timestamp
def get_current_users_messages(users):
    return f'There are { len(users) } other users connected: { list(users.values()) }'

@add_timestamp
def get_saying_messages(name, message):
    return f'{ name }: { message }'

@add_timestamp
def get_join_event(name):
    return f'{ name } has joined the chat'

@add_timestamp
def get_leave_event(name):
    return f'{ name } has left the chat'

async def notify_users(message, users):
    if users:
        for client, _ in users.items():
            await client.send(message)

async def handle_client_message(websocket, path, name, all_users):
    # Handle messages from this client
    while True:
        try:
            message = await websocket.recv()
        except Exception as ex:
            logging.info(f'exception { ex }')
            their_name = all_users[websocket]
            del all_users[websocket]
            message = get_leave_event(their_name)
            await notify_users(message, all_users)
            break
        
        if message is None:
            their_name = all_users[websocket]
            del all_users[websocket]
            logging.info(f'Client closed connection { their_name }')
            message = get_leave_event(their_name)
            await notify_users(message, all_users)
            break

        message = get_saying_messages(name, message)
        logging.info(f'send { message }')
        # Send message to all clients
        await notify_users(message, all_users)
        await asyncio.sleep(1)


async def handle(websocket, path):
    global LIST_CLIENTS
    logging.info(f'New client {websocket}')
    logging.info(f' ({ len(LIST_CLIENTS) } existing clients)')

    # The first line from the client is the name
    name = await websocket.recv()
    # send welcome message
    message = get_welcome_message(name)
    await websocket.send(message)
    message = get_current_users_messages(LIST_CLIENTS)
    await websocket.send(message)
    # notify other users someone joined
    message = get_join_event(name)
    await notify_users(message, LIST_CLIENTS)
    LIST_CLIENTS[websocket] = name

    # Handle messages from this client
    await handle_client_message(websocket, path, name, LIST_CLIENTS)


def main(argv=None):
    parser = argparse.ArgumentParser(prog='chat client', description='websocket chat client')
    parser.add_argument('--bind-ip', default='localhost', help='bind ip')
    parser.add_argument('--bind-port', default=8567, help='bind port')
    parser.add_argument('--ca-file', required=False, help='ca file')
    parser.add_argument('--allowed-clients', required=False, help='allowed clients')
    args = parser.parse_args(argv)

    log_format = '%(asctime)-15s  %(filename)s - [line:%(lineno)d] %(message)s'
    logging.basicConfig(filename='server_debug.log', level=logging.INFO, format=log_format)
    # init websocket ssl context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(args.ca_file)
    # close ping/pong for unexcept connection close
    start_server = websockets.serve(
        handle, args.bind_ip, args.bind_port, ssl=ssl_context, ping_interval=None)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    try:
        loop.run_forever()
    except Exception as ex:
        logging.exception(f"{ ex }")
    finally:
        loop.close()

        
if __name__ == "__main__":
    main(sys.argv[1:])
