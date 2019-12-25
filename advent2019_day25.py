from utils import read_data
from advent2019_day25_intcode import run_tape_multithreaded
from multiprocessing import Process, Queue


DATA = [int(x) for x in read_data().split(",")]

# Items needed to pass my detector floor:
# - hologram
# - space heater
# - antenna
# - astronaut ice cream

if __name__ == '__main__':
    input_queue = Queue()
    text_adv = Process(target=run_tape_multithreaded, args=(DATA, input_queue))
    text_adv.start()

    while True:
        command = input() + "\n"
        if command == "exit_simulation\n":
            text_adv.kill()
            exit()
        else:
            input_queue.put(command)
