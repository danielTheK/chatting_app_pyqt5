import pickle
import socket
import threading
import json
import hashlib
from typing import Any, Dict

NUM_OF_CLIENTS = 1
LISTEN_PORT = 8865

USERS_PATH = 'users.pickle'


def get_users():
    try:
        with open(USERS_PATH, 'rb') as f:
            return pickle.load(f)
    except EOFError:
        return {}


def update_users(new_users):
    with open(USERS_PATH, 'wb') as f:
        pickle.dump(new_users, f)


users = get_users()
history = {}


class User:
    instances = []

    def __init__(self, client_soc, client_address):
        self.client_soc, self.client_address = client_soc, client_address

        is_correct = False
        name = ''
        while not is_correct:
            self.client_msg = self.client_soc.recv(1024).decode()
            if self.client_msg[0] == "1":
                name, password = self.client_msg[3:].split(",")
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if name in users and users[name] == hashed_password:
                    self.client_soc.sendall("1".encode())
                    is_correct = True
                else:
                    self.client_soc.sendall("0".encode())
            elif self.client_msg[0] == "2":
                name, password = self.client_msg[3:].split(",")
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if name in users:
                    self.client_soc.sendall("0".encode())
                else:
                    self.client_soc.sendall("1".encode())
                    users[name] = hashed_password
                    update_users(users)

        self.__class__.instances.append(self)
        self.name = name
        self.client_soc.recv(1024)
        if self.name in history:
            self.client_soc.sendall(json.dumps(history[self.name]).encode())
        else:
            history[self.name] = {}
            self.client_soc.sendall("$$$".encode())

        try:
            while True:
                self.client_msg = self.client_soc.recv(1024).decode()
                if "@" in self.client_msg:
                    self.sent_to, self.client_msg = self.client_msg.split("@")
                    self.send()
                elif self.client_msg == "121212":
                    contacts = "$$" + ",".join([a for a in users if a != self.name])
                    self.client_soc.sendall(contacts.encode())
        except ConnectionResetError:
            print(f"The user {self.name} has disconnected")
            print(history)
            self.__class__.instances.remove(self)

    def send(self):
        for instance in User.instances:
            if self.sent_to == instance.name:
                instance.client_soc.sendall("{}@{}\n".format(self.name, self.client_msg).encode())

        if self.sent_to in history[self.name]:
            history[self.name][self.sent_to].append("{}@{}\n".format(self.name, self.client_msg))
        else:
            history[self.name][self.sent_to] = [("{}@{}\n".format(self.name, self.client_msg))]

        if self.sent_to in history:
            if self.name in history[self.sent_to]:
                history[self.sent_to][self.name].append("{}@{}\n".format(self.name, self.client_msg))
            else:
                history[self.sent_to][self.name] = [("{}@{}\n".format(self.name, self.client_msg))]
        else:
            history[self.sent_to] = {}
            history[self.sent_to][self.name] = [("{}@{}\n".format(self.name, self.client_msg))]
        print(f"{self.name} history is {history[self.name]}")


def main():
    listening_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('', LISTEN_PORT)
    listening_soc.bind(server_address)
    while True:
        listening_soc.listen(1)
        client_soc, client_address = listening_soc.accept()
        threading.Thread(target=User, args=(client_soc, client_address)).start()


if __name__ == '__main__':
    main()
