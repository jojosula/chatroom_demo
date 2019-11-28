# chatroom_demo
This is demo project for chat room by python.

## Run executable files

### Windows

For convenience, you can find the executable chatroom.exe under chatroom_demo\dist\windows

### Execute Server

   * accept all clients

   ```
   chatroom.exe serve --bind-ip 127.0.0.1 --bind-port 8567 --ca-file D:\your_path\chatroom_demo\conf\server_cert\server.pem
   ```

   * accept authorized clients only

   ```
   chatroom.exe serve --bind-ip 127.0.0.1 --bind-port 8567 --ca-file D:\your_path\chatroom_demo\conf\server_cert\server.pem --allowed-clients D:\your_path\chatroom_demo\conf\client_cert\client1.crt
   ```

### Execute Client

   * connect server without allowed client certificate
   
   ```
   chatroom.exe connect --host localhost --bind-port 8567 --ca-file D:\your_path\chatroom_demo\conf\server_cert\server.pem --handle username
   ```
   
   * connect server with allowed client certificate
   
   ```
   chatroom.exe connect --host localhost --bind-port 8567 --ca-file D:\your_path\chatroom_demo\conf\server_cert\server.pem --client-cert D:\your_path\chatroom_demo\conf\client_cert\client1.pem --handle username
   ```

## Prepare Dev Environment

1. Install python

   Download & install Python 3.8.0 from https://www.python.org.

2. Install requirements

    ```
    pip install -r res/requirements.txt
    ```
    
3. Execute Server

    * accept all clients
    
    ```
    python main.py serve --bind-ip 127.0.0.1 --bind-port 8567 --ca-file D:\your_path\chatroom_demo\conf\server_cert\server.pem
    ```
    
    * accept authorized clients only
    
    ```
    python main.py serve --bind-ip 127.0.0.1 --bind-port 8567 --ca-file D:\your_path\chatroom_demo\conf\server_cert\server.pem --allowed-clients D:\your_path\chatroom_demo\conf\client_cert\client1.crt
    ```

4. Execute Client

    * connect server without allowed client certificate
    
    ```
    python main.py connect --host localhost --bind-port 8567 --ca-file D:\your_path\chatroom_demo\conf\server_cert\server.pem --handle username
    ```
    
    * connect server with allowed client certificate
    
    ```
    python main.py connect --host localhost --bind-port 8567 --ca-file D:\your_path\chatroom_demo\conf\server_cert\server.pem --client-cert D:\your_path\chatroom_demo\conf\client_cert\client1.pem --handle username
    ```

## Package python application

```
pyinstaller -F main.py
```

note: if it shows "TypeError: an integer is required (got type bytes)", you can fix it by installing developer version.

```
pip install https://github.com/pyinstaller/pyinstaller/archive/develop.tar.gz
```
ref: https://github.com/pyinstaller/pyinstaller/issues/4265

## Troubleshooting

### ModuleNotFoundError: No module named '_curses'

python built-in curses not support on windows, there is an extension required. 

Go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses 

Download & install curses‑2.2.1+utf8‑cp38‑cp38

