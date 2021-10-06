#!/usr/bin/python3
import errno
import sys

from customException import InterruptedConnection
from functions import recv_unpack
from functions import pack_send


# A wrapper method to try to receive data to the server.
# Catches OSErrors,
# custom interrupt error, indicating message was wasn't received
# and Keyboard, EOFError, meaning player force quit the game.
def tryToRecv(socket):
    try:
        return recv_unpack(socket)
    except OSError as error:
        if error.errno == errno.ECONNREFUSED:
            print("Disconnected from server")
        else:
            print(error.strerror)
    except InterruptedConnection:
        print("Disconnected from server")
    except (KeyboardInterrupt, EOFError):
        pass
    socket.close()
    sys.exit()


# A wrapper method to try to send data to the server.
# Catches OSErrors,
# and Keyboard, EOFError, meaning player force quit the game.
def tryToSend(socket, c, i):
    try:
        pack_send(socket, c, i)
        return
    except OSError as error:
        if error.errno == errno.EPIPE or errno.ECONNRESET:
            print("Disconnected from server")
        else:
            print(error.strerror)
    except (KeyboardInterrupt, EOFError):
        pass
    socket.close()
    sys.exit()


# Get three messages from the server,
# each message containing a heaps name, and the amount of dices inside.
# Print those values to the player accordingly.
def getHeapFromServer(socket):
    for i in range(3):
        heap = tryToRecv(socket)
        print(f"Heap {heap[0]}: {heap[1]}")


# Receive a message from server whether the game was over.
# 'W0' means game isn't over
# 'W1' means player won
# 'W2' means server won
def isGameOver(socket):
    return tryToRecv(socket)[1]


# Ask the player to input his next move.
# Possible moves are 'Q' to quit the game,
# or 'A/B/C' followed by a number.
# Whether the number is legal, is checked by the server, not here.
def makeMove(socket):
    try:
        userInput = input()
    except (KeyboardInterrupt, EOFError):
        socket.close()
        sys.exit()
    if userInput == 'Q':
        tryToSend(socket, 'Q', 0)
    parsed = userInput.split(" ")
    if len(parsed) == 2:
        if parsed[0] == 'A' or parsed[0] == 'B' or parsed[0] == 'C':
            if parsed[1].isnumeric():
                tryToSend(socket, parsed[0], int(parsed[1]))
                return
    pack_send(socket, 'A', 1001)


# Receive a message from the server whether the move made by the player was legal or not,
# and print a corresponding message to the player.
def isMoveLegal(socket):
    moveCheck = tryToRecv(socket)
    if moveCheck[1] == 0:
        print("Illegal move")
    elif moveCheck[1] == 1:
        print("Move accepted")


# Play game until someone wins or disconnects.
# First, get all the heap sizes from server and print them.
# Second, check if someone won.
# If no one won yet, ask player to make a move,
# send the move to the server, and get a response whether the move was legal.
def playGame(socket):
    while True:
        getHeapFromServer(socket)
        winner = isGameOver(socket)
        if winner == 1:
            print("You win!")
            return
        elif winner == 2:
            print("Server win!")
            return
        else:
            print("Your turn:")
            makeMove(socket)
        isMoveLegal(socket)
