# chatroom_demo
This is demo project for chat room by python.

## Prepare Dev Environment

1. Install python
   Download & install Python 3.8.0 from https://www.python.org.

2. Install requirements
    pip install -r res/requirements.txt

3. Execute Server
    python main.py serve --ca-file D:\johnchang_project\chatroom_demo\conf\server.pem

4. Execute Client
    python main.py connect --ca-file D:\johnchang_project\chatroom_demo\conf\server.pem --handle aa
    python main.py connect --ca-file D:\johnchang_project\chatroom_demo\conf\server.pem --handle bb
    ...

5. Start chatting!

## Run executable files

### Windows
* Execute Server
chatroom serve --bind-ip 127.0.0.1 --bind-port 8000 --ca-file D:\johnchang_project\chatroom_demo\conf\server.pem
* Execute Client
chatroom connect --host localhost --bind-port 8000 --ca-file D:\johnchang_project\chatroom_demo\conf\server.pem --handle username
