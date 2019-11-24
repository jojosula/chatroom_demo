#!/usr/bin/env python

import asyncio
import websockets
import logging

FORMAT = '%(asctime)-15s  %(filename)s - [line:%(lineno)d] %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

# logger = logging.getLogger('websockets')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())

LIST_CLIENTS = {}

def get_welcome_message(name):
    return 'Welcome to websocket-chat, {}'.format(name)

def get_current_users_messages(users):
    return 'There are {} other users connected: {}'.format(len(users), list(users.values()))

def get_saying_messages(name, message):
    return 'send {}: {}'.format(name, message)

def get_join_event(name):
    return name + ' has joined the chat'

def get_leave_event(name):
    return name + ' has left the chat'

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
            logging.info('exception {}'.format(ex))
            their_name = all_users[websocket]
            del all_users[websocket]
            message = get_leave_event(name)
            await notify_users(message, all_users)
            break
        if message is None:
            their_name = all_users[websocket]
            del all_users[websocket]
            logging.info('Client closed connection {}'.format(websocket))
            message = get_leave_event(name)
            await notify_users(message, all_users)
            break

        logging.info('recv {}'.format(message))
        message = get_saying_messages(name, message)
        logging.info('send {}: {}'.format(name, message))
        # Send message to all clients
        await notify_users(message, all_users)
        await asyncio.sleep(1)


async def handle(websocket, path):
    logging.info('New client {}'.format(websocket))
    logging.info(' ({} existing clients)'.format(len(LIST_CLIENTS)))

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


if __name__ == '__main__':
    # close ping/pong for unexcept connection close
    start_server = websockets.serve(handle, "localhost", 8765, ping_interval=None)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
