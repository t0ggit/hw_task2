import socket
import threading
from message import ChatMessage
from time import sleep


class ChatServer:
    def __init__(self):
        self.host = '0.0.0.0'  # IP-адрес сервера
        self.port = 55513  # Порт сервера
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.clients = {}  # Словарь для хранения клиентов и их соединений
        self.stash = {}  # Словарь сохраненных недоставленных сообщений

    def start(self):
        self.server_socket.listen()
        print("Сервер запущен. Ожидание подключений...")
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket, client_address):
        client_id = client_socket.recv(1024).decode()  # Получение идентификатора клиента
        if client_id not in self.clients.keys() and client_id != 'server':
            self.clients[client_id] = client_socket
            print(f"Идентифицирован пользователь: {client_id} @ {client_address}")
            client_socket.send(ChatMessage('server', f'{client_id}', f'Logged in as {client_id}').as_json().encode())
            if client_id in self.stash.keys():
                for unread_msg in self.stash[client_id]:
                    client_socket.send(unread_msg.as_json().encode())

        else:
            print(f"Неудачная попытка идентификации: {client_id}")
            client_socket.send(ChatMessage('server', f'{client_id}', f'Cannot log in as {client_id}.').as_json().encode())
            client_socket.close()
            return

        remainder = ''
        while True:
            msg, remainder = ChatMessage().from_json(remainder + client_socket.recv(1024).decode())

            if msg.dst in self.clients.keys():
                self.clients[msg.dst].send(msg.as_json().encode())
            elif msg.dst == 'server':
                if msg.txt == 'exit':
                    client_socket.close()
                    del self.clients[client_id]
                    print(f"Соединение разорвано: {client_id}")
                    return
            else:
                client_socket.send(
                    ChatMessage('server', client_id, f'Пользователь {msg.dst} не в сети. Сообщение сохранено.')
                    .as_json().encode())
                if msg.dst not in self.stash.keys():
                    self.stash[msg.dst] = list()
                    self.stash[msg.dst].append(msg)
                else:
                    self.stash[msg.dst].append(msg)
                print(self.stash)


if __name__ == "__main__":
    server = ChatServer()
    server.start()
