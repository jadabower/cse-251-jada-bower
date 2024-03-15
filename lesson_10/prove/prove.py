"""
Course: CSE 251
Lesson Week: 10
File: assignment.py
Author: Jada Bower

Purpose: assignment for week 10 - reader writer problem

Instructions:

- Review TODO comments

- writer: a process that will send numbers to the reader.  
  The values sent to the readers will be in consecutive order starting
  at value 1.  Each writer will use all of the sharedList buffer area
  (ie., BUFFER_SIZE memory positions)

- reader: a process that receive numbers sent by the writer.  The reader will
  accept values until indicated by the writer that there are no more values to
  process.  

- Do not use try...except statements

- Display the numbers received by the reader printing them to the console.

- Create WRITERS writer processes

- Create READERS reader processes

- You can use sleep() statements for any process.

- You are able (should) to use lock(s) and semaphore(s).  When using locks, you can't
  use the arguments "block=False" or "timeout".  Your goal is to make your
  program as parallel as you can.  Over use of lock(s), or semaphore(s) in the wrong
  place will slow down your code.

- You must use ShareableList between the two processes.  This shareable list
  will contain different "sections".  There can only be one shareable list used
  between your processes.
  1) BUFFER_SIZE number of positions for data transfer. This buffer area must
     act like a queue - First In First Out.
  2) current value used by writers for consecutive order of values to send
  3) Any indexes that the processes need to keep track of the data queue
  4) Any other values you need for the assignment

- Not allowed to use Queue(), Pipe(), List(), Barrier() or any other data structure.

- Not allowed to use Value() or Array() or any other shared data type from 
  the multiprocessing package.

- When each reader reads a value from the sharedList, use the following code to display
  the value:
  
                    print(<variable from the buffer>, end=', ', flush=True)

Add any comments for me:

"""

import random
from multiprocessing.managers import SharedMemoryManager
import multiprocessing as mp

BUFFER_SIZE = 10
READERS = 2
WRITERS = 2


class Reader(mp.Process):
    """ Reads from the buffer """
    def __init__(self, buff, read_lock, available_to_read_sem, available_to_write_sem):
        mp.Process.__init__(self)
        self.buff = buff
        # Indices in buff of the given values
        self.tail_i = 1
        self.num_read = 2
        self.read_lock = read_lock
        self.available_to_read_sem = available_to_read_sem
        self.available_to_write_sem = available_to_write_sem

    def run(self):
        while True:
            # Acquire from the semaphore to make sure the tail never gets ahead of the head
            self.available_to_read_sem.acquire()
            # Acquire the read lock to make sure only one process reads the next value
            self.read_lock.acquire()
            current_val = self.buff[self.buff[self.tail_i]]

            # Base case
            if current_val == None:
                self.read_lock.release()
                break

            # Print the number and increment the number of values read
            print(current_val, end=', ', flush=True)
            self.buff[self.num_read] += 1

            # Logic for incrementing the tail by one
            self.buff[self.tail_i] += 1
            if self.buff[self.tail_i] >= BUFFER_SIZE + 4:
                self.buff[self.tail_i] = 4

            # Release the semaphore to make sure the Head knows it can continue
            self.available_to_write_sem.release()
            self.read_lock.release()


class Writer(mp.Process):
    """ Write to the buffer """
    def __init__(self, buff, write_lock, available_to_read_sem, available_to_write_sem, max_val, num_of_readers, writer_index):
        mp.Process.__init__(self)
        self.buff = buff
        # Indices in buff of the given values
        self.head_i = 0
        self.num_to_write = 3
        self.write_lock = write_lock
        self.available_to_read_sem = available_to_read_sem
        self.available_to_write_sem = available_to_write_sem
        self.max_val = max_val
        self.num_of_readers = num_of_readers
        self.writer_index = writer_index

    def run(self):
        while True:
            # Acquire from the semaphore to make sure the tail never gets ahead of the head
            self.available_to_write_sem.acquire()
            # Acquire the write lock to make sure only one process writes the next value
            self.write_lock.acquire()
            current_val = self.buff[self.num_to_write]

            # Base case
            if current_val > self.max_val:
                if self.writer_index == 0:
                    for _ in range(self.num_of_readers):
                        self.available_to_read_sem.release()
                    self.buff[self.buff[self.head_i]] = None
                self.write_lock.release()
                break

            # Write the number to the buffer and increment the value to be read
            self.buff[self.buff[self.head_i]] = current_val
            self.buff[self.num_to_write] += 1

            # Logic for incrementing the head by one
            self.buff[self.head_i] += 1
            if self.buff[self.head_i] >= BUFFER_SIZE + 4:
                self.buff[self.head_i] = 4
            
            # Release the semaphore to make sure the tail knows it can continue
            self.available_to_read_sem.release()
            self.write_lock.release()


def main():

    # This is the number of values that the writer will send to the reader
    items_to_send = random.randint(1000, 10000)

    smm = SharedMemoryManager()
    smm.start()

    # - Create a ShareableList to be used between the processes
    # - The buffer should be size 10 PLUS at least three other
    #   values (ie., [0] * (BUFFER_SIZE + 3)).  The extra values
    #   are used for the head and tail for the circular buffer.
    #   The other value is the current number that the writers
    #   need to send over the buffer.  This last value is shared
    #   between the writers.
    #   You can add another value to the shareable list to keep
    #   track of the number of values received by the readers.
    #   (ie., [0] * (BUFFER_SIZE + 4))
    
    buff = smm.ShareableList([0] * (BUFFER_SIZE + 4))

    # The following are the indices of the buffer
    head_i = 0
    tail_i = 1
    num_read = 2
    num_to_write = 3

    # Set the values in the buffer to the starting values
    buff[head_i] = 4
    buff[tail_i] = 4
    buff[num_to_write] = 1


    # Create any lock(s) or semaphore(s) that you feel you need
    read_lock = mp.Lock()
    write_lock = mp.Lock()
    available_to_read_sem = mp.Semaphore(0)
    available_to_write_sem = mp.Semaphore(BUFFER_SIZE)

    # Create reader and writer processes
    readers = []
    for _ in range(READERS):
        readers.append(Reader(buff, read_lock, available_to_read_sem, available_to_write_sem))
    writers = []
    for i in range(WRITERS):
        writers.append(Writer(buff, write_lock, available_to_read_sem, available_to_write_sem, items_to_send, READERS, i))

    # Start the processes and wait for them to finish
    for reader in readers:
        reader.start()
    for writer in writers:
        writer.start()

    for reader in readers:
        reader.join()
    for writer in writers:
        writer.join()


    print(f'\n\n{items_to_send} values sent')

    items_received = buff[num_read]

    # Display the number of numbers/items received by the reader.
    # Can not use "items_to_send", must be a value collected
    # by the reader processes.

    print(f'{items_received} values received')

    smm.shutdown()


if __name__ == '__main__':
    main()