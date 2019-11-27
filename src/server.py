#!/usr/bin/env python

import sys
import ssl
import argparse
import asyncio
import websockets
import logging
from datetime import datetime

class ChatServer(object):
    """ A Server object for chat room """

    def __init__(self, args):
        # init websocket ssl context
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(args.ca_file)
        self.loop = asyncio.get_event_loop()
        self.bind_ip = args.bind_ip
        self.bind_port = args.bind_port
        self.list_clients = {}

    def add_timestamp(func):
        def warp(self, *args, **kwargs):
            new_result = f'{ datetime.now().strftime("%Y-%m-%d %H:%M") } { func(self, *args, **kwargs) }'
            return new_result
        return warp

    @add_timestamp
    def get_welcome_message(self, name):
        return f'Welcome to websocket-chat, { name }'

    @add_timestamp
    def get_current_users_messages(self, users):
        return f'There are { len(users) } other users connected: { list(users.values()) }'

    @add_timestamp
    def get_saying_messages(self, name, message):
        return f'{ name }: { message }'

    @add_timestamp
    def get_join_event(self, name):
        return f'{ name } has joined the chat'

    @add_timestamp
    def get_leave_event(self, name):
        return f'{ name } has left the chat'

    async def notify_users(self, message, users):
        if users:
            for client, _ in users.items():
                await client.send(message)

    async def handle_client_message(self, websocket, path, name, all_users):
        # Handle messages from this client
        while True:
            try:
                message = await websocket.recv()
            except Exception as ex:
                logging.exception(f'exception { ex }')
                their_name = all_users[websocket]
                del all_users[websocket]
                message = self.get_leave_event(their_name)
                await self.notify_users(message, all_users)
                break
            
            if message is None:
                their_name = all_users[websocket]
                del all_users[websocket]
                logging.info(f'Client closed connection { their_name }')
                message = self.get_leave_event(their_name)
                await self.notify_users(message, all_users)
                break

            message = self.get_saying_messages(name, message)
            logging.info(f'send { message }')
            # Send message to all clients
            await self.notify_users(message, all_users)
            await asyncio.sleep(1)

    async def handle(self, websocket, path):
        logging.info(f'New client {websocket}')
        logging.info(f' ({ len(self.list_clients) } existing clients)')

        # The first line from the client is the name
        name = await websocket.recv()
        # send welcome message
        message = self.get_welcome_message(name)
        await websocket.send(message)
        message = self.get_current_users_messages(self.list_clients)
        await websocket.send(message)
        # notify other users someone joined
        message = self.get_join_event(name)
        await self.notify_users(message, self.list_clients)
        self.list_clients[websocket] = name

        # Handle messages from this client
        await self.handle_client_message(websocket, path, name, self.list_clients)

    def run(self):
        # close ping/pong for unexcept connection close
        start_server = websockets.serve(
            self.handle, self.bind_ip, self.bind_port, ssl=self.ssl_context, ping_interval=None)
        
        self.loop.run_until_complete(start_server)
        return self.loop.run_forever()

    def close(self):
        self.loop.close()


def main(argv=None):
    parser = argparse.ArgumentParser(prog='chat client', description='websocket chat client')
    parser.add_argument('--bind-ip', default='localhost', help='bind ip')
    parser.add_argument('--bind-port', default=8567, help='bind port')
    parser.add_argument('--ca-file', required=False, help='ca file')
    parser.add_argument('--allowed-clients', required=False, help='allowed clients')
    args = parser.parse_args(argv)

    log_format = '%(asctime)-15s  %(filename)s - [line:%(lineno)d] %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)
    
    try:
        server = ChatServer(args)
        server.run()
    except Exception as ex:
        logging.exception(f"{ ex }")
    finally:
        server.close()


if __name__ == "__main__":
    main(sys.argv[1:])
