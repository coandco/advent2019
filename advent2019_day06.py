from utils import read_data
from collections import defaultdict


def generate_reverse_map(data):
    forward_map = defaultdict(list)
    reverse_map = {'COM': None}
    for line in data:
        orbitee, orbiter = line.split(')', 1)
        reverse_map[orbiter] = orbitee
    return reverse_map


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
    # Subtract one from each leg because we start on a planet and don't need to travel there
    leg_one_length = obj_one_pedigree.index(common_ancestor)-1
    leg_two_length = obj_two_pedigree.index(common_ancestor)-1
    return leg_one_length + leg_two_length


DATA = read_data().split("\n")

reverse = generate_reverse_map(DATA)

print(f'checksum is {sum(len(get_pedigree(reverse, x))-1 for x in reverse)}')

print(f'path length is {get_path_length(reverse, "YOU", "SAN")}')
