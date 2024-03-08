"""
Course: CSE 251 
Lesson: L09 Prove Part 2
File:   prove_part_2.py
Author: <Add name here>

Purpose: Part 2 of prove 9, finding the path to the end of a maze using recursion.

Instructions:
- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- You MUST use recursive threading to find the end of the maze.
- Each thread MUST have a different color than the previous thread:
    - Use get_color() to get the color for each thread; you will eventually have duplicated colors.
    - Keep using the same color for each branch that a thread is exploring.
    - When you hit an intersection spin off new threads for each option and give them their own colors.

This code is not interested in tracking the path to the end position. Once you have completed this
program however, describe how you could alter the program to display the found path to the exit
position:

What would be your strategy?

I would make it so when I create a new thread I would pass in the path
that all previous paths took to get to that point. Then every time a
thread moved it would add the position it moved to to the accumulating
path. Then once one path found the exit, it's path would be returned 
up the recursion tree and we could print it at the end.

Why would it work?

This would work because every individual thread would have a different
path, so the ones that are incorrect would just be left to the garbage
collector. But the correct path would be saved through the recursive
return statements.

"""

import math
import threading 
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 251 files
from cse251 import *

SCREEN_SIZE = 700
COLOR = (0, 0, 255)
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)
SLOW_SPEED = 100
FAST_SPEED = 0

# Globals
current_color_index = 0
thread_count = 0
stop = False
speed = SLOW_SPEED

def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


def solve_maze_recursively(maze, pos, COLOR, stop_lock):
    global stop
    global thread_count

    with stop_lock:
        if stop:
            return True
    
    row, col = pos
    if maze.can_move_here(row, col):
        maze.move(row, col, COLOR)

    if maze.at_end(row, col):
        with stop_lock:
            stop = True
        return True
    
    threads = []
    moves = maze.get_possible_moves(row, col)
    if len(moves) > 0:
        last_move = moves.pop()
        for move in moves:
            if maze.can_move_here(move[0], move[1]):
                threads.append(threading.Thread(target=solve_maze_recursively, args=(maze, move, get_color(), stop_lock)))
                thread_count += 1

        for thread in threads:
            thread.start()
        
        if maze.can_move_here(last_move[0], last_move[1]):
            if solve_maze_recursively(maze, last_move, COLOR, stop_lock):
                with stop_lock:
                    stop = True
                return True
            
        for thread in threads:
            if thread.join():
                with stop_lock:
                    stop = True
                return True
    
    with stop_lock:
        if stop:
            return True
    maze.restore(row, col)
    return False


def solve_find_end(maze):
    """ Finds the end position using threads. Nothing is returned. """
    # When one of the threads finds the end position, stop all of them.
    global thread_count
    global stop
    stop = False
    thread_count = 0
    starting_pos = maze.get_start_pos()
    stop_lock = threading.Lock()
    t = threading.Thread(target=solve_maze_recursively, args=(maze, starting_pos, get_color(), stop_lock))
    t.start()
    thread_count += 1
    t.join()


def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

    done = False
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('1'):
                speed = SLOW_SPEED
            elif key == ord('2'):
                speed = FAST_SPEED
            elif key == ord('q'):
                exit()
            elif key != ord('p'):
                done = True
        else:
            done = True


def find_ends(log):
    """ Do not change this function """

    files = (
        ('very-small.bmp', True),
        ('very-small-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False),
        ('large-squares.bmp', False),
        ('large-open.bmp', False)
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()