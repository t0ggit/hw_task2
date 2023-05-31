import socket
import threading
from message import ChatMessage


class ChatClient:
    def __init__(self, client_id):
        self.host = '0.0.0.0'  # IP-адрес сервера
        self.port = 55513  # Порт сервера
        self.client_id = client_id
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        receive_thread = threading.Thread(target=self.receive_messages)
        user_input_thread = threading.Thread(target=self.get_user_inputs)
        self.threads = [receive_thread, user_input_thread]

    def start(self):
        self.client.send(self.client_id.encode())  # Отправка идентификатора клиента на сервер
        for t in self.threads:
            t.start()

    def get_user_inputs(self):
        while True:
            user_input = input()
            if user_input == "exit":
                self.client.send(ChatMessage('', 'server', 'exit').as_json().encode())
                self.client.close()
                main()
            else:
                if len(user_input.split(":")) > 1:
                    destination_id = user_input.split(":")[0]
                    message = ':'.join(user_input.split(":")[1:])
                    msg = ChatMessage(self.client_id, destination_id, message)
                    self.client.send(msg.as_json().encode())

    def receive_messages(self):
        remainder = ''
        while True:
            try:
                message = remainder + self.client.recv(1024).decode()  # Получение сообщения от сервера
            except OSError:
                continue
            if message:
                msg, remainder = ChatMessage().from_json(message)
                print(f"{msg.time} | Сообщение от {msg.src}: {msg.txt}")


def main():
    client_id = input("Введите ваше имя: ")
    client = ChatClient(client_id)
    client.start()


if __name__ == "__main__":
    main()
