"""
Course: CSE 251 
Lesson: L04 Prove
File:   prove.py
Author: <Add name here>

Purpose: Assignment 04 - Factory and Dealership

Instructions:

- Complete the assignments TODO sections and DO NOT edit parts you were told to leave alone.
- Review the full instructions in Canvas; there are a lot of DO NOTS in this lesson.
"""

import time
import threading
import random

# Include cse 251 common Python files
from cse251 import *

# Global Constants - DO NOT CHANGE
CARS_TO_PRODUCE = 500
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 50

# NO GLOBAL VARIABLES!

class Car():
    """ This is the Car class that will be created by the factories """

    # Class Variables
    car_makes = ('Ford', 'Chevrolet', 'Dodge', 'Fiat', 'Volvo', 'Infiniti', 'Jeep', 'Subaru', 
                'Buick', 'Volkswagen', 'Chrysler', 'Smart', 'Nissan', 'Toyota', 'Lexus', 
                'Mitsubishi', 'Mazda', 'Hyundai', 'Kia', 'Acura', 'Honda')

    car_models = ('A1', 'M1', 'XOX', 'XL', 'XLS', 'XLE' ,'Super' ,'Tall' ,'Flat', 'Middle', 'Round',
                'A2', 'M1X', 'SE', 'SXE', 'MM', 'Charger', 'Grand', 'Viper', 'F150', 'Town', 'Ranger',
                'G35', 'Titan', 'M5', 'GX', 'Sport', 'RX')

    car_years = [i for i in range(1990, datetime.now().year)]

    def __init__(self):
        # Make a random car
        self.model = random.choice(Car.car_models)
        self.make = random.choice(Car.car_makes)
        self.year = random.choice(Car.car_years)

        # Sleep a little.  Last statement in this for loop - don't change
        time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))

        # Display the car that has was just created in the terminal
        # print(f'Created: {self.info()}')
           
    def info(self):
        """ Helper function to quickly get the car information. """
        return f'{self.make} {self.model}, {self.year}'


class Queue251():
    """ This is the queue object to use for this assignment. Do not modify!! """

    def __init__(self):
        self.items = []

    def size(self):
        return len(self.items)

    def put(self, item):
        assert len(self.items) <= 10
        self.items.append(item)

    def get(self):
        return self.items.pop(0)


class Factory(threading.Thread):
    """ This is a factory.  It will create cars and place them on the car queue """

    def __init__(self, f_sem, d_sem, cars, log):
        # all of data that 1 factory needs
        # to create cars and to place them in a queue.
        super().__init__()
        self.f_sem = f_sem
        self.d_sem = d_sem
        self.cars = cars
        self.log = log

    def run(self):
        for i in range(CARS_TO_PRODUCE):
            """
            create a car
            place the car on the queue
            signal the dealer that there is a car on the queue
           """
            self.f_sem.acquire()
            car = Car()
            self.cars.put(car)
            self.log.write(f'Factory created: {car.info()}')
            self.d_sem.release()

        # signal the dealer that there there are not more cars
        self.cars.put('ALL_CARS_PRODUCED')
        self.d_sem.release()


class Dealer(threading.Thread):
    """ This is a dealer that receives cars """

    def __init__(self, f_sem, d_sem, cars, log, queue_stats):
        # all of data that 1 Dealer needs to sell a car
        super().__init__()
        self.f_sem = f_sem
        self.d_sem = d_sem
        self.cars = cars
        self.log = log
        self.stats = queue_stats

    def run(self):
        while True:
            """
            take the car from the queue
            signal the factory that there is an empty slot in the queue
            """
            self.d_sem.acquire()
            car = self.cars.get()
            if car == 'ALL_CARS_PRODUCED':
                break
            else:
                self.stats[self.cars.size()] += 1
                self.log.write(f'Dealership sold: {car.info()}')
                self.f_sem.release()

            # Sleep a little after selling a car
            # Last statement in this for loop - don't change
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))



def main():
    log = Log(show_terminal=True)

    # Create semaphore(s)
    f_sem = threading.Semaphore(10)
    d_sem = threading.Semaphore(0)
    # Create queue251 
    cars = Queue251()

    # This tracks the length of the car queue during receiving cars by the dealership
    # i.e., update this list each time the dealer receives a car
    queue_stats = [0] * MAX_QUEUE_SIZE
    # print(queue_stats)

    # Create one factory
    factory = Factory(f_sem, d_sem, cars, log)

    # Create one dealership
    dealership = Dealer(f_sem, d_sem, cars, log, queue_stats)

    log.start_timer()

    # Start factory and dealership
    factory.start()
    dealership.start()

    # Wait for factory and dealership to complete
    factory.join()
    dealership.join()

    log.stop_timer(f'All {sum(queue_stats)} have been created')

    xaxis = [i for i in range(1, MAX_QUEUE_SIZE + 1)]
    plot = Plots()
    plot.bar(xaxis, queue_stats, title=f'{sum(queue_stats)} Produced: Count VS Queue Size', x_label='Queue Size', y_label='Count', filename='Production count vs queue size.png')



if __name__ == '__main__':
    main()