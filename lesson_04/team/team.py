"""
Course: CSE 251 
Lesson: L04 Team Activity
File:   team.py
Author: <Add name here>

Purpose: Practice concepts of Queues, Locks, and Semaphores.

Instructions:

- Review instructions in Canvas.

Question:

- Is the Python Queue thread safe? (https://en.wikipedia.org/wiki/Thread_safety)
"""

import threading
import queue
import requests
import json

# Include cse 251 common Python files
from cse251 import *

RETRIEVE_THREADS = 38        # Number of retrieve_threads
NO_MORE_VALUES = 'No more'  # Special value to indicate no more items in the queue

def retrieve_thread(queue, sem, log, i):
    """ Process values from the data_queue """

    while True:
        # check to see if anything is in the queue
        sem.acquire()
        # process the value retrieved from the queue
        url = queue.get()
        if url == NO_MORE_VALUES:
            break
        else:
            # make Internet call to get characters name and log it
            response = requests.get(url)
            # Check the status code to see if the request succeeded.
            status_code = response.status_code
            if response.status_code == 200:
                response = response.json()
                log.write(response['name'])
            else:
                print('RESPONSE = ', response.status_code)


def file_reader(queue, sem, log):
    """ This thread reads the data file and places the values in the data_queue """
    # Open the data file "urls.txt" and place items into a queue
    with open("urls.txt") as urls:
        for url in urls:
            url = url.strip()
            queue.put(url)
            sem.release()

    log.write(f'finished reading file with {RETRIEVE_THREADS} threads')

    # signal the retrieve threads one more time that there are "no more values"
    for i in range(RETRIEVE_THREADS):
        queue.put(NO_MORE_VALUES)
        sem.release()
    



def main():
    """ Main function """

    log = Log(show_terminal=True)

    # create queue
    q = queue.Queue()
    # create semaphore (if needed)
    sem = threading.Semaphore(0)

    retrieve_threads = []

    # create the threads. 1 filereader() and RETRIEVE_THREADS retrieve_thread()s
    # Pass any arguments to these thread need to do their job
    file_reader_thread = threading.Thread(target=file_reader, args=(q, sem, log))

    for i in range(RETRIEVE_THREADS):
        retrieve_threads.append(threading.Thread(target=retrieve_thread, args=(q, sem, log, i)))

    log.start_timer()

    # Get them going - start the retrieve_threads first, then file_reader
    file_reader_thread.start()

    for thread in retrieve_threads:
        thread.start()

    # Wait for them to finish - The order doesn't matter
    file_reader_thread.join()

    for thread in retrieve_threads:
        thread.join()

    log.stop_timer('Time to process all URLS')


if __name__ == '__main__':
    main()



