from utils import read_data
import numpy as np


# from https://stackoverflow.com/a/434328
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def get_pixel(y, x, layers):
    for layer in layers:
        if layer[y, x] != 2:
            return layer[y,x]
    raise Exception("Transparent all the way down!")


def make_layers(incoming_data):
    chunked_data = list(chunker(DATA, pixels_per_layer))

    layers = []
    for rawlayer in chunked_data:
        layers.append(np.array(rawlayer).reshape((size_y, size_x)))
    return layers


def part_one(layers):
    min_zeroes = 99999
    least_zero_layer = None
    for i, layer in enumerate(layers):
        if (layer_zeroes := np.count_nonzero(layer == 0)) < min_zeroes:
            min_zeroes = layer_zeroes
            least_zero_layer = i

    return np.count_nonzero(layers[least_zero_layer] == 1) * np.count_nonzero(layers[least_zero_layer] == 2)


def part_two(layers):
    final_image = np.zeros([size_y, size_x], dtype=np.int)

    for y in range(size_y):
        for x in range(size_x):
            final_image[y, x] = get_pixel(y, x, layers)
    return final_image


size_x = 25
size_y = 6

pixels_per_layer = size_x * size_y

DATA = [int(x) for x in read_data()]

layers = make_layers(DATA)

print(f"part one answer is {part_one(layers)}")

with np.printoptions(linewidth=200, formatter={'int': lambda x: "X" if x == 1 else " "}):
    print(part_two(layers))

