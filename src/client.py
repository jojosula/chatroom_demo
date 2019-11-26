#!/usr/bin/env python

import sys
import ssl
import argparse
import asyncio
import websockets
import logging
import curses
import traceback


class ChatClient(object):
    """ A client object for chat """

    def __init__(self, args):
        # screenObj should be 'stdscr' or a curses window/pad object
        self.stdscr = curses.initscr() # initialize curses
        self.screenObj = Screen(self.stdscr)   # create Screen object
        self.user_name = args.user_name
        self.host = args.host
        self.port = args.port
        # init websocket ssl context
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_context.load_verify_locations(args.ca_file)
        # message queue
        self.queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop()

    async def read_input(self):
        await self.screenObj.doRead(self.queue)

    async def handle_server_message(self, websocket):
        # get message from server and show on screen
        while True:
            try:
                message = await websocket.recv()
                # show on screen
                self.screenObj.addLine(f"{ message }")
            except Exception as ex:
                logging.exception(f'exception { ex }')
                break

    async def handle_input_message(self, websocket):
        # get message from user input and send to server
        while True:
            message = await self.queue.get()
            await websocket.send(message)

    async def __async__connect(self):
        # close ping/pong for unexcept connection close
        async with websockets.connect(f'wss://{self.host}:{self.port}', ssl=self.ssl_context, ping_interval=None) as websocket:
            await websocket.send(self.user_name)
            handle_message_task = asyncio.create_task(
                self.handle_server_message(websocket))
            handle_input_task = asyncio.create_task(
                self.handle_input_message(websocket))
            handle_read_input_task = asyncio.create_task(
                self.read_input())
            await handle_message_task
            await handle_input_task
            await handle_read_input_task
            # cancel tasks
            handle_message_task.cancel()
            handle_input_task.cancel()
            handle_read_input_task.cancel()

    def run(self):
        return self.loop.run_until_complete(self.__async__connect())

    def close(self):
        self.screenObj.close()

class Screen(object):
    def __init__(self, stdscr):
        self.timer = 0
        self.statusText = "Chat Client - Enter your message"
        self.inputText = ''
        self.stdscr = stdscr

        # set screen attributes
        self.stdscr.nodelay(1) # this is used to make input calls non-blocking
        curses.cbreak()
        self.stdscr.keypad(1)
        curses.curs_set(0)     # no annoying mouse cursor

        self.rows, self.cols = self.stdscr.getmaxyx()
        self.lines = []

        curses.start_color()

        # create color pair's 1 and 2
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)

        self.paintStatus(self.statusText)

    def addLine(self, text):
        """ add a line to the internal list of lines"""

        self.lines.append(text)
        self.redisplayLines()

    def redisplayLines(self):
        """ method for redisplaying lines 
            based on internal list of lines """

        self.stdscr.clear()
        self.paintStatus(self.statusText)
        i = 0
        index = len(self.lines) - 1
        while i < (self.rows - 3) and index >= 0:
            self.stdscr.addstr(self.rows - 3 - i, 0, self.lines[index], 
                               curses.color_pair(2))
            i = i + 1
            index = index - 1
        self.stdscr.refresh()

    def paintStatus(self, text):
        self.stdscr.addstr(self.rows-2,0,text + ' ' * (self.cols-len(text)), 
                           curses.color_pair(1))
        # move cursor to input line
        self.stdscr.move(self.rows-1, self.cols-1)

    async def doRead(self, queue):
        """ Input is ready! """
        curses.noecho()
        while True:
            c = self.stdscr.getch() # read a character

            if c == curses.KEY_BACKSPACE:
                self.inputText = self.inputText[:-1]

            elif c == curses.KEY_ENTER or c == 10:
                queue.put_nowait(self.inputText)
                self.inputText = ''

            else:
                if len(self.inputText) == self.cols-2:
                    return
                # get char
                if c >= 0:
                    self.inputText = self.inputText + chr(c)

            self.stdscr.addstr(self.rows-1, 0, 
                            self.inputText + (' ' * (
                            self.cols-len(self.inputText)-2)))
            self.stdscr.move(self.rows-1, len(self.inputText))
            self.stdscr.refresh()
            await asyncio.sleep(0.1)

    def close(self):
        """ clean up """
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()


def main(argv=None):
    parser = argparse.ArgumentParser(prog='chat client', description='websocket chat client')
    parser.add_argument('--user-name', default='Username', help='user name')
    parser.add_argument('--host', default='localhost', help='bind ip')
    parser.add_argument('--port', default=8567, help='bind port')
    parser.add_argument('--ca-file', required=False, help='ca file')
    parser.add_argument('--client-cert', required=False, help='client certificate')
    args = parser.parse_args(argv)

    log_format = '%(asctime)-15s %(filename)s - [line:%(lineno)d] %(message)s'
    logging.basicConfig(filename='client_debug.log', level=logging.INFO, format=log_format)

    try:
        client = ChatClient(args)
        client.run()
    except Exception as ex:
        logging.exception(f"{ ex }")
    finally:
        client.close()


if __name__ == '__main__':
    main(sys.argv[1:])
