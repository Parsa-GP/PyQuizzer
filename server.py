# shoutout to https://stackoverflow.com/questions/33434007/python-socket-send-receive-messages-at-the-same-time!
#from pandas import DataFrame
from base64 import b64decode,b64encode
from json import dumps,loads
from os import system
from sys import exit
from dbman import *

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

try:
    from tabulate import tabulate
except ImportError:
    system("pip install tabulate")
    from tabulate import tabulate

test=True

quiz_data = {
    "Advanced Python": {
        "Final Quiz": [
            {
                "name": "question 1 (Straight question and answer)",
                "type": "qa",
                "data": {
                    "question": "what is 1+1?",
                    "answers": ["2", "5-3"]
                }
            },

            {
                "name": "question 2 (4 answer)",
                "type": "4an",
                "data": {
                    "question": "what is 1+1?",
                    "answers": ["1", "2", "3", "4"],
                    "answer": 1 #index of item in answers
                }
            },

            {
                "name": "question 3 (multiselect)",
                "type": "multi",
                "data": {
                    "question": "select odd numbers.",
                    "answers": ["1", "2", "3", "4", "5", "6"],
                    "answer": [0,2,4] #index of items in answers
                }
            },

            {
                "name": "question 4 (gimme code)",
                "type": "code",
                "data": {
                    "question": "how to 1+1 in python?\nSet \"number\" variable to 1+1",
                    "answers": ["number=1+1", "number=1;number+=1"]
                }
            },

            {
                "name": "question 5 (yes no)",
                "type": "yn",
                "data": {
                    "question": "are you a human?",
                    "answer": True
                }
            }
        ]
    },
    "Beginner Py": {
        "Starter Quiz": [
            {
                "name": "iq test",
                "type": "yn",
                "data": {
                    "question": "yes?",
                    "answer": True
                }
            }
        ],
        "Final Quiz": [
            {
                "name": "input test",
                "type": "yn",
                "data": {
                    "question": "if i write number in input(), the function is going to convert it to intger?",
                    "answer": False
                }
            }
        ]
    }
}

def cls():
    system("cls")

def print_log(*text, priority=0):
    if test:
        if priority==0: prefix=  f"[{color.BOLD}{color.CYAN}INFO{color.RESET}]{color.CYAN}"
        elif priority==1: prefix=f"[{color.BOLD}{color.YELLOW}WARN{color.RESET}]{color.YELLOW}"
        elif priority==2: prefix=f"[{color.BOLD}{color.PURPLE}CRIT{color.RESET}]{color.PURPLE}"
        elif priority==3: prefix=f"[{color.BOLD}{color.RED}EROR{color.RESET}]{color.RED}"
        else: prefix=""

        print(prefix, " ".join(text), color.RESET)

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
                data = client_socket.recv(16384)
            except ConnectionResetError:
                print_log("A User disconnected!")
            if not data:
                break
            rdata = data.decode().split(":")
            print_log("Received:", ":".join(rdata))
            if rdata[0] == "iwantquiz":
                username = rdata[1]
                db = SQLiteManager("users");db.connect()
                userdata = db.get_record_from_table("users", f"username = '{username}'")
                if userdata is None:
                    response = "invalidun:" + username
                    client_socket.send(response.encode())
                    print_log(f"Invalid Username for {username} Sent!")
                    continue

                print(f"hey, {userdata[2]} wants a quiz, what quiz should i send?")
                class_data = quiz_data[userdata[3]]
                db.close_connection()
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
            elif rdata[0] == "answers":
                print_log(f"Got Answers from {rdata[1]}")
                # do grade stuff
                grade = -1 # because if grade eqals to -1, then client won't print the grade!
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

if test:
    start_server(int(12345))
else:
    #start = input("Start Server [Y,n]? ")
    #if start.lower()=="n":
    #    pass
    #elif start=="" or start.lower()=="y":
    port = input("which port [12345]? ")
    if not bool(port): port=12345
    start_server(int(port))
    exit()
