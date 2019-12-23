from utils import read_data
from advent2019_day23_intcode import run_tape_multithreaded, Packet
from multiprocessing import Queue, Process
from queue import Empty
from typing import NamedTuple, List
import time

def part_one(data, num_entities=50):
    network_inputs: List[Queue] = []
    processes: List[Process] = []
    output_queue = Queue()

    for i in range(num_entities):
        print(f"Starting process {i}/{num_entities}")
        network_inputs.append(Queue())
        new_process = Process(target=run_tape_multithreaded, args=(data, i, network_inputs[i], output_queue, 3))
        processes.append(new_process)
        new_process.start()

    while True:
        packet = output_queue.get(block=True)
        # print(f"Processing packet {packet}")
        if packet.dest == 255:
            [x.kill() for x in processes]
            return packet.y
        network_inputs[packet.dest].put((packet.x, packet.y))


def part_two(data, num_entities=50):
    network_inputs: List[Queue] = []
    processes: List[Process] = []
    output_queue = Queue()
    nat_buffer = None
    previous_sent_nat_packet = None

    for i in range(num_entities):
        print(f"Starting process {i}/{num_entities}")
        network_inputs.append(Queue())
        new_process = Process(target=run_tape_multithreaded, args=(data, i, network_inputs[i], output_queue, 3))
        processes.append(new_process)
        new_process.start()

    while True:
        try:
            # Give the workers time to starve before checking input queues
            packet = output_queue.get(block=True, timeout=0.3)
        except Empty:
            if all(x.empty() for x in network_inputs):
                if previous_sent_nat_packet is not None and previous_sent_nat_packet == nat_buffer:
                    [x.kill() for x in processes]
                    return nat_buffer
                network_inputs[0].put((nat_buffer.x, nat_buffer.y))
                previous_sent_nat_packet = nat_buffer
                continue
        # print(f"Processing packet {packet}")
        if packet.dest == 255:
            nat_buffer = packet
        else:
            network_inputs[packet.dest].put((packet.x, packet.y))


if __name__ == '__main__':
    DATA = [int(x) for x in read_data().split(",")]
    print(f"Y of first packet to 255 is {part_one(DATA)}")
    first_twice = part_two(DATA)
    print(f"Y of first packet to be sent twice is {first_twice}")
