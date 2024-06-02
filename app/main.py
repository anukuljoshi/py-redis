import socket
import threading


def handle_request(connection):
    print("connection", connection)
    connection.sendall(b"+PONG\r\n")


def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        connection, _ = server_socket.accept()
        threading.Thread(target=lambda: handle_request(connection)).start()


if __name__ == "__main__":
    main()
