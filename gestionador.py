from datetime import datetime, timedelta
import socket
from enum import Enum
import json
from multiprocessing import Process
import random
import cluster

class Event(Enum):
    CONNECT = 1
    DISCONNECT = 2
    CREATE = 3

class Games(Enum):
    OBSTACLES = 0
    CATCH_THE_BALL = 1
    PAPERPLANES = 2
    ROPE_CLIMBERS = 3
    SEA_BATTLE = 4
    TIE_SHAPPING = 5
    SEA_BOMBS = 6
    SHIPS_PUSHERS = 7
    AIR_BALLONS = 8
    HOT_WAY = 9

class Direction(Enum):
    UP = 0
    DOWN = 1
    RIGHT = 2
    LEFT = 3

unico_juego = 7000

four_player_games = [Games.HOT_WAY, Games.AIR_BALLONS, Games.SHIPS_PUSHERS, Games.SEA_BATTLE]
two_player_games = [Games.TIE_SHAPPING, Games.SEA_BATTLE]
single_player_games = [Games.ROPE_CLIMBERS, Games.PAPERPLANES, Games.CATCH_THE_BALL, Games.OBSTACLES]


playing = {}
pending = {}

now = datetime.now().timestamp() * 1000
start_time = now + 2*60*1000

def get_remaining_time():
    now = datetime.now().timestamp() * 1000
    return start_time - now

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def open_socket():
    # Bind the socket to a specific IP address and port
    server_address = ('localhost', 6969)
    sock.bind(server_address)
def wait_recv():
    while True:
        # Wait for incoming data
        data, address = sock.recvfrom(4096)
        data = json.loads(data.decode())

        if data['type'] == Event.CONNECT:
            pending[data['seat']] = address
            message = json.dumps({'time':str(get_remaining_time())})
            sock.sendto(message.encode(), address)

def countdown(name):
    while(get_remaining_time > 0):
        pass
    game = random.choice(four_player_games)
    player_group, groups = cluster.cluster(pending.keys())
    for group in groups:
        for index, player in enumerate(group):
            if game == Games.SEA_BOMBS:
                message = json.dumps({'game':str(game),
                           'direction':str(index)})
            
            sock.sendto(message.encode(), pending[player])
    for group in groups:
        message = json.dumps({'event':Event.CREATE, 'players':groups[group]})
        sock.sendto(message.encode(), unico_juego)

def main():
    open_socket()

    p = Process(target=countdown)
    p.start()
    p.join()

if __name__ == '__main__':
    main()