#!/usr/bin/python3
import struct
from customException import InterruptedConnection

bufferSize = 5


# Function to recursively send data with socket.send until all the data was sent
def my_sendall(sock, data):
    if len(data) == 0:
        return None
    ret = sock.send(data)
    return my_sendall(sock, data[ret:])


# Pack the data and send it with our custom my_sendall function described above
def pack_send(sock, c, n):
    data = struct.pack(">ci", c.encode(), n)
    return my_sendall(sock, data)


# Function to receive data using socket.recv until all the data was received
def my_recvall(sock):
    data = bytes()
    while len(data) < bufferSize:
        chunk = sock.recv(bufferSize - len(data))
        if not chunk:
            return None
        data += chunk
    return data


# Receive data using the custom my_recvall  function described above and unpack it
def recv_unpack(sock):
    rawData = my_recvall(sock)
    if not rawData:
        raise InterruptedConnection
    unpacked = struct.unpack(">ci", rawData)
    return unpacked[0].decode(), unpacked[1]
