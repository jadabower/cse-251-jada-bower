"""
Course: CSE 251 
Lesson: L06 Team Activity
File:   team.py
Author: <Add name here>

Purpose: Team Activity

Instructions:

- Implement the process functions to copy a text file exactly using a pipe
- After you can copy a text file word by word exactly, change the program (any way you want) to be
  faster (still using the processes).
"""

import multiprocessing as mp
from multiprocessing import Value, Process
import filecmp 

# Include cse 251 common Python files
from cse251 import *

# This is the parent connection function.
def sender(filename1, conn):
    """ function to send messages to other end of pipe """
    '''
    open the file
    send all contents of the file over a pipe to the other process
    Note: you must break each line in the file into words and
          send those words through the pipe
    '''
    with open(filename1, 'r', newline = '\n') as file:
        file_list = file.read()
        for i in range(len(file_list)):
            # Get the text as a list of words.
            words = file_list[i].split(' ')
            for j in range(len(words)):
                # Send the current word.
                conn.send(f'{words[j]}')
                # If this is the last word in the last line, send the flag.
                # Otherwise send a space to prepare for the next word.
                if j == len(words) - 1:
                    if i == len(file_list) - 1:
                        # Send a flag to show this is the end of the file.
                        conn.send(None)
                else:
                    conn.send(' ')

    # Close this connection when done.
    conn.close()


# Thus is the child connection function.
def receiver(filename2, conn_receiver, pipe_counter, send_conn_counter):
    """ function to print the messages received from other end of pipe """
    ''' 
    open the file for writing
    receive all content through the shared pipe and write to the file
    Keep track of the number of items sent over the pipe
    '''
    while True:
        # Receive data down the pipe.
        data = conn_receiver.recv()
        # print(f"Received: {data}")
        pipe_counter += 1

        # If this is the flag, send the final count, and stop writing.
        if data == None:
            send_conn_counter.send(pipe_counter)
            send_conn_counter.close()
            break

        
        # Write each item to the copy file.
        with open(filename2, 'a', newline = '\n') as file:
            file.write(data)


def are_files_same(filename1, filename2):
    """ Return True if two files are the same """
    return filecmp.cmp(filename1, filename2, shallow = False) 


def copy_file(log, filename1, filename2):
    # Clear the file to write to.
    open(filename2, 'w', newline = '\n').close()

    # Create a pipe.
    sender_conn, receiver_conn = mp.Pipe()
    send_conn_counter, receive_conn_counter = mp.Pipe()
    
    # Create variable to count items sent over the pipe.
    pipe_count = 0

    # Create processes.
    reader = mp.Process(target=sender, args=(filename1, sender_conn))
    writer = mp.Process(target=receiver, args=(filename2, receiver_conn, pipe_count, send_conn_counter))

    log.start_timer()
    start_time = log.get_time()

    # Start processes.
    reader.start()
    writer.start()

    # Wait for processes to finish.
    reader.join()
    pipe_count = receive_conn_counter.recv()
    writer.join()


    stop_time = log.get_time()

    log.stop_timer(f'Total time to transfer content = {stop_time - start_time}: ')
    log.write(f'items / second = {(pipe_count) / (stop_time - start_time)}')

    if are_files_same(filename1, filename2):
        log.write(f'{filename1} - Files are the same')
    else:
        log.write(f'{filename1} - Files are different')


if __name__ == "__main__": 

    log = Log(show_terminal=True)

    # copy_file(log, 'gettysburg.txt', 'gettysburg-copy.txt')
    
    # After you get the gettysburg.txt file working, uncomment this statement
    copy_file(log, 'bom.txt', 'bom-copy.txt')