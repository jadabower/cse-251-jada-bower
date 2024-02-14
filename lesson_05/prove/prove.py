"""
Course: CSE 251 
Lesson: L05 Prove
File:   prove.py
Author: <Add name here>

Purpose: Assignment 05 - Factories and Dealers

Instructions:

- Read the comments in the following code.  
- Implement your code where the TODO comments are found.
- No global variables, all data must be passed to the objects.
- Only the included/imported packages are allowed.  
- Thread/process pools are not allowed
- You MUST use a barrier!
- Do not use try...except statements.
- You are not allowed to use the normal Python Queue object. You must use Queue251.
- The shared queue between the threads that are used to hold the Car objects
  can not be greater than MAX_QUEUE_SIZE.
"""

from datetime import datetime, timedelta
import time
import threading
import random

# Include cse 251 common Python files.
from cse251 import *

# Global Constants.
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 50

# NO GLOBAL VARIABLES!

class Car():
    """ This is the Car class that will be created by the factories """

    # Class Variables.
    car_makes = ('Ford', 'Chevrolet', 'Dodge', 'Fiat', 'Volvo', 'Infiniti', 'Jeep', 'Subaru', 
                'Buick', 'Volkswagen', 'Chrysler', 'Smart', 'Nissan', 'Toyota', 'Lexus', 
                'Mitsubishi', 'Mazda', 'Hyundai', 'Kia', 'Acura', 'Honda')

    car_models = ('A1', 'M1', 'XOX', 'XL', 'XLS', 'XLE' ,'Super' ,'Tall' ,'Flat', 'Middle', 'Round',
                'A2', 'M1X', 'SE', 'SXE', 'MM', 'Charger', 'Grand', 'Viper', 'F150', 'Town', 'Ranger',
                'G35', 'Titan', 'M5', 'GX', 'Sport', 'RX')

    car_years = [i for i in range(1990, datetime.now().year)]

    def __init__(self):
        # Make a random car.
        self.model = random.choice(Car.car_models)
        self.make = random.choice(Car.car_makes)
        self.year = random.choice(Car.car_years)

        # Sleep a little. Last statement in this for loop - don't change.
        time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))

        # Display the car that has was just created in the terminal.
        # print(f'Created: {self.info()}')
           
    def info(self):
        """ Helper function to quickly get the car information. """
        return f'{self.make} {self.model}, {self.year}'


class Queue251():
    """ This is the queue object to use for this assignment. Do not modify!! """

    def __init__(self):
        self.items = []
        self.max_size = 0

    def get_max_size(self):
        return self.max_size

    def put(self, item):
        self.items.append(item)
        if len(self.items) > self.max_size:
            self.max_size = len(self.items)

    def get(self):
        return self.items.pop(0)

class Factory(threading.Thread):
    """ This is a factory.  It will create cars and place them on the car queue """

    def __init__(self, cars_to_produce_sem, cars_to_sell_sem, car_queue, finished_producing_barrier, num_of_dealers):
        super().__init__()
        # All of the data that 1 factory needs to create cars and to place them in a queue.
        self.cars_to_produce = random.randint(200, 300) # DO NOT change.
        self.f_sem = cars_to_produce_sem
        self.d_sem = cars_to_sell_sem
        self.cars = car_queue
        self.barrier = finished_producing_barrier
        self.num_of_dealers = num_of_dealers
        self.cars_produced = 0

    def run(self):
        for _ in range(self.cars_to_produce):
            """
            create a car
            place the car on the queue
            signal the dealer that there is a car on the queue
           """
            # Produce the cars, then send them to the dealerships.
            self.f_sem.acquire()
            car = Car()
            self.cars.put(car)
            self.cars_produced += 1
            self.d_sem.release()

        # Wait until all of the factories are finished producing cars.
        wait_num = self.barrier.wait()

        # "Wake up/signal" the dealerships one more time.  Select one factory to do this.
        if wait_num == 0:
            for _ in range(self.num_of_dealers):
                self.f_sem.acquire()
                self.cars.put(None)
                self.d_sem.release()



class Dealer(threading.Thread):
    """ This is a dealer that receives cars """

    def __init__(self, cars_to_produce_sem, cars_to_sell_sem, car_queue, pid):
        # All of the data that 1 Dealer needs to sell a car.
        super().__init__()
        self.f_sem = cars_to_produce_sem
        self.d_sem = cars_to_sell_sem
        self.cars = car_queue
        self.pid = pid
        self.cars_processed = 0

    def run(self):
        while True:
            """
            take the car from the queue
            signal the factory that there is an empty slot in the queue
            """
            self.d_sem.acquire()
            car = self.cars.get()
            if car == None:
                break
            self.cars_processed += 1
            self.f_sem.release()

            # Sleep a little - don't change.  This is the last line of the loop.
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR + 0))



def run_production(factory_count, dealer_count):
    """ This function will do a production run with the number of
        factories and dealerships passed in as arguments.
    """

    # Create semaphore(s) if needed.
    cars_to_produce_sem = threading.Semaphore(MAX_QUEUE_SIZE)
    cars_to_sell_sem = threading.Semaphore(0)

    # Create queue.
    car_queue = Queue251()
    
    # Create barrier.
    finished_producing_barrier = threading.Barrier(factory_count)

    # Create your factories, each factory will create a random amount of cars; your code must account for this.
    # You have no control over how many cars a factory will create in this assignment.
    factories = []
    for i in range(factory_count):
        factories.append(Factory(cars_to_produce_sem, cars_to_sell_sem, car_queue, finished_producing_barrier, dealer_count))

    # Create your dealerships.
    dealerships = []
    for i in range(dealer_count):
        dealerships.append(Dealer(cars_to_produce_sem, cars_to_sell_sem, car_queue, i+1))

    log.start_timer()

    # Start all factories.
    for factory in factories:
        factory.start()

    # Start all dealerships.
    for dealer in dealerships:
        dealer.start()

    # This is used to track the number of cars produced by each factory. DO NOT pass this into
    # your factories! You must collect this data here in `run_production` after the factories are finished.
    factory_stats = []
    dealer_stats = []

    # Wait for the factories and dealerships to complete; do not forget to get the factories stats.
    for factory in factories:
        factory.join()
        factory_stats.append(factory.cars_produced)

    for dealer in dealerships:
        dealer.join()
        dealer_stats.append(dealer.cars_processed)

    run_time = log.stop_timer(f'{sum(dealer_stats)} cars have been created.')

    # This function must return the following - Don't change!
    # factory_stats: is a list of the number of cars produced by each factory.
    #                collect this information after the factories are finished. 
    return (run_time, car_queue.get_max_size(), dealer_stats, factory_stats)


def main(log):
    """ Main function - DO NOT CHANGE! """

    runs = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 5), (5, 2), (10, 10)]
    for factories, dealerships in runs:
        run_time, max_queue_size, dealer_stats, factory_stats = run_production(factories, dealerships)

        log.write(f'Factories      : {factories}')
        log.write(f'Dealerships    : {dealerships}')
        log.write(f'Run Time       : {run_time:.4f}')
        log.write(f'Max queue size : {max_queue_size}')
        log.write(f'Factory Stats  : Made = {sum(dealer_stats)} @ {factory_stats}')
        log.write(f'Dealer Stats   : Sold = {sum(factory_stats)} @ {dealer_stats}')
        log.write('')

        # The number of cars produced needs to match the cars sold.
        assert sum(dealer_stats) == sum(factory_stats)


if __name__ == '__main__':
    log = Log(show_terminal=True)
    main(log)

