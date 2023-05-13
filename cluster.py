from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
import numpy as np


def getCoord(seat: str):
  column = (ord(seat[0]) -65) if seat[0] < 'D' else (ord(seat[0]) -64.5)
  row = (int(seat[1:]) -1)  * 1.1
  return (column,row)


def generate_positions(size):
  import random
  letters = 'ABCDEF'
  players = []
  for i in range(size):
    seat = random.choice(letters)+str(random.randint(1,52))
    players.append(seat)
  return players


def get_even_clusters(X, cluster_size):
    n_init = 10
    n_clusters = int(np.ceil(len(X)/cluster_size))
    kmeans = KMeans(n_clusters, n_init=10)
    kmeans.fit(X)
    centers = kmeans.cluster_centers_
    centers = centers.reshape(-1, 1, X.shape[-1]).repeat(cluster_size, 1).reshape(-1, X.shape[-1])
    distance_matrix = cdist(X, centers)
    clusters = linear_sum_assignment(distance_matrix)[1]//cluster_size
    return clusters


def cluster(seats: list):
    player_group = {}
    groups_dict = {}
    players = np.array(list(map(getCoord, seats)))
    groups = get_even_clusters(players, 4)
    for player, group in zip(seats, groups):
      player_group[player] = group
    for player in player_group:
      if player_group[player] not in groups_dict:
        groups_dict[player_group[player]] = []
      groups_dict[player_group[player]].append(player)
    return player_group, groups_dict
