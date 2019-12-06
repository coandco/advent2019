from utils import read_data
from collections import defaultdict


def generate_maps(data):
    forward_map = defaultdict(list)
    reverse_map = {'COM': None}
    for line in data:
        orbitee, orbiter = line.split(')', 1)
        forward_map[orbitee].append(orbiter)
        reverse_map[orbiter] = orbitee
    return forward_map, reverse_map


def get_pedigree(reverse_map, object_name):
    pedigree = [object_name]
    while reverse_map[object_name] is not None:
        pedigree.append(reverse_map[object_name])
        object_name = reverse_map[object_name]
    return pedigree


def find_common_ancestor(obj_one_pedigree, obj_two_pedigree):
    for obj in obj_one_pedigree:
        if obj in obj_two_pedigree:
            return obj


def get_path_length(reverse_map, obj_one, obj_two):
    obj_one_pedigree = get_pedigree(reverse_map, obj_one)
    obj_two_pedigree = get_pedigree(reverse_map, obj_two)
    common_ancestor = find_common_ancestor(obj_one_pedigree, obj_two_pedigree)
    leg_one_length = obj_one_pedigree.index(common_ancestor)
    leg_two_length = obj_two_pedigree.index(common_ancestor)
    # Subtract one from each leg because we start on a planet and don't need to travel there
    return leg_one_length-1 + leg_two_length-1


DATA = read_data().split("\n")

forward, reverse = generate_maps(DATA)

print(f'checksum is {sum(len(get_pedigree(reverse, x))-1 for x in reverse)}')

print(f'path length is {get_path_length(reverse, "YOU", "SAN")}')
