"""
Course: CSE 251
Lesson Week: 11
File: Assignment.py
"""

import time
import random
import multiprocessing as mp

# number of cleaning staff and hotel guests
CLEANING_STAFF = 2
HOTEL_GUESTS = 5

# Run program for this number of seconds
TIME = 60

STARTING_PARTY_MESSAGE =  'Turning on the lights for the party vvvvvvvvvvvvvv'
STOPPING_PARTY_MESSAGE  = 'Turning off the lights  ^^^^^^^^^^^^^^^^^^^^^^^^^^'

STARTING_CLEANING_MESSAGE =  'Starting to clean the room >>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
STOPPING_CLEANING_MESSAGE  = 'Finish cleaning the room <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'

def cleaner_waiting():
    time.sleep(random.uniform(0, 2))

def cleaner_cleaning(id):
    print(f'Cleaner: {id}')
    time.sleep(random.uniform(0, 2))

def guest_waiting():
    time.sleep(random.uniform(0, 2))

def guest_partying(id, count):
    print(f'Guest: {id}, count = {count}')
    time.sleep(random.uniform(0, 1))

def is_time_up(start_time):
    current_time = time.perf_counter()
    time_passed_int = int(current_time - start_time)
    # print(f'time passed: {current_time - start_time}')
    if time_passed_int >= TIME:
        return True
    return False

def cleaner(start_time, id, empty_room, is_cleaning, cleaned_count):
    """
    do the following for TIME seconds
        cleaner will wait to try to clean the room (cleaner_waiting())
        get access to the room
        display message STARTING_CLEANING_MESSAGE
        Take some time cleaning (cleaner_cleaning())
        display message STOPPING_CLEANING_MESSAGE
    """
    time_up = False
    while time_up == False:
        cleaner_waiting()
        with empty_room:
            if is_time_up(start_time):
                    break
            with is_cleaning:
                if is_time_up(start_time):
                    break
                print(STARTING_CLEANING_MESSAGE)
                cleaner_cleaning(id)
                if is_time_up(start_time):
                    break
                print(STOPPING_CLEANING_MESSAGE)
                cleaned_count.value += 1


def guest(start_time, id, empty_room, is_cleaning, count, party_count):
    """
    do the following for TIME seconds
        guest will wait to try to get access to the room (guest_waiting())
        get access to the room
        display message STARTING_PARTY_MESSAGE if this guest is the first one in the room
        Take some time partying (call guest_partying())
        display message STOPPING_PARTY_MESSAGE if the guest is the last one leaving in the room
    """
    time_up = False
    while time_up == False:
        if is_time_up(start_time):
            break
        room_was_empty = empty_room.acquire(block=False)
        # No one is in the room
        if room_was_empty:
            # Do something with the lock
            count.value += 1
            print(STARTING_PARTY_MESSAGE)
            guest_partying(id, count.value)
            count.value -= 1
            if count.value == 0:
                print(STOPPING_PARTY_MESSAGE)
                party_count.value += 1
                empty_room.release()
            if is_time_up(start_time):
                break
            guest_waiting()
            if is_time_up(start_time):
                break
        # If there is another guest in the room 
        elif count.value >= 1:
            # The lock was not acquired, so do something else
            count.value += 1
            guest_partying(id, count.value)
            count.value -= 1
            if count.value == 0:
                print(STOPPING_PARTY_MESSAGE)
                party_count.value += 1
                empty_room.release()
            if is_time_up(start_time):
                break
            guest_waiting()
            if is_time_up(start_time):
                break
        # There is a maid cleaning
        else:
            is_cleaning.acquire()
            is_cleaning.release()

            

def main():
    # Start time of the running of the program. 
    start_time = time.perf_counter()

    # TODO - add any variables, data structures, processes you need
    # TODO - add any arguments to cleaner() and guest() that you need

    empty_room = mp.Lock()
    is_cleaning = mp.Lock()
    count = mp.Value('i', 0)
    cleaned_count = mp.Value('i', 0)
    party_count = mp.Value('i', 0)
    
    # Create the cleaners
    cleaners = []
    for i in range(CLEANING_STAFF):
        cleaners.append(mp.Process(target=cleaner, args=(start_time, i + 1, empty_room, is_cleaning, cleaned_count)))
    # Create the guests
    guests = []
    for i in range(HOTEL_GUESTS):
        guests.append(mp.Process(target=guest, args=(start_time, i + 1, empty_room, is_cleaning, count, party_count)))

    # Start the cleaners
    for process in cleaners:
        process.start()
    # Start the guests
    for process in guests:
        process.start()

    # Wait for the cleaners to finish
    for process in cleaners:
        process.join()
    # Wait for the guests to finish
    for process in guests:
        process.join()


    # Results
    print(f'Room was cleaned {cleaned_count.value} times, there were {party_count.value} parties')


if __name__ == '__main__':
    main()

