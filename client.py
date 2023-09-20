# Imports
from socket import socket#################
from socket import AF_INET,SOCK_STREAM##
from base64 import b64decode,b64encode
from gzip import compress,decompress
from threading import Event,Thread
from signal import signal,SIGINT
from os import system,remove##
from json import dumps,loads
from socket import timeout
from time import sleep##
from sys import exit##

# Config
DEBUG = False
username = ""

# Default Variables
global_crash = \
isAnswerSent = \
isQuizReceived = \
isQuizAnswered = \
isGradeReceived = False
quiz = answers = []
grade = 0

# colored text class
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

    @staticmethod
    def reset():
        print(color.RESET, end="")

# Functions
def take_quiz(quiz_data):
    answers = []
    for i in quiz_data:
        system("cls")
        print(color.GREEN+"="*55 + f"\n= {color.CYAN}{i['name']: <50}{color.GREEN} ==\n" + "="*55 + "\n"+color.RESET)
        qdata = i["data"]
        print(qdata["question"])
        if i["type"] == "qa":
            ans = input(color.YELLOW+"Answer: "+color.RESET)
            color.reset()
            answers.append(ans)
        elif i["type"] == "4an":
            while True:
                #print("\n".join([f"[{ind}] "+str(item) for ind,item in enumerate(qdata["answers"])]))
                print(f" {color.GREEN}[1] {color.CYAN}{qdata['answers'][0]} {color.RESET}| {color.GREEN}[2] {color.CYAN}{qdata['answers'][1]}\n {color.GREEN}[3] {color.CYAN}{qdata['answers'][2]} {color.RESET}| {color.GREEN}[4] {color.CYAN}{qdata['answers'][3]} ")
                ans = int(input(color.YELLOW+"Answer (Choose index of answer): "+color.RESET))
                if not ans<5 and ans>0: continue
                answers.append(int(ans))
                break
        elif i["type"] == "multi":
            print("\n".join([f"{color.GREEN}[{ind}] {color.CYAN}"+str(item) for ind,item in enumerate(qdata['answers'])]))
            ans = input(color.YELLOW+"Answer (Choose indexes of answers): ")
            answers.append(ans)
        elif i["type"] == "code":
            with open("answer", "w") as f: f.write("Type the answer HERE!\n")
            system("notepad answer")
            #input("~ Press Enter if you done writing ")
            with open("answer", "r") as f: ans = f.read()
            remove("answer")
            answers.append(ans)
        if i["type"] == "yn":
            while True:
                ans = input(color.YELLOW+"Answer [yes,no/true,false]: ").strip()
                if ans.lower()=="yes" or ans.lower()=="true":
                    ans = "+"
                    break
                elif ans.lower()=="no" or ans.lower()=="false":
                    ans = "-"
                    break
            answers.append(ans)
    return answers
def print_log(*text, priority=0):
    if DEBUG:
        if priority==0: prefix=  f"[{color.CYAN}INFO{color.RESET}]"
        elif priority==1: prefix=f"[{color.YELLOW}WARN{color.RESET}]"
        elif priority==2: prefix=f"[{color.PURPLE}CRIT{color.RESET}]"
        elif priority==3: prefix=f"[{color.RED}EROR{color.RESET}]"
        else: prefix=""

        print(prefix, " ".join(text))
def send_thread(client_socket):
    if DEBUG: print_log(f"(SEND) Starting Send thread...")
    global isQuizAnswered
    global isAnswerSent
    global username
    global answers
    global quiz

    print_log("(SEND) Sending iwantquiz...")

    username = input("username: ")

    message = f"iwantquiz:{username}"
    client_socket.send(message.encode())

    print_log("(SEND) iwantquiz Sent!")
    print_log("(SEND) Wait until QuizAnswered...")

    while not isQuizAnswered:
        if stop_event.is_set():
            print_log(f"Thread SEND is stopping...")
            return
        sleep(1)

    print_log("(SEND) QuizAnswered!")
    print_log("(SEND) Sending the answers...")

    message = f"answers:{username}:{answers}"
    client_socket.send(message.encode())
    isAnswerSent = True

    print_log("(SEND) answers Sent!")
    print_log(f"(SEND) Thread SEND is stopping...")
def receive_thread(client_socket):
    print_log(f"(RECV) Starting Receive thread...")
    global isQuizAnswered
    global isAnswerSent
    global answers
    global grade

    while True:
        if stop_event.is_set():
            print_log(f"(RECV) Thread RECEIVE is stopping...")
            return
        try:
            data = client_socket.recv(16384).decode()
        except (timeout, ConnectionRefusedError):
            print("Connection timed out.\nPerhaps the Server is not Running or crashed!")
            client_socket.close()
            stop_event.set()
            return
        data:list = data.split(":")
        print_log("(RECV) Received:", ":".join(data))

        if data[0] == "quiz":
            print_log("(RECV) Quiz Recieved!")
            #isQuizReceived = True
            print_log("(RECV) Take the Quizz...")
            answers = take_quiz(loads(b64decode(":".join(data[1:])).decode("utf-8")))
            print_log("(RECV) Quiz Taked!")
            isQuizAnswered = True
            print_log("(RECV) Wait until AnswerSent...")
            while not isAnswerSent:
                sleep(1)
        elif data[0] == "invalidun":
            print("Username is not valid.")
            exit()
        elif data[0] == "grade":
            grade = int(b64decode("".join(data[1]).encode()))
            if grade == -1: break
            print_log(f"(RECV) Grade = {grade}")
            print(f"Grade = {grade}!")
            break
def pack(t) -> bin:
    return compress(bytes(type(t).__name__+"#"+b64encode(str(t).encode()).decode('utf-8'), 'utf-8'))
def unpack(t:bin) -> str:
    dc = decompress(t).decode('utf-8').split("#")
    types = {
        "list": loads,
        "dict": loads,
        "int": int,
        "float": float,
        "str": str
    }
    return types[dc[0]](b64decode(dc[1]).decode('utf-8'))

# Main Code
if __name__ == "__main__":
    if DEBUG:
        host = "127.0.0.1"
        port = 12345
    else:
        host = input("IP [127.0.0.1]: ")
        port = input("PORT [12345]: ")

        if not bool(host): host="127.0.0.1"
        if not bool(port): port=12345
        else: port=int(port)

    # Flag to signal threads to stop
    stop_event = Event()

    def exit_gracefully(signal, frame):
        print_log("Ctrl+C detected. Stopping all threads...")
        stop_event.set()

    signal(SIGINT, exit_gracefully)

    # Create a socket
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.settimeout(30)
    try:
        client_socket.connect((host, port))
    except (ConnectionRefusedError):
        print("Connection Refused.\nPerhaps the Server is not Running!")
        client_socket.close()
        exit(1)

    # Create threads
    threads = [Thread(target=send_thread,    args=(client_socket,)),
               Thread(target=receive_thread, args=(client_socket,))]

    threads[0].setDaemon = True
    threads[1].setDaemon = True

    threads[0].start()
    threads[1].start()

    try:
        for thread in threads:
            thread.join()
    except Exception:
        stop_event.set()

    client_socket.close()
    print_log("All threads have stopped.")
