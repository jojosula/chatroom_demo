#!/usr/bin/env python

import sys
import argparse
import logging
from client import ChatClient
from server import ChatServer

def chat_factory(args):
    ACTION_SERVE='serve'
    ACTION_CONNECT='connect'
    if args.action.lower() == ACTION_SERVE:
        return ChatServer(args)
    if args.action.lower() == ACTION_CONNECT:
        return ChatClient(args)


def main(argv=None):
    parser = argparse.ArgumentParser(prog='chatroom program', description='chatroom program include client/server')
    parser.add_argument('action', help='action argument only accept [serve, connect]')
    parser.add_argument('--bind-ip', default='localhost', help='bind ip')
    parser.add_argument('--bind-port', default=8567, help='bind port')
    parser.add_argument('--allowed-clients', required=False, help='allowed clients certificate folder path')
    parser.add_argument('--handle', default='Username', help='user name')
    parser.add_argument('--host', default='localhost', help='bind ip')
    parser.add_argument('--port', default=8567, help='bind port')
    parser.add_argument('--ca-file', required=True, help='ca file')
    parser.add_argument('--client-cert', required=False, help='client certificate')
    args = parser.parse_args(argv)

    log_format = '%(asctime)-15s %(filename)s - [line:%(lineno)d] %(message)s'
    logging.basicConfig(filename='debug.log', level=logging.INFO, format=log_format)

    chatObj = None
    try:
        chatObj = chat_factory(args)
        chatObj.run()
    except Exception as ex:
        logging.exception(f"{ ex }")
    finally:
        if chatObj:
            chatObj.close()


if __name__ == '__main__':
    main(sys.argv[1:])
