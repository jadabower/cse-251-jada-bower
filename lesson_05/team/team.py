"""
Course: CSE 251 
Lesson: L05 Team Activity
File:   team.py
Author: <Add your name here>

Purpose: Check for prime values

Instructions:

- You can't use thread pools or process pools.
- Follow the graph from the `../canvas/teams.md` instructions.
- Start with PRIME_PROCESS_COUNT = 1, then once it works, increase it.
"""

import time
import threading
import multiprocessing as mp
import random
from os.path import exists

#Include cse 251 common Python files
from cse251 import *

PRIME_PROCESS_COUNT = 3

def is_prime(n: int) -> bool:
    """Primality test using 6k+-1 optimization.
    From: https://en.wikipedia.org/wiki/Primality_test
    """
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def read_thread(filename, shared_unfiltered, sem):
    # log.write('Started reading file')
    with open(filename) as file:
        for line in file:
            num = int(line.strip())
            shared_unfiltered.put(num)
            print(f'Added: {num}')
            sem.release()
    for _ in range(PRIME_PROCESS_COUNT):
        shared_unfiltered.put('DONE')
        sem.release()
    # log.write('Finished reading file')


def prime_processes(shared_unfiltered, shared_primes, sem):
    # log.write('Started processing numbers')
    while True:
        sem.acquire()
        possible_num = shared_unfiltered.get()
        print(f'Processing: {possible_num}')
        # log.write(f'Processing: {possible_num}')
        if type(possible_num) != int:
            # log.write('Finished processing numbers')
            break
        is_num_prime = is_prime(possible_num)
        if is_num_prime:
            shared_primes.put(possible_num)
            print(f'Found prime: {possible_num}')


def create_data_txt(filename):
    # only create if is doesn't exist 
    if not exists(filename):
        with open(filename, 'w') as f:
            for _ in range(1000):
                f.write(str(random.randint(10000000000, 100000000000000)) + '\n')


def main():
    """ Main function """

    # Create the data file for this demo if it does not already exist.
    filename = 'data.txt'
    create_data_txt(filename)

    log = Log(show_terminal=True)
    log.start_timer()

    # Create shared data structures
    processes = []
    sem = mp.Semaphore(0)
    unfiltered = mp.Queue()
    primes = mp.Queue()
    log.write('Created shared structures')

    # Create reading thread
    reader = mp.Process(target=read_thread, args=(filename, unfiltered, sem))
    log.write('Created reader')

    # Create prime processes
    for _ in range(PRIME_PROCESS_COUNT):
        processor = mp.Process(target=prime_processes, args=(unfiltered, primes, sem))
        processes.append(processor)
    log.write('Created processors')

    # Start them all
    reader.start()
    for i in processes:
        i.start()
    log.write('Started')

    # Wait for them to complete
    reader.join()
    for i in processes:
        i.join()
    log.write('Joined')
    primes.put('STOP')

    log.stop_timer(f'All primes have been found using {PRIME_PROCESS_COUNT} processes')

    primes_list = []
    
    for i in iter(primes.get, 'STOP'):
        primes_list.append(i)

    # display the list of primes
    print(f'There are {len(primes_list)} found:')
    for prime in primes_list:
        print(prime)


if __name__ == '__main__':
    main()
