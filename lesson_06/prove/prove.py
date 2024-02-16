"""
Course: CSE 251 
Lesson: L06 Prove
File:   prove.py
Author: <Add name here>

Purpose: Processing Plant

Instructions:

- Implement the necessary classes to allow gifts to be created.
"""

import random
import multiprocessing as mp
import os.path
import time
import datetime

# Include cse 251 common Python files - Don't change
from cse251 import *

CONTROL_FILENAME = 'settings.json'
BOXES_FILENAME   = 'boxes.txt'

# Settings constants
MARBLE_COUNT = 'marble-count'
CREATOR_DELAY = 'creator-delay'
NUMBER_OF_MARBLES_IN_A_BAG = 'bag-count'
BAGGER_DELAY = 'bagger-delay'
ASSEMBLER_DELAY = 'assembler-delay'
WRAPPER_DELAY = 'wrapper-delay'

# No Global variables

class Bag():
    """ Bag of marbles - Don't change """

    def __init__(self):
        self.items = []

    def add(self, marble):
        self.items.append(marble)

    def get_size(self):
        return len(self.items)

    def __str__(self):
        return str(self.items)

class Gift():
    """
    Gift of a large marble and a bag of marbles - Don't change

    Parameters:
        large_marble (string): The name of the large marble for this gift.
        marbles (Bag): A completed bag of small marbles for this gift.
    """

    def __init__(self, large_marble, marbles):
        self.large_marble = large_marble
        self.marbles = marbles

    def __str__(self):
        marbles = str(self.marbles)
        marbles = marbles.replace("'", "")
        return f'Large marble: {self.large_marble}, marbles: {marbles[1:-1]}'


class Marble_Creator(mp.Process):
    """ This class "creates" marbles and sends them to the bagger """

    def __init__(self, marble_count, marble_delay, send_conn):
        mp.Process.__init__(self)
        self.marble_count = marble_count
        self.marble_delay = marble_delay
        self.send_conn = send_conn
        self.colors = ('Gold', 'Orange Peel', 'Purple Plum', 'Blue', 'Neon Silver', 
        'Tuscan Brown', 'La Salle Green', 'Spanish Orange', 'Pale Goldenrod', 'Orange Soda', 
        'Maximum Purple', 'Neon Pink', 'Light Orchid', 'Russian Violet', 'Sheen Green', 
        'Isabelline', 'Ruby', 'Emerald', 'Middle Red Purple', 'Royal Orange', 'Big Dip O’ruby', 
        'Dark Fuchsia', 'Slate Blue', 'Neon Dark Green', 'Sage', 'Pale Taupe', 'Silver Pink', 
        'Stop Red', 'Eerie Black', 'Indigo', 'Ivory', 'Granny Smith Apple', 
        'Maximum Blue', 'Pale Cerulean', 'Vegas Gold', 'Mulberry', 'Mango Tango', 
        'Fiery Rose', 'Mode Beige', 'Platinum', 'Lilac Luster', 'Duke Blue', 'Candy Pink', 
        'Maximum Violet', 'Spanish Carmine', 'Antique Brass', 'Pale Plum', 'Dark Moss Green', 
        'Mint Cream', 'Shandy', 'Cotton Candy', 'Beaver', 'Rose Quartz', 'Purple', 
        'Almond', 'Zomp', 'Middle Green Yellow', 'Auburn', 'Chinese Red', 'Cobalt Blue', 
        'Lumber', 'Honeydew', 'Icterine', 'Golden Yellow', 'Silver Chalice', 'Lavender Blue', 
        'Outrageous Orange', 'Spanish Pink', 'Liver Chestnut', 'Mimi Pink', 'Royal Red', 'Arylide Yellow', 
        'Rose Dust', 'Terra Cotta', 'Lemon Lime', 'Bistre Brown', 'Venetian Red', 'Brink Pink', 
        'Russian Green', 'Blue Bell', 'Green', 'Black Coral', 'Thulian Pink', 
        'Safety Yellow', 'White Smoke', 'Pastel Gray', 'Orange Soda', 'Lavender Purple',
        'Brown', 'Gold', 'Blue-Green', 'Antique Bronze', 'Mint Green', 'Royal Blue', 
        'Light Orange', 'Pastel Blue', 'Middle Green')

    def run(self):
        '''
        for each marble:
            send the marble (one at a time) to the bagger
              - A marble is a random name from the colors list above
            sleep the required amount
        Let the bagger know there are no more marbles
        '''
        for _ in range(self.marble_count):
            marble = random.choice(self.colors)
            self.send_conn.send(marble)
            time.sleep(self.marble_delay)
        self.send_conn.send(None)
        self.send_conn.close()


class Bagger(mp.Process):
    """ Receives marbles from the marble creator, then when there are enough
        marbles, the bag of marbles are sent to the assembler """
    def __init__(self, num_of_marbles_per_bag, bagger_delay, recv_conn, send_conn):
        mp.Process.__init__(self)
        self.num_per_bag = num_of_marbles_per_bag
        self.bagger_delay = bagger_delay
        self.recv_conn = recv_conn
        self.send_conn = send_conn

    def run(self):
        '''
        while there are marbles to process
            collect enough marbles for a bag
            send the bag to the assembler
            sleep the required amount
        tell the assembler that there are no more bags
        '''
        bag = Bag()
        while True:
            marble = self.recv_conn.recv()
            # If there are no marbles left to receive, send flag and close
            if marble == None:
                self.send_conn.send(None)
                self.send_conn.close()
                break
            # If the bag is not full add the marble to the bag
            if bag.get_size() < self.num_per_bag:
                bag.add(marble)
            # Otherwise, (if the bag is full), send the bag, sleep, and create a new empty bag
            else:
                self.send_conn.send(bag)
                time.sleep(self.bagger_delay)
                bag = Bag()


