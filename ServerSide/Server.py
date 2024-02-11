import pickle
import socket
import threading
import json
import hashlib

LISTEN_PORT = 8865

USERS_PATH = 'users.pickle'
HISTORY_PATH = 'history.pickle'
FILE_ID_PATH = 'file-id.pickle'
FILES_PATH = 'files.pickle'


def get_users():
    try:
        with open(USERS_PATH, 'rb') as f:
            return pickle.load(f)
    except EOFError:
        return {}


def update_users(new_users):
    with open(USERS_PATH, 'wb') as f:
        pickle.dump(new_users, f)


def get_history():
    try:
        with open(HISTORY_PATH, 'rb') as f:
            return pickle.load(f)
    except EOFError:
        return {}


def update_history(new_users):
    with open(HISTORY_PATH, 'wb') as f:
        pickle.dump(new_users, f)


def get_file_id():
    try:
        with open(FILE_ID_PATH, 'rb') as f:
            return pickle.load(f)
    except EOFError:
        return 0


def update_file_id(new_file_id):
    with open(FILE_ID_PATH, 'wb') as f:
        pickle.dump(new_file_id, f)


def get_files():
    try:
        with open(FILES_PATH, 'rb') as f:
            return pickle.load(f)
    except EOFError:
        return {}


def update_files(new_files):
    with open(FILES_PATH, 'wb') as f:
        pickle.dump(new_files, f)

def reset_all_history(): # debug purposes
    update_file_id(0)
    update_history({})
    update_users({})
    update_files({})
reset_all_history()
users = get_users()
history = get_history()
file_id = get_file_id()
files = get_files()

connected_users = []# no need to save it from run to run
class User:
    instances = []

    def __init__(self, client_soc, client_address):
        global file_id
        self.client_soc, self.client_address = client_soc, client_address

        is_correct = False
        name = ''
        while not is_correct:
            self.client_msg = self.client_soc.recv(1024).decode()
            if self.client_msg[0] == "1":
                name, password = self.client_msg[3:].split(",")
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if name in users and users[name] == hashed_password and name not in connected_users:
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
        connected_users.append(name)
        self.client_soc.recv(1024)
        if self.name in history:
            print(f'history[self.name]={history[self.name]}')
            self.client_soc.sendall(json.dumps(history[self.name]).encode())
        else:
            history[self.name] = {}
            self.client_soc.sendall("$$$".encode())

        try:
            while True:
                self.client_msg = self.client_soc.recv(1024)
                if self.client_msg[:3] == b"7$$":
                    self.sent_to, file_name, size, file_data = self.client_msg[3:].split(b"@")
                    self.sent_to, file_name = self.sent_to.decode(), file_name.decode()
                    while file_data[-7:] != b"$$END$$":
                        file_data += self.client_soc.recv(10024)
                    file_data = file_data[:-7]
                    #self.client_soc.sendall(f"11$${file_id}".encode()) #so the sender would also have the id in cace he want to download from the server either
                    with open(str(file_id), "wb") as f:
                        f.write(file_data)
                    files[str(file_id)] = file_name
                    update_files(files)
                    file_id += 1
                    update_file_id(file_id)
                    size = size.decode()
                    self.send_file_notification(file_name, size)
                elif self.client_msg[:3] == b"6$$": #requesting file
                    file_id = self.client_msg[3:].decode()
                    with open(str(file_id), "rb") as f:
                        file_data = f.read()
                    self.client_soc.sendall(f"10$${files[file_id]}$$".encode() + file_data + b"$$END$$") # 10$${file_name}$${file}$$END$$
                else:
                    self.client_msg = self.client_msg.decode()
                    if "@" in self.client_msg:
                        self.sent_to, self.client_msg = self.client_msg.split("@")
                        self.send()
                    elif self.client_msg == "121212":
                        contacts = "$$" + ",".join([a for a in users if a != self.name])
                        self.client_soc.sendall(contacts.encode())
        except ConnectionResetError:
            connected_users.remove(self.name)
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
        update_history(history)
        print(f"{self.name} history is {history[self.name]}")

    def send_file_notification(self, file_name, file_size):  # protocol: 8$$sender@file_name@file_size@file_id
        for instance in User.instances:
            if self.sent_to == instance.name:
                instance.client_soc.sendall(f"8$${self.name}@{file_name}@{file_size}@{file_id-1}".encode())

        if self.sent_to in history[self.name]:
            history[self.name][self.sent_to].append(f"8$${self.name}@{file_name}@{file_size}@{file_id-1}")
        else:
            history[self.name][self.sent_to] = [f"8$${self.name}@{file_name}@{file_size}@{file_id-1}"]

        if self.sent_to in history:
            if self.name in history[self.sent_to]:
                history[self.sent_to][self.name].append(f"8$${self.name}@{file_name}@{file_size}@{file_id-1}")
            else:
                history[self.sent_to][self.name] = [f"8$${self.name}@{file_name}@{file_size}@{file_id-1}"]
        else:
            history[self.sent_to] = {}
            history[self.sent_to][self.name] = [f"8$${self.name}@{file_name}@{file_size}@{file_id-1}"]
        update_history(history)
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
