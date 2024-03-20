"""
Course: CSE 251
Lesson  Week: 11
File:   team2.py
Author: Brother Comeau

Purpose: Team Activity 2: Queue, Pipe, Stack

Instructions:

Part 1:
- Create classes for Queue_t, Pipe_t and Stack_t that are thread safe.
- You can use the List() data structure in your classes.
- Once written, test them using multiple threads.

Part 2
- Create classes for Queue_p, Pipe_p and Stack_p that are process safe.
- You can use the List() data structure in your classes.
- Once written, test them using multiple processes.

Queue methods:
    - constructor(<no arguments>)
    - size()
    - get()
    - put(item)

Stack methods:
    - constructor(<no arguments>)
    - push(item)
    - pop()

Steps:
1) write the Queue_t and test it with threads.
2) write the Queue_p and test it with processes.
3) Implement Stack_t and test it 
4) Implement Stack_p and test it 

Note: Testing means having lots of concurrency/parallelism happening.  Also
some methods for lists are thread safe - some are not.

"""
import time
import threading
import multiprocessing as mp

# -------------------------------------------------------------------
class Queue_t:

    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.queue = []

    def size(self):
        with self.lock:
            size = len(self.queue)
            print(f'size {size}')
        return size

    def get(self):
        with self.lock:
            if len(self.queue) > 0:
                val = self.queue.pop(0)
            else:
                val = 'None'
            print(f'got {val}')
        return val
            
    def put(self, value):
        with self.lock:
            self.queue.append(value)
            print(f'added {value}')


# -------------------------------------------------------------------
class Stack_t:

    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.stack = []

    def size(self):
        with self.lock:
            size = len(self.stack)
            print(f'size {size}')
        return size

    def get(self):
        with self.lock:
            if len(self.stack) > 0:
                val = self.stack.pop()
            else:
                val = 'None'
            print(f'got {val}')
        return val

    def put(self, value):
        with self.lock:
            self.stack.append(value)
            print(f'added {value}')

# -------------------------------------------------------------------
class Queue_p:

    def __init__(self):
        super().__init__()
        self.lock = mp.Lock()
        self.queue = []

    def size(self):
        with self.lock:
            size = len(self.queue)
            print(f'size {size}')
        return size

    def get(self):
        with self.lock:
            if len(self.queue) > 0:
                val = self.queue.pop(0)
            else:
                val = 'None'
            print(f'got {val}')
        return val
            
    def put(self, value):
        with self.lock:
            self.queue.append(value)
            print(f'added {value}')

# -------------------------------------------------------------------
class Stack_p:

    def __init__(self):
        super().__init__()
        self.lock = mp.Lock()
        self.stack = []

    def size(self):
        with self.lock:
            size = len(self.stack)
            print(f'size {size}')
        return size

    def get(self):
        with self.lock:
            if len(self.stack) > 0:
                val = self.stack.pop()
            else:
                val = 'None'
            print(f'got {val}')
        return val

    def put(self, value):
        with self.lock:
            self.stack.append(value)
            print(f'added {value}')

# -------------------------------------------------------------------
def putValues(index, data_struct):
    numbers_to_add = 3
    for i in range(numbers_to_add):
        data_struct.put(f'{index}-{i}')
        # print(f'putter {index} added {index}-{i}')

def getValues(index, data_struct):
    numbers_to_take = 3
    for _ in range(numbers_to_take):
        val = data_struct.get()
        # print(f'getter {index} got {val}')

def getSize(index, data_struct):
    times_to_check_size = 3
    for _ in range(times_to_check_size):
        size = data_struct.size()
        # print(f'checker {index} got size {size}')

# -------------------------------------------------------------------
def main():
    THREADS = 4
    PROCESSES = 4

    print("\nTHREADED QUEUE\n")
    t_queue = Queue_t()
    threads = []
    for i in range(THREADS):
        threads.append(threading.Thread(target=putValues, args=(i, t_queue)))
        threads.append(threading.Thread(target=getValues, args=(i, t_queue)))
        threads.append(threading.Thread(target=getSize, args=(i, t_queue)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("\nTHREADED STACK\n")
    t_stack = Stack_t()
    threads = []
    for i in range(THREADS):
        threads.append(threading.Thread(target=putValues, args=(i, t_stack)))
        threads.append(threading.Thread(target=getValues, args=(i, t_stack)))
        threads.append(threading.Thread(target=getSize, args=(i, t_stack)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("\nPROCESSED QUEUE\n")
    p_queue = Queue_p()
    processes = []
    for i in range(PROCESSES):
        processes.append(mp.Process(target=putValues, args=(i, p_queue)))
        processes.append(mp.Process(target=getValues, args=(i, p_queue)))
        processes.append(mp.Process(target=getSize, args=(i, p_queue)))

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    print("\nPROCESSED STACK\n")
    p_stack = Stack_p()
    processes = []
    for i in range(THREADS):
        processes.append(mp.Process(target=putValues, args=(i, p_stack)))
        processes.append(mp.Process(target=getValues, args=(i, p_stack)))
        processes.append(mp.Process(target=getSize, args=(i, p_stack)))

    for process in processes:
        process.start()

    for process in processes:
        process.join()

if __name__ == '__main__':
    main()