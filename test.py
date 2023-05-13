from datetime import datetime, timedelta
import socket
from enum import Enum
import json
from multiprocessing import Process
import random
import cluster
import queue

class Event(Enum):
    CONNECT = 1
    DISCONNECT = 2
    CREATE = 3
    MINIGAME_ENDED = 4
    FINISHED_PLAYING = 5


class Games(Enum):
    OBSTACLES = 0
    CATCH_THE_BALL = 1
    PAPERPLANES = 2
    ROPE_CLIMBERS = 3
    SEA_BATTLE = 4
    TIE_SHAPING = 5
    SEA_BOMBS = 6
    SHEEP_PUSHERS = 7
    AIR_BALLONS = 8
    HOT_WAY = 9

class Direction(Enum):
    UP = 0
    DOWN = 1
    RIGHT = 2
    LEFT = 3

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 6969)

def open_socket():
    # Bind the socket to a specific IP address and port
    client_address = ('localhost', 6968)

    sock.bind(client_address)

def send():

        # Wait for incoming data

    message = json.dumps({'event':Event.CONNECT.value, 'seat':'A7'})
    sock.sendto(message.encode(), server_address)

    data, address = sock.recvfrom(4096)
    data = json.loads(data.decode())
    print(data)

    data, address = sock.recvfrom(4096)
    data = json.loads(data.decode())
    print(data)
        

def main():
    open_socket()
    send()

if __name__ == '__main__':
    main()