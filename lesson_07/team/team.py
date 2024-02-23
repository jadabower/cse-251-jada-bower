
"""
Course: CSE 251 
Lesson: L07 Team
File:   prove.py
Author: Jada Bower

Purpose: Retrieve Star Wars details from a server
"""

"""
Instructions:

1) Make a copy of your lesson 2 prove assignment. Since you are  working in a team for this
   assignment, you can decide which assignment 2 program that you will use for the team activity.

2) You can continue to use the Request_Thread() class that makes the call to the server.

3) Convert the program to use a process pool that uses apply_async() with callback function(s) to
   retrieve data from the Star Wars website. Each request for data must be an apply_async() call;
   this means 1 url = 1 apply_async call, 94 urls = 94 apply_async calls.
"""
"""
Week 2 Instructions:

- Each API call must only retrieve one piece of information
- You are not allowed to use any other modules/packages except for the ones used
  in this assignment.
- Run the server.py program from a terminal/console program.  Simply type
  "python server.py"
- The only "fixed" or hard coded URL that you can use is TOP_API_URL.  Use this
  URL to retrieve other URLs that you can use to retrieve information from the
  server.
- You need to match the output outlined in the description of the assignment.
  Note that the names are sorted.
- You are required to use a threaded class (inherited from threading.Thread) for
  this assignment. This object will make the API calls to the server. You can
  define your class within this Python file (ie., no need to have a separate
  file for the class)
- Do not add any global variables except for the ones included in this program.

The call to TOP_API_URL will return the following Dictionary(JSON).  Do NOT have
this dictionary hard coded - use the API call to get this.  Then you can use
this dictionary to make other API calls for data.

{
   "people": "http://127.0.0.1:8790/people/", 
   "planets": "http://127.0.0.1:8790/planets/", 
   "films": "http://127.0.0.1:8790/films/",
   "species": "http://127.0.0.1:8790/species/", 
   "vehicles": "http://127.0.0.1:8790/vehicles/", 
   "starships": "http://127.0.0.1:8790/starships/"
}
"""

from datetime import datetime, timedelta
import requests
import json
import threading
import multiprocessing as mp
import os

# Include cse 251 common Python files
from cse251 import *

# Const Values
TOP_API_URL = 'http://127.0.0.1:8790'

# Global Variables
call_count = 0
data = []

def make_call(url):
    # Make a request to the users url
    response = requests.get(url)
    # If the API call succeeded call the callback function
    if response.status_code == 200:
        return response.json()

def callback_fun(response):
    global call_count
    global data
    # Update our global counter to track how many requests we make
    call_count += 1
    data.append(response)
    return data

def get_all_data(urls):
    global data
    data = []
    p = mp.Pool(os.cpu_count())
    for url in urls:
        p.apply_async(make_call, args=(url,), callback=callback_fun)
    # Close the pool to prevent any further tasks from being executed.
    p.close()
    # Wait for all of the tasks to finish executing.
    p.join()
    return data

def print_film_details(log, film, chars, planets, starships, vehicles, species):

    def display_names(title, name_list):
        log.write('')
        log.write(f'{title}: {len(name_list)}')
        names = sorted([item["name"] for item in name_list])
        log.write(str(names)[1:-1].replace("'", ""))


    log.write('-' * 40)
    log.write(f'Title   : {film["title"]}')
    log.write(f'Director: {film["director"]}')
    log.write(f'Producer: {film["producer"]}')
    log.write(f'Released: {film["release_date"]}')

    display_names('Characters', chars)
    display_names('Planets', planets)
    display_names('Starships', starships)
    display_names('Vehicles', vehicles)
    display_names('Species', species)


def main():
    log = Log(show_terminal=True, filename_log='lesson-2-prove.log')
    log.start_timer('Starting to retrieve data from the server')

    # MY CODE START >>>

    # DONE: Retrieve top API urls
    data = get_all_data([TOP_API_URL])

    # DONE: Retrieve top level data urls
    routes = data[0]
    films = routes['films']

    # Request film 6 details
    data = get_all_data([f'{films}6'])

    # Get film 6 top level urls
    film_6 = data[0]

    # DONE: Retrieve details (actual data) of film 6
    characters = get_all_data(film_6['characters'])
    planets = get_all_data(film_6['planets'])
    starships = get_all_data(film_6['starships'])
    vehicles = get_all_data(film_6['vehicles'])
    species = get_all_data(film_6['species'])

    # DONE: Display results
    print_film_details(log, film_6, characters, planets, starships, vehicles, species)

    # <<< MY CODE END

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')
    

if __name__ == "__main__":
    main()


