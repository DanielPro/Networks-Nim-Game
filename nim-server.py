#!/usr/bin/python3
from socket import *
from functions import *
import errno
import sys

portNum = 6444
heapsDict = {}

if len(sys.argv) < 4:
    sys.exit("Too few arguments. Try again.")

heapsDict['A'] = n_a = int(sys.argv[1])
heapsDict['B'] = n_b = int(sys.argv[2])
heapsDict['C'] = n_c = int(sys.argv[3])

if len(sys.argv) > 4:
    portNum = int(sys.argv[4])

try:
    listeningSocket = socket(AF_INET, SOCK_STREAM)
    listeningSocket.bind(('', portNum))
    listeningSocket.listen(1)
except OSError as error:
    print(error.strerror)
    listeningSocket.close()
    sys.exit()
except (KeyboardInterrupt, EOFError):
    listeningSocket.close()
    sys.exit()


# Check if game isn't finished yet (Some heap still has dice in it)
def unfinished(heaps):
    if heaps['A'] > 0 or heaps['B'] > 0 or heaps['C'] > 0:
        return True
    else:
        return False


# Make a move.
# Remove 1 from the heap which has the max amount of dice.
def serverTurn(heaps):
    maximum = max(heaps, key=heaps.get)
    heaps[maximum] = heaps.get(maximum) - 1


# wrapper function to try to send data to the client.
# Catches OSErrors,
# and Keyboard, EOFError, meaning someone force quit the server.
def msg(sock, c, n):
    try:
        pack_send(sock, c, n)
        return
    except OSError as error:
        if error.errno == (errno.EPIPE or errno.ECONNRESET):
            print("Connection was closed by client")
        else:
            print(error.strerror)
        return 1
    except (KeyboardInterrupt, EOFError):
        return 1


# Send all the heaps data to the client
def msg_heap_status(sock):
    for key in heapsDict.keys():
        if msg(sock, key, heapsDict.get(key)) == 1:
            return 1


# Accept a new connection, and play the game until someone wins
# or the client disconnects. When the game ends for some reason as described here,
# restart the heap sizes and close the connection socket, allowing a new client to connect.
while True:
    try:
        (connectionSocket, address) = listeningSocket.accept()
    except OSError as error:
        print(error.strerror)
        sys.exit()
    except (KeyboardInterrupt, EOFError):
        listeningSocket.close()
        sys.exit()

    while True:

        if msg_heap_status(connectionSocket) == 1:
            break
        if msg(connectionSocket, 'W', 0) == 1:  # Game continues
            break

        try:
            move = recv_unpack(connectionSocket)
        except OSError as error:
            if error.errno == (errno.EPIPE or errno.ECONNRESET):
                print("Connection was closed by client")
            else:
                print(error.strerror)
            break
        except InterruptedConnection:
            print("Client disconnected")
            break
        except (KeyboardInterrupt, EOFError, IOError):
            connectionSocket.close()
            listeningSocket.close()
            sys.exit()

        if move[0] == 'Q':
            break

        if 0 < move[1] <= heapsDict.get(move[0]):  # Move accepted
            heapsDict[move[0]] = heapsDict.get(move[0]) - move[1]
            if msg(connectionSocket, 'M', 1) == 1:
                break

        else:  # Illegal move - code 1001
            if msg(connectionSocket, 'M', 0) == 1:
                break

        if unfinished(heapsDict):
            serverTurn(heapsDict)

        else:  # Client wins
            msg_heap_status(connectionSocket)
            msg(connectionSocket, 'W', 1)
            break

        if not unfinished(heapsDict):  # Server wins
            msg_heap_status(connectionSocket)
            msg(connectionSocket, 'W', 2)
            break

    # Restart parameters
    heapsDict['A'] = n_a
    heapsDict['B'] = n_b
    heapsDict['C'] = n_c

    connectionSocket.close()
