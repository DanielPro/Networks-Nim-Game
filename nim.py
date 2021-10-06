#!/usr/bin/python3
from socket import *

from clientGameLogic import *

isConnected = False
clientSocket = None

serverHostname = 'localhost'    # Default host to connect to
serverPort = 6444               # Default port number of host

if len(sys.argv) >= 2:
    serverHostname = sys.argv[1]

if len(sys.argv) == 3:
    serverPort = int(sys.argv[2])

try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverHostname, serverPort))
    isConnected = True
except OSError as error:
    if error.errno == errno.ECONNREFUSED:
        print("Connection refused by server")
    else:
        print(error.strerror)
except (KeyboardInterrupt, EOFError):
    pass

if isConnected:
    playGame(clientSocket)

clientSocket.close()
