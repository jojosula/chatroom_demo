# chatroom_demo
This is demo project for chat room by python.

## Prepare Dev Environment

1. Install python
   Download & install Python 3.8.0 from https://www.python.org.

2. Install requirements
    pip install -r res/requirements.txt

3. Execute Server
    python server.py --ca-file D:\johnchang_project\chatroom_demo\conf\server.pem

4. Execute Client
    python client.py --ca-file D:\johnchang_project\chatroom_demo\conf\server.pem --user-name aa
    python client.py --ca-file D:\johnchang_project\chatroom_demo\conf\server.pem --user-name bb
    ...

5. Start chatting!
