import socket


# function client()
# Reads from server and display the change
def client():
    host = '127.0.0.1'  # Server hostname/ip
    port = 5050

    listener = socket.socket()
    listener.connect((host, port))

    while True:
        info = listener.recv(1024).decode()
        print(info)


if __name__ == '__main__':
    client()
