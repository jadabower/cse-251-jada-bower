"""
Course: CSE 251 
Lesson: L02 Team Activity
File:   team.py
Author: <Add name here>

Purpose: Make threaded API calls with the Playing Card API http://deckofcardsapi.com

Instructions:

- Review instructions in Canvas.
"""

"""
Deck created:

{
  "success": true,
  "deck_id": "9k8oo2t3qi59",
  "remaining": 52,
  "shuffled": false
}
9k8oo2t3qi59
"""

from datetime import datetime, timedelta
import threading
import requests
import json

# Include cse 251 common Python files
from cse251 import *

class Request_thread(threading.Thread):
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.response = {}
        self.status_code = {}

    def run(self):
        response = requests.get(self.url)
        # Check the status code to see if the request succeeded.
        self.status_code = response.status_code
        if response.status_code == 200:
            self.response = response.json()
        else:
            print('RESPONSE = ', response.status_code)

    # def run(self):
    #     response = requests.get(self.url)
    #     if response:
    #         self.response = response
    #     else:
    #         print('Error')
    #         return False

class Deck:

    def __init__(self, deck_id):
        self.id = deck_id
        self.reshuffle()
        self.remaining = 52

    def reshuffle(self):
        print('Reshuffle Deck')
        t = Request_thread(f'https://deckofcardsapi.com/api/deck/{self.id}/shuffle/')
        t.start()
        t.join()

    def draw_card(self):
        card_thread = Request_thread(f'https://deckofcardsapi.com/api/deck/{self.id}/draw/?count=1')
        card_thread.start()
        card_thread.join()
        if card_thread.status_code == 200 and card_thread.response != {}:
            self.remaining = card_thread.response['remaining']
            return card_thread.response['cards'][0]['code']
        else:
            return ''

    def cards_remaining(self):
        return self.remaining

    def draw_endless(self):
        if self.remaining <= 0:
            self.reshuffle()
        return self.draw_card()


if __name__ == '__main__':

    deck_id = 'ph7jfurkyqsa'

    # Testing Code >>>>>
    deck = Deck(deck_id)

    for i in range(55):
        card = deck.draw_endless()
        print(f'card {i + 1}: {card}', flush=True)
    print()
    # <<<<<<<<<<<<<<<<<<