class Assembler(mp.Process):
    """ Take the set of marbles and create a gift from them.
        Sends the completed gift to the wrapper """

    def __init__(self, assembler_delay, recv_conn, send_conn):
        mp.Process.__init__(self)
        self.assembler_delay = assembler_delay
        self.recv_conn = recv_conn
        self.send_conn = send_conn
        self.marble_names = ('Lucky', 'Spinner', 'Sure Shot', 'Big Joe', 'Winner', '5-Star', 'Hercules', 'Apollo', 'Zeus')

    def run(self):
        '''
        while there are bags to process
            create a gift with a large marble (random from the name list) and the bag of marbles
            send the gift to the wrapper
            sleep the required amount
        tell the wrapper that there are no more gifts
        '''
        while True:
            bag = self.recv_conn.recv()
            # If there are no bags left to receive, send flag and close
            if bag == None:
                self.send_conn.send(None)
                self.send_conn.close()
                break
            # Otherwise, create a large marble
            large_marble = random.choice(self.marble_names)
            # Assemble a gift with the bag and large marble
            gift = Gift(large_marble, bag)
            # Send the gift and sleep
            self.send_conn.send(gift)
            time.sleep(self.assembler_delay)



class Wrapper(mp.Process):
    """ Takes created gifts and "wraps" them by placing them in the boxes file. """
    def __init__(self, wrapper_delay, recv_conn, num_of_gifts, filename):
        mp.Process.__init__(self)
        self.wrapper_delay = wrapper_delay
        self.recv_conn = recv_conn
        self.num_of_gifts = num_of_gifts
        self.filename = filename

    def run(self):
        '''
        open file for writing
        while there are gifts to process
            save gift to the file with the current time
            sleep the required amount
        '''
        while True:
            gift = self.recv_conn.recv()
            # Add a gift to the gift counter
            self.num_of_gifts.value += 1
            # If there are no gifts left, break
            if gift == None:
                break
            # Write each gift to the file
            with open(self.filename, 'a') as file:
                file.write(f'Created - {datetime.now().time()}: {gift.__str__()}\n')


def display_final_boxes(filename, log):
    """ Display the final boxes file to the log file -  Don't change """
    if os.path.exists(filename):
        log.write(f'Contents of {filename}')
        with open(filename) as boxes_file:
            for line in boxes_file:
                log.write(line.strip())
    else:
        log.write_error(f'The file {filename} doesn\'t exist.  No boxes were created.')



def main():
    """ Main function """

    log = Log(show_terminal=True)

    log.start_timer()

    # Load settings file
    settings = load_json_file(CONTROL_FILENAME)
    if settings == {}:
        log.write_error(f'Problem reading in settings file: {CONTROL_FILENAME}')
        return

    log.write(f'Marble count     = {settings[MARBLE_COUNT]}')
    log.write(f'Marble delay     = {settings[CREATOR_DELAY]}')
    log.write(f'Marbles in a bag = {settings[NUMBER_OF_MARBLES_IN_A_BAG]}') 
    log.write(f'Bagger delay     = {settings[BAGGER_DELAY]}')
    log.write(f'Assembler delay  = {settings[ASSEMBLER_DELAY]}')
    log.write(f'Wrapper delay    = {settings[WRAPPER_DELAY]}')

    # Create Pipes between creator -> bagger -> assembler -> wrapper
    creator_send_conn, bagger_recv_conn = mp.Pipe()
    bagger_send_conn, assembler_recv_conn = mp.Pipe()
    assembler_send_conn, wrapper_recv_con = mp.Pipe()

    # Create variable to be used to count the number of gifts
    num_of_gifts = mp.Value('i', 0)

    # Delete final boxes file
    if os.path.exists(BOXES_FILENAME):
        os.remove(BOXES_FILENAME)

    log.write('Create the processes')

    # Create the processes (ie., classes above)
    creator = Marble_Creator(settings[MARBLE_COUNT], settings[CREATOR_DELAY], creator_send_conn)
    bagger = Bagger(settings[NUMBER_OF_MARBLES_IN_A_BAG], settings[BAGGER_DELAY], bagger_recv_conn, bagger_send_conn)
    assembler = Assembler(settings[ASSEMBLER_DELAY], assembler_recv_conn, assembler_send_conn)
    wrapper = Wrapper(settings[WRAPPER_DELAY], wrapper_recv_con, num_of_gifts, BOXES_FILENAME)

    log.write('Starting the processes')
    creator.start()
    bagger.start()
    assembler.start()
    wrapper.start()

    log.write('Waiting for processes to finish')
    creator.join()
    bagger.join()
    assembler.join()
    wrapper.join()

    display_final_boxes(BOXES_FILENAME, log)
    
    # Log the number of gifts created.
    log.write(f'Number of gifts created: {wrapper.num_of_gifts.value}')

    log.stop_timer(f'Total time')




if __name__ == '__main__':
    main()
