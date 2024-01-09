"""
Author: Brother Keers + Bard AI

In this example

"""

import time
import math
import sys
import multiprocessing as mp
import psutil

def get_safe_ish_large_number():
    """ Determines a relatively large number that SHOULD still be safe to attempt on your computer. """
    total_ram = psutil.virtual_memory().total
    total_ram = math.floor(total_ram / 1024 ** 3)
    # Create a little over a million numbers for every GB of ram capped at 90% of availability.
    safe_ish_number = math.floor(1_100_100 * (total_ram * .9))
    # Stress the CPU by multiplying this large number by 1.5 times the available cores.
    return math.floor(mp.cpu_count() * 1.5 * safe_ish_number)


def reverse_list_recursively_naive(lst, start=0, end=-1):
    """ A poorly written algorithm that reverses the order of a list manually. """
    reversed_list = []
    for i in range(len(lst) - 1, -1, -1):
        reversed_list.append(lst[i])
    return reversed_list
    """
    NOTE: This method is actually slightly optimized by Python. Try using the following truly manual
    method and your computer may crash. Source: https://stackoverflow.com/a/217204/3193156

    def reverse(lst, start=0, end=-1):
        if start >= len(l)/2: return
        l[start], l[end] = l[end], l[start]
        reverse(lst, start + 1, end - 1)
    """


def reverse_list_optimized(lst):
    """
    An optimized solution to reversing the order of a list using Pythons built-in list slicing.

    List slicing is a python feature that is heavily optimized because it uses C code under the hood.
    This improves performance in many ways but most notably:

    - Allows for direct access to the underlying memory layout and optimized machine code execution.
    - The interpreter and underlying memory management mechanisms try to keep frequently accessed data in the CPU cache, reducing the need for costly memory accesses

    Learn more from the following resources:

    - https://www.geeksforgeeks.org/python-list-slicing/
    - https://www.codecademy.com/learn/dacp-python-fundamentals/modules/dscp-python-lists/cheatsheet#heading-list-slicing
    """
    return lst[::-1]


def main():
    # Get a safe-ish large number and make a list of that many items; this will use all available RAM!
    numbers = get_safe_ish_large_number()
    lst = list(range(numbers))

    # Show how many numbers we created to the user.
    print(f'Created list with {numbers:,} items.')
    
    # Optimized list reversal first.
    start_time = time.time()
    reverse_list_optimized(lst)
    end_time = time.time()
    print(f'Optimized list reversal time: {end_time - start_time:.5f} secs')

    # Naive list reversal second.
    start_time = time.time()
    reverse_list_recursively_naive(lst)
    end_time = time.time()
    print(f'Naive list reversal time: {end_time - start_time:.5f} secs')


if __name__ == "__main__":
    main()