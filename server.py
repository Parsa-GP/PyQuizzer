# BIG Shout-out to https://stackoverflow.com/questions/33434007/
from base64 import b64decode,b64encode
from json import dumps,loads,load
from os import system,path
from sys import exit
from dbman import *

# Got from https://stackoverflow.com/questions/287871/
class color:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def cls():
    system("cls")

def print_log(*text, priority=0):
    if config["debug"]:
        if priority==0: prefix=  f"[{color.BOLD}{color.CYAN}INFO{color.RESET}]{color.CYAN}"
        elif priority==1: prefix=f"[{color.BOLD}{color.YELLOW}WARN{color.RESET}]{color.YELLOW}"
        elif priority==2: prefix=f"[{color.BOLD}{color.PURPLE}CRIT{color.RESET}]{color.PURPLE}"
        elif priority==3: prefix=f"[{color.BOLD}{color.RED}EROR{color.RESET}]{color.RED}"
        else: prefix=""

        print(prefix, " ".join(text), color.RESET)

# Checking if Tabulate is installed, If not, install it using pip
try:
    from tabulate import tabulate
except ImportError:
    pri
    system("pip install tabulate")
    from tabulate import tabulate

# Getting Quiz Data from File
if not path.isfile("quiz_data.json"):
    print_log("The Quiz Data file Does not Exists. Please make a Quiz Data file", priority=3)
    exit()
with open("quiz_data.json") as f:
    quiz_data = load(f)

# Create a Default Config file
config = {
    "max_incomingdata": 16,
    "do_grade_calculation": False,
    "debug": True,
    "port": 6363,
}

def start_server(port):
    global quiz_data
    import socket,threading,signal
    stop_event = threading.Event()

    def exit_gracefully(signal, frame):
        print("Ctrl+C detected. Stopping all threads...")
        stop_event.set()
        exit()

    def handle_client(client_socket):
        global quiz_data
        while True:
            try:
                data = client_socket.recv(int(config["max_incomingdata"])*1024)
                # Maximum incoming data in KB
            except ConnectionResetError:
                print_log("A User disconnected!")
            if not data:
                break
            rdata = data.decode().split(":")
            print_log("Received:", ":".join(rdata))

            # If the user send a quiz request
            if rdata[0] == "iwantquiz":
                username = rdata[1]
                db = SQLiteManager("users")
                db.connect()
                userdata = db.get_record_from_table("users", f"username = '{username}'")
                db.close_connection()

                if userdata is None:
                    response = "invalidun:" + username
                    client_socket.send(response.encode())
                    print_log(f"Invalid Username for {username} Sent!")
                    continue
                class_data = quiz_data[userdata[3]]

                if len(class_data) == 1:
                    quizname = list(class_data.keys())[0]
                else:
                    print(f"Hey, {userdata[2]} wants to take quiz, what quiz should i send?")
                    table_data = [{'Name': name, 'Questions': question} for name, question in \
                        zip(list(class_data.keys()), [len(class_data[a]) \
                        for a in class_data.keys()])]
                    print(tabulate(table_data, headers='keys', tablefmt='presto'))
                    while True:
                        try:
                            quizname = list(class_data.keys())[int(input("QuizIndex:> "))]
                            break
                        except IndexError: pass
                response = "quiz: " + \
                           b64encode(dumps(class_data[quizname]).encode()).decode("utf-8")

                try:
                    client_socket.send(response.encode())
                except ConnectionResetError:
                    print_log("An connection was forcibly closed", priority=3)

                print_log(f"Quiz Sent for {userdata[2]}!")

            # If user wants to send the answers
            elif rdata[0] == "answers":
                print_log(f"Got Answers from {rdata[1]}")

                if config["do_grade_calculation"]:
                    # do grade stuff
                    pass
                else:
                    grade = -1 # if grade == -1, then client won't print the grade!

                print_log(f"Grade for {rdata[1]} is {grade}!")
                response = "grade:" + b64encode(str(grade).encode()).decode("utf-8")

                try:
                    client_socket.send(response.encode())
                except ConnectionResetError:
                    print_log("An connection was forcibly closed", priority=3)
                print_log("Grade Sent!")
        client_socket.close()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen(5)
    print(f"listening on port {port}")
    signal.signal(signal.SIGINT, exit_gracefully)

    while True:
        client_socket, client_address = server_socket.accept()
        print_log("Accepted connection from:", str(client_address))
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        try:
            client_handler.start()
            client_handler.join()
        except Exception as e:
            exit(e)

if config["debug"]:
    start_server(int(config["port"]))
else:
    port = input(f"which port [{config['port']}]? ")
    if not bool(port): port=int(config["port"])
    start_server(int(port))
    exit()
