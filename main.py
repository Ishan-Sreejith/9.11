import os
import uuid
import socket
import threading

# Simulated file system (in-memory)
file_system = {"root": {}}

# Default users
users = {"admin": "password"}

# Simulated process table
processes = []
current_working_directory = ["root"]

# Server settings for chat
CHAT_HOST = '127.0.0.1'
CHAT_PORT = 65432

# Global chat variables
clients = []
usernames = {}

def boot():
    print("Booting the integrated text OS with chat...")
    threading.Thread(target=start_chat_server, daemon=True).start()
    user_login()

def user_login():
    username = input("Username: ")
    password = input("Password: ")
    if username in users and users[username] == password:
        print(f"Welcome, {username}!")
        kernel(username)
    else:
        print("Invalid credentials. Shutting down...")

def kernel(current_user):
    while True:
        command = input(f"{current_user}@shell> ").strip().split()
        if not command:
            continue
        cmd = command[0]
        args = command[1:]

        if cmd == "exit":
            print("Shutting down...")
            break
        elif cmd == "create":
            create_file(args)
        elif cmd == "read":
            read_file(args)
        elif cmd == "delete":
            delete_file(args)
        elif cmd == "ls":
            list_files(args)
        elif cmd == "mkdir":
            make_directory(args)
        elif cmd == "rmdir":
            remove_directory(args)
        elif cmd == "cd":
            change_directory(args)
        elif cmd == "useradd":
            user_add(args)
        elif cmd == "userdel":
            user_del(args)
        elif cmd == "users":
            list_users()
        elif cmd == "passwd":
            change_password(args)
        elif cmd == "run":
            run_process(args)
        elif cmd == "ps":
            list_processes()
        elif cmd == "kill":
            kill_process(args)
        elif cmd == "download":
            download_file(args)
        elif cmd == "fetch":
            fetch_web_content(args)
        elif cmd == "chat":
            chat_client()
        elif cmd == "help":
            show_help()
        else:
            print("Unknown command. Type 'help' for a list of available commands.")

def create_file(args):
    if len(args) != 1:
        print("Usage: create <filename>")
        return
    filename = args[0]
    path, fname = os.path.split(filename)
    dir = navigate_to_directory(path)
    if fname in dir:
        print(f"Error: File '{filename}' already exists.")
    else:
        dir[fname] = input("Enter file content: ")
        print(f"File '{filename}' created.")

def read_file(args):
    if len(args) != 1:
        print("Usage: read <filename>")
        return
    filename = args[0]
    path, fname = os.path.split(filename)
    dir = navigate_to_directory(path)
    if fname in dir:
        print(f"Content of '{filename}':")
        print(dir[fname])
    else:
        print(f"Error: File '{filename}' not found.")

def delete_file(args):
    if len(args) != 1:
        print("Usage: delete <filename>")
        return
    filename = args[0]
    path, fname = os.path.split(filename)
    dir = navigate_to_directory(path)
    if fname in dir:
        del dir[fname]
        print(f"File '{filename}' deleted.")
    else:
        print(f"Error: File '{filename}' not found.")

def list_files(args):
    if len(args) > 1:
        print("Usage: ls [directory]")
        return
    directory = args[0] if args else ""
    dir = navigate_to_directory(directory)
    if isinstance(dir, dict):
        if dir:
            print("Files in directory:")
            for filename in dir:
                print(f" - {filename}")
        else:
            print("No files in directory.")
    else:
        print(f"Error: Directory '{directory}' not found.")

def make_directory(args):
    if len(args) != 1:
        print("Usage: mkdir <directory>")
        return
    directory = args[0]
    path, dirname = os.path.split(directory)
    dir = navigate_to_directory(path)
    if dirname in dir:
        print(f"Error: Directory '{directory}' already exists.")
    else:
        dir[dirname] = {}
        print(f"Directory '{directory}' created.")

def remove_directory(args):
    if len(args) != 1:
        print("Usage: rmdir <directory>")
        return
    directory = args[0]
    path, dirname = os.path.split(directory)
    dir = navigate_to_directory(path)
    if dirname in dir and isinstance(dir[dirname], dict):
        del dir[dirname]
        print(f"Directory '{directory}' deleted.")
    else:
        print(f"Error: Directory '{directory}' not found or not a directory.")

def change_directory(args):
    global current_working_directory
    if len(args) != 1:
        print("Usage: cd <directory>")
        return
    directory = args[0]
    if directory == "..":
        if len(current_working_directory) > 1:
            current_working_directory.pop()
    else:
        dir = navigate_to_directory(directory)
        if isinstance(dir, dict):
            current_working_directory.append(directory)
        else:
            print(f"Error: Directory '{directory}' not found.")

def user_add(args):
    if len(args) != 1:
        print("Usage: useradd <username>")
        return
    username = args[0]
    if username in users:
        print(f"Error: User '{username}' already exists.")
    else:
        password = input(f"Enter password for {username}: ")
        users[username] = password
        print(f"User '{username}' added.")

def user_del(args):
    if len(args) != 1:
        print("Usage: userdel <username>")
        return
    username = args[0]
    if username not in users:
        print(f"Error: User '{username}' not found.")
    else:
        del users[username]
        print(f"User '{username}' deleted.")

def list_users():
    print("Users in system:")
    for user in users:
        print(f" - {user}")

def change_password(args):
    if len(args) != 1:
        print("Usage: passwd <username>")
        return
    username = args[0]
    if username not in users:
        print(f"Error: User '{username}' not found.")
    else:
        password = input(f"Enter new password for {username}: ")
        users[username] = password
        print(f"Password for user '{username}' changed.")

def run_process(args):
    if len(args) != 1:
        print("Usage: run <process_name>")
        return
    process_name = args[0]
    pid = uuid.uuid4()
    processes.append({"pid": pid, "name": process_name, "status": "running"})
    print(f"Process '{process_name}' started with PID {pid}.")

def list_processes():
    if processes:
        print("Running processes:")
        for process in processes:
            print(f" - PID: {process['pid']} | Name: {process['name']} | Status: {process['status']}")
    else:
        print("No running processes.")

def kill_process(args):
    if len(args) != 1:
        print("Usage: kill <pid>")
        return
    pid = args[0]
    for process in processes:
        if str(process['pid']) == pid:
            process['status'] = 'terminated'
            print(f"Process with PID {pid} terminated.")
            return
    print(f"Error: Process with PID {pid} not found.")

def download_file(args):
    if len(args) != 2:
        print("Usage: download <url> <filename>")
        return
    url = args[0]
    filename = args[1]
    response = requests.get(url)
    if response.status_code == 200:
        path, fname = os.path.split(filename)
        dir = navigate_to_directory(path)
        dir[fname] = response.content.decode('utf-8')
        print(f"File '{filename}' downloaded.")
    else:
        print(f"Error: Failed to download '{url}'. HTTP status code: {response.status_code}")

def fetch_web_content(args):
    if len(args) != 1:
        print("Usage: fetch <url>")
        return
    url = args[0]
    response = requests.get(url)
    if response.status_code == 200:
        print(response.text)
    else:
        print(f"Error: Failed to fetch '{url}'. HTTP status code: {response.status_code}")

def chat_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((CHAT_HOST, CHAT_PORT))
    
    username = input("Enter your chat username: ")
    client_socket.send(username.encode())
    
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
    
    while True:
        message = input()
        if message.lower() == 'exit':
            client_socket.close()
            break
        client_socket.send(message.encode())

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print(message)
            else:
                print("You have been disconnected from the chat server.")
                client_socket.close()
                break
        except:
            print("You have been disconnected from the chat server.")
            client_socket.close()
            break

def start_chat_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((CHAT_HOST, CHAT_PORT))
    server.listen()
    print(f"Chat server is listening on {CHAT_HOST}:{CHAT_PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    conn.send("Enter your chat username: ".encode())
    username = conn.recv(1024).decode()
    usernames[conn] = username
    clients.append(conn)
    
    broadcast(f"{username} has joined the chat.", conn)
    
    while True:
        try:
            message = conn.recv(1024).decode()
            if not message:
                break
            broadcast(f"{username}: {message}", conn)
        except:
            break
    
    conn.close()
    clients.remove(conn)
    broadcast(f"{username} has left the chat.", conn)
    del usernames[conn]

def broadcast(message, connection):
    for client in clients:
        if client != connection:
            try:
                client.send(message.encode())
            except:
                client.close()
                clients.remove(client)

def navigate_to_directory(path):
    global current_working_directory
    dir = file_system
    for part in current_working_directory:
        dir = dir.get(part, {})
    for part in path.split("/"):
        if part:
            dir = dir.get(part, {})
    return dir

def show_help():
    print("Available commands:")
    print(" - create <filename>: Create a new file")
    print(" - read <filename>: Read a file's content")
    print(" - delete <filename>: Delete a file")
    print(" - ls [directory]: List files in a directory")
    print(" - mkdir <directory>: Create a new directory")
    print(" - rmdir <directory>: Remove a directory")
    print(" - cd <directory>: Change the current working directory")
    print(" - useradd <username>: Add a new user")
    print(" - userdel <username>: Delete a user")
    print(" - users: List all users")
    print(" - passwd <username>: Change user password")
    print(" - run <process_name>: Run a new process")
    print(" - ps: List running processes")
    print(" - kill <pid>: Kill a process")
    print(" - download <url> <filename>: Download a file from the internet")
    print(" - fetch <url>: Fetch web content")
    print(" - chat: Start the chat client")
    print(" - help: Show this help message")

if __name__ == "__main__":
    boot()
