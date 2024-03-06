"""
Course: CSE 251 
Lesson: L09 Team Part 1
File:   team_part_1.py
Author: <Add name here>

Purpose: Solve the Dining philosophers problem to practice skills you have learned so far in this course.

Problem Statement:

Five silent philosophers sit at a round table with bowls of spaghetti. Forks
are placed between each pair of adjacent philosophers.

Each philosopher must alternately think and eat. However, a philosopher can
only eat spaghetti when they have both left and right forks. Each fork can be
held by only one philosopher and so a philosopher can use the fork only if it
is not being used by another philosopher. After an individual philosopher
finishes eating, they need to put down both forks so that the forks become
available to others. A philosopher can only take the fork on their right or
the one on their left as they become available and they cannot start eating
before getting both forks.  When a philosopher is finished eating, they think 
for a little while.

Eating is not limited by the remaining amounts of spaghetti or stomach space;
an infinite supply and an infinite demand are assumed.

The problem is how to design a discipline of behavior (a concurrent algorithm)
such that no philosopher will starve

Instructions:

        ****************************************************************
        ** DO NOT search for a solution on the Internet! Your goal is **
        ** not to copy a solution, but to work out this problem using **
        ** the skills you have learned so far in this course.         **
        ****************************************************************

Requirements you must Implement:

- Use threads for this problem.
- Start with the PHILOSOPHERS being set to 5.
- Philosophers need to eat for a random amount of time, between 1 to 3 seconds, when they get both forks.
- Philosophers need to think for a random amount of time, between 1 to 3 seconds, when they are finished eating.
- You want as many philosophers to eat and think concurrently as possible without violating any rules.
- When the number of philosophers has eaten a combined total of MAX_MEALS_EATEN times, stop the
  philosophers from trying to eat; any philosophers already eating will put down their forks when they finish eating.
    - MAX_MEALS_EATEN = PHILOSOPHERS x 5

Suggestions and team Discussion:

- You have Locks and Semaphores that you can use:
    - Remember that lock.acquire() has arguments that may be useful: `blocking` and `timeout`.  
- Design your program to handle N philosophers and N forks after you get it working for 5.
- When you get your program working, how to you prove that no philosopher will starve?
  (Just looking at output from print() statements is not enough!)
- Are the philosophers each eating and thinking the same amount?
    - Modify your code to track how much each philosopher is eating.
- Using lists for the philosophers and forks will help you in this program. For example:
  philosophers[i] needs forks[i] and forks[i+1] to eat (the % operator helps).
"""

import time
import random
import threading

PHILOSOPHERS = 5
MAX_MEALS_EATEN = PHILOSOPHERS * 5 # NOTE: Total meals to be eaten, not per philosopher!

class Philosopher(threading.Thread):
    def __init__(self, index, left_fork, right_fork, meals_to_eat_lock):
        super().__init__()
        self.pid = index + 1
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.meals_to_eat_lock = meals_to_eat_lock
        self.meals_eaten = 0

    def run(self):
      while self._should_eat():
        # Try to acquire the fork on the left.
        if self.left_fork.acquire():
          # If we acquired the left fork, try to acquire the right fork.
          if self.right_fork.acquire():
            # We acquired both forks, so eat, put down the forks and ponder.
            self._eat()
            self.left_fork.release()
            self.right_fork.release()
            self._ponder()
          else:
            # We acquired the left fork but not the right one, so release the left one and try again.
            self.left_fork.release()
        elif self.right_fork.acquire():
          # If we acquired the right fork, try to acquire the left fork.
          if self.left_fork.acquire():
            # We acquired both forks, so eat, put down the forks and ponder.
            self._eat()
            self.right_fork.release()
            self.left_fork.release()
            self._ponder()
          else:
            # We acquired the right fork but not the left one, so release the right one and try again.
            self.right_fork.release()

    def _should_eat(self):
      # Check that we have not passed the threshold of meals to eat
      return_val = False
      with self.meals_to_eat_lock:
        global meals_to_eat
        if meals_to_eat <= 0:
          return_val = False
        else:
          meals_to_eat -= 1
          self.meals_eaten += 1
          return_val = True
      return return_val

    def _eat(self):
      # Eat for 1-3 seconds
      eat_time = random.uniform(1.0, 3.0)
      time.sleep(eat_time)
      print(f'Philosopher {self.pid} is eating for {eat_time} seconds')

    def _ponder(self):
      # Think for 1-3 seconds
      think_time = random.uniform(1.0, 3.0)
      time.sleep(think_time)
      print(f'Philosopher {self.pid} is thinking for {think_time} seconds')



def main():
    global meals_to_eat
    meals_to_eat = MAX_MEALS_EATEN
    meals_to_eat_lock = threading.Lock()

    # Create the forks.
    forks = []
    for _ in range(PHILOSOPHERS):
        forks.append(threading.Lock())

    # Create PHILOSOPHERS philosophers.
    philosophers = []
    for i in range(PHILOSOPHERS):
      left_fork_index = i
      right_fork_index = (i + 1) % PHILOSOPHERS
      philosophers.append(Philosopher(i, forks[left_fork_index], forks[right_fork_index], meals_to_eat_lock))

    # Start them eating and thinking.
    for philosopher in philosophers:
      philosopher.start()

    # Wait for them to finish.
    for philosopher in philosophers:
      philosopher.join()

    # Display how many times each philosopher ate.
    for philosopher in philosophers:
      print(f'Philosopher {philosopher.pid} ate {philosopher.meals_eaten}')


if __name__ == '__main__':
    main()