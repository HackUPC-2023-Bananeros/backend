from datetime import datetime, timedelta
import socket
from enum import Enum
import json
import threading
import random
import cluster
from collections import deque


class Type(Enum):
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

unico_juego1 = ('localhost', 7000)
unico_juego2 = ('localhost', 7005)
game_categories={}
game_categories['four_player'] = [Games.HOT_WAY, Games.AIR_BALLONS, Games.SHEEP_PUSHERS, Games.SEA_BATTLE]
game_categories['two_player'] = [Games.TIE_SHAPING, Games.SEA_BATTLE]
game_categories['single_player'] = [Games.ROPE_CLIMBERS, Games.PAPERPLANES, Games.CATCH_THE_BALL, Games.OBSTACLES]
game_categories['beach'] = [Games.SEA_BOMBS, Games.SEA_BATTLE]
game_categories['mountain'] = [Games.SHEEP_PUSHERS, Games.ROPE_CLIMBERS]
game_categories['snow'] = [Games.HOT_WAY]
cities = ["Berlín", "Düsseldorf", "Fráncfort", "Hamburgo", "Hanóver", "Múnich", "Nuremberg", "Stuttgart", "Argel", "Viena", "Bruselas", "Sal", "Lárnaca", "Dubrovnik", "Split", "Zagreb", "Billund", "Copenhague", "El Cairo", "A Coruña", "Alicante", "Almería", "Asturias", "Barcelona", "Bilbao", "Fuerteventura", "Gran Canaria", "Granada", "Ibiza", "Jerez", "La Palma", "Lanzarote", "Logroño", "Madrid", "Málaga", "Mallorca", "Menorca", "Pamplona", "Reus", "San Sebastián", "Santander", "Santiago", "Sevilla", "Tenerife", "Valencia", "Valladolid", "Vigo", "Zaragoza", "Bastia", "Burdeos", "Lyon", "Marsella", "Nantes", "Niza", "París", "Toulouse", "Banjul", "Atenas", "Corfú", "Creta", "Mikonos", "Santorini", "Zante", "Budapest", "Cork", "Dublín", "Shannon", "Reikiavik", "Tel Aviv", "Alguer", "Bari", "Bolonia", "Cagliari", "Catania", "Florencia", "Génova", "Lampedusa", "Milán", "Nápoles", "Olbia", "Palermo", "Roma", "Turín", "Venecia", "Amán", "Beirut", "Malta", "Agadir", "Casablanca", "Marrakech", "Tánger", "Bergen", "Oslo", "Ámsterdam", "Faro", "Lisboa", "Madeira", "Oporto", "Ponta Delgada", "Birmingham", "Cardiff", "Edimburgo", "Londres", "Manchester", "Praga", "Dakar", "Estocolmo", "Gotemburgo", "Basilea", "Ginebra", "Zúrich", "Túnez"]
city_categories = {}
city_categories['beach'] = cities[:12]
city_categories['mountain'] = cities[12:24]
city_categories['snow'] = cities[24:]
groups = {}

def get_biome_by_city(city):
    if city in city_categories['beach']:
        return 'beach'
    if city in city_categories['mountain']:
        return 'mountain'
    if city in city_categories['snow']:
        return 'snow'

def match_biome(game):
    destination_biome = get_biome_by_city(destination)
    for biome in city_categories:
        if biome == destination_biome:
            if game in game_categories[biome]:
                return True
        else:
            if game in game_categories[biome]:
                return False
    return True
route = random.sample(cities, 5)
destination = route[-1]

playing_progress = {}
playing = {}
pending = {}


now = datetime.now().timestamp() * 1000
start_time = now + 1*60*1000

def get_remaining_time():
    now = datetime.now().timestamp() * 1000
    return start_time - now

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def find_group(seat):
    for group in groups:
        if seat in groups[group]:
            return group

def send_start_game(seat):
    group = find_group(seat)
    game = playing_progress[seat].pop()
    game = Games.SEA_BOMBS
    if game == Games.SEA_BOMBS:
            message = json.dumps({'game':str(Games.SEA_BOMBS.value), 'direction':str(groups[group].index(seat))})
            sock.sendto(message.encode(), pending[seat])


def open_socket():
    # Bind the socket to a specific IP address and port
    server_address = ('172.200.200.1', 7001)
    sock.bind(server_address)

def wait_recv():
    global pening, playing, playing_progress
    while True:
        # Wait for incoming data
        data, address = sock.recvfrom(4096)
        data = json.loads(data.decode())
        if data['type'] == Type.CONNECT.value:
            print(f"Recieved connection from seat {data['seat']}, Registerd player in queue for next game")
            pending[data['seat']] = address
            print(list(pending.keys()))
            message = json.dumps({'time':str(get_remaining_time())})
            sock.sendto(message.encode(), address)
            print(f"Sent remaining time to seat {data['seat']}")
        elif data['type'] == Type.MINIGAME_ENDED.value:
            print(f"{data['players']} ended their previous minigame, looking for the next one")
            #group = find_group(data['players'][0])
            if len(playing_progress[data['players'][0]])>0:
                for player in data['players']:
                    message = json.dumps({'type':Type.FINISHED_PLAYING.value})
                    sock.sendto(message.encode(), playing[data['player']])
                    print(f"seat {data['player']} has finished all minigames, sending FINISHED_PLAYING type")
                    playing.pop(data['player'])           
            else:
                for player in data['players']:
                    game = playing_progress[data['player']].pop()
                    message = json.dumps({'game':str(game)})
                    sock.sendto(message.encode(), playing[data['player']])
                    print(f"Next minigame for {data['player']} is {game}. Entering minigame")
                message = json.dumps({'type':Type.CREATE.value, 'players':data['players']})
                sock.sendto(message.encode(), unico_juego2)
                

def countdown():
    global pending, playing, groups
    while True:
        while(get_remaining_time() > 0 or len(playing) > 0 or len(pending) == 0):
            pass
        now = datetime.now().timestamp() * 1000
        start_time = now + 2*60*1000
        games_list = list(random.sample(game_categories['four_player'], len(game_categories['four_player']))) + list(random.sample(game_categories['two_player'], len(game_categories['two_player']))) + list(random.sample(game_categories['single_player'], len(game_categories['single_player'])))
        games_list = list(filter(match_biome, games_list))
        games_list = games_list[:len(route)]
        print(list(pending.keys()))
        player_group, groups = cluster.cluster(list(pending.keys()))
        for group in groups:
            for player in groups[group]:
                playing_progress[player] = deque(games_list)
                send_start_game(player)

        playing = pending.copy()
        pending = {}
        for group in groups:
            message = json.dumps({'type':Type.CREATE.value, 'players':groups[group]})
            sock.sendto(message.encode(), unico_juego1)

def main():
    open_socket()

    p = threading.Thread(target=countdown)
    p.start()
    wait_recv()
    p.join()

if __name__ == '__main__':
    main()