"""
Course: CSE 251 
Lesson: L07 Prove
File:   prove.py
Author: <Add name here>

Purpose: Process Task Files.

Instructions:

See Canvas for the full instructions for this assignment. You will need to complete the TODO comment
below before submitting this file:

Add your comments here on the pool sizes that you used for your assignment and why they were the best choices:

For the pool sizes, I decided that it would be faster if I dedicated more of the CPU power to the I/O 
bound problems (the word and name tasks) than the CPU bound issues so that more requests for external
issues could be started while the other processes quickly worked through the CPU problems. So I had it
where there was a 2 cores dedicated to each of the CPU bound problems and the rest of the cores were 
divided between the two I/O bound issues. That made it much faster than when I tried it the other way
around (with the majority on the CPU bound problems and the minority on the I/O bound problems). 

But then out of curiosity I tried simply splitting the number of cores evenly between the different tasks 
and that was a little faster. So I did that, splitting the number of cores evenly, and adding the 
remainder to the biggest I/O problem (the one that goes out to the server) because it is faster to 
give I/O bound problems more cores than CPU bound problems.

"""

from datetime import datetime, timedelta
import requests
import multiprocessing as mp
from matplotlib.pylab import plt
import numpy as np
import glob
import math 
import os

# Include cse 251 common Python files - Dont change
from cse251 import *

# Constants - Don't change
TYPE_PRIME  = 'prime'
TYPE_WORD   = 'word'
TYPE_UPPER  = 'upper'
TYPE_SUM    = 'sum'
TYPE_NAME   = 'name'

CPU_COUNT = os.cpu_count()

PRIME_POOL_SIZE = CPU_COUNT // 5
WORD_POOL_SIZE  = CPU_COUNT // 5
UPPER_POOL_SIZE = CPU_COUNT // 5
SUM_POOL_SIZE   = CPU_COUNT // 5
NAME_POOL_SIZE  = (CPU_COUNT // 5) + (CPU_COUNT % 5)


# Global lists to collect the task results
result_primes = []
result_words = []
result_upper = []
result_sums = []
result_names = []

def is_prime(n: int):
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


def task_prime(value):
    """
    Use the is_prime() above
    Add the following to the global list:
        {value} is prime
            - or -
        {value} is not prime
    """
    if is_prime(value):
        return f'{value:,} is prime'
    else:
        return f'{value:,} is not prime'

def prime_callback(prime_msg):
    global result_primes
    result_primes.append(prime_msg)


def task_word(word):
    """
    search in file 'words.txt'
    Add the following to the global list:
        {word} found
            - or -
        {word} not found *****
    """
    with open ('words.txt', 'r') as words:
        for file_word in words:
            if word == file_word:
                return f'{word} found'
        return f'{word} not found'

def word_callback(found_msg):
    global result_words
    result_words.append(found_msg)


def task_upper(text):
    """
    Add the following to the global list:
        {text} ==>  uppercase version of {text}
    """
    return f'{text} ==> {text.upper()}'

def upper_callback(upper_msg):
    global result_upper
    result_upper.append(upper_msg)


def task_sum(start_value, end_value):
    """
    Add the following to the global list:
        sum of {start_value:,} to {end_value:,} = {total:,}
    """
    total = 0
    for i in range(start_value, end_value + 1):
        total += i
    return f'sum of {start_value:,} to {end_value:,} = {total:,}'

def sum_callback(total_msg):
    global result_sums
    result_sums.append(total_msg)


def task_name(url):
    """
    use requests module
    Add the following to the global list:
        {url} has name <name>
            - or -
        {url} had an error receiving the information
    """
    response = requests.get(url)
    if response.status_code == 200:
        response_as_dict = response.json()
        return f'{url} has name {response_as_dict['name']}'
    else:
        return f'{url} had an error receiving the information'

def name_callback(name_msg):
    global result_names
    result_names.append(name_msg)


def main():
    log = Log(show_terminal=True)
    log.start_timer()

    # Create process pools
    prime_pool = mp.Pool(PRIME_POOL_SIZE)
    word_pool = mp.Pool(WORD_POOL_SIZE)
    upper_pool = mp.Pool(UPPER_POOL_SIZE)
    sum_pool = mp.Pool(SUM_POOL_SIZE)
    name_pool = mp.Pool(NAME_POOL_SIZE)

    # Start the pools
    count = 0
    task_files = glob.glob("tasks/*.task")
    for filename in task_files:
        # print()
        # print(filename)
        task = load_json_file(filename)
        print(task)
        count += 1
        task_type = task['task']
        if task_type == TYPE_PRIME:
            prime_pool.apply_async(task_prime, args=(task['value'],), callback=prime_callback)
            # task_prime(task['value'])
        elif task_type == TYPE_WORD:
            word_pool.apply_async(task_word, args=(task['word'],), callback=word_callback)
            # task_word(task['word'])
        elif task_type == TYPE_UPPER:
            upper_pool.apply_async(task_upper, args=(task['text'],), callback=upper_callback)
            # task_upper(task['text'])
        elif task_type == TYPE_SUM:
            sum_pool.apply_async(task_sum, args=(task['start'], task['end']), callback=sum_callback)
            # task_sum(task['start'], task['end'])
        elif task_type == TYPE_NAME:
            name_pool.apply_async(task_name, args=(task['url'],), callback=name_callback)
            # task_name(task['url'])
        else:
            log.write(f'Error: unknown task type {task_type}')

    # Wait on the pools
    prime_pool.close()
    word_pool.close()
    upper_pool.close()
    sum_pool.close()
    name_pool.close()

    prime_pool.join()
    word_pool.join()
    upper_pool.join()
    sum_pool.join()
    name_pool.join()


    # DO NOT change any code below this line!
    #---------------------------------------------------------------------------
    def log_list(lst, log):
        for item in lst:
            log.write(item)
        log.write(' ')
    
    log.write('-' * 80)
    log.write(f'Primes: {len(result_primes)}')
    log_list(result_primes, log)

    log.write('-' * 80)
    log.write(f'Words: {len(result_words)}')
    log_list(result_words, log)

    log.write('-' * 80)
    log.write(f'Uppercase: {len(result_upper)}')
    log_list(result_upper, log)

    log.write('-' * 80)
    log.write(f'Sums: {len(result_sums)}')
    log_list(result_sums, log)

    log.write('-' * 80)
    log.write(f'Names: {len(result_names)}')
    log_list(result_names, log)

    log.write(f'Number of Primes tasks: {len(result_primes)}')
    log.write(f'Number of Words tasks: {len(result_words)}')
    log.write(f'Number of Uppercase tasks: {len(result_upper)}')
    log.write(f'Number of Sums tasks: {len(result_sums)}')
    log.write(f'Number of Names tasks: {len(result_names)}')
    log.stop_timer(f'Total time to process {count} tasks')


if __name__ == '__main__':
    main()