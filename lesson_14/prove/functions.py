"""
Course: CSE 251, week 14
File: functions.py
Author: Jada Bower

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
request = Request_thread(f'{TOP_API_URL}/family/{id}')
request.start()
request.join()

Example JSON returned from the server
{
    'id': 6128784944, 
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
request = Request_thread(f'{TOP_API_URL}/person/{id}')
request.start()
request.join()

Example JSON returned from the server
{
    'id': 2373686152, 
    'name': 'Stella', 
    'birth': '9-3-1846', 
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}

You will lose 10% if you don't detail your part 1 and part 2 code below

Describe how to speed up part 1

<Add your comments here>

Describe how to speed up part 2

<Add your comments here>

Extra (Optional) 10% Bonus to speed up part 3

<Add your comments here>

"""
from common import *
import queue

# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree):
    # KEEP this function even if you don't implement it
    # TODO - Implement depth first retrieval
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    def process_one_family(family_id):
        
        nonlocal tree

        req_family = Request_thread(f'{TOP_API_URL}/family/{family_id}')
        req_family.start()
        req_family.join()

        new_family = Family(req_family.get_response())
        tree.add_family(new_family)

        husband = None
        wife = None

        # Get husband details
        husband_id = new_family.get_husband()
        # print(f'    Retrieving Husband : {husband_id}')
        req_person1 = Request_thread(f'{TOP_API_URL}/person/{husband_id}')
        req_person1.start()

        # Get wife details
        wife_id = new_family.get_wife()
        # print(f'    Retrieving Wife : {wife_id}')
        req_person2 = Request_thread(f'{TOP_API_URL}/person/{wife_id}')
        req_person2.start()
        
        # Retrieve children
        # print(f'    Retrieving Children : {str(new_family.get_children())[1:-1]}')
        children = []
        children_threads = []
        for child_id in new_family.get_children():
            # Don't request a person if that person is in the tree already
            if not tree.does_person_exist(child_id):
                req_child =  Request_thread(f'{TOP_API_URL}/person/{child_id}')
                children_threads.append(req_child)

        for child in children_threads:
            child.start()

        for child in children_threads:
            child.join()

        for child in children_threads:
            child_person = Person(child.get_response())
            children.append(child_person)
        
        req_person1.join()
        req_person2.join()

        husband = Person(req_person1.get_response())
        wife = Person(req_person2.get_response())

        tree.add_person(husband)
        tree.add_person(wife)
        for c in children:
            tree.add_person(c)

        # Add the husband's parent's family to the queue
        husband_family = husband.get_parentid()
        if husband_family != None:
            if not tree.does_family_exist(husband_family):
                process_one_family(husband_family)
        
        # Add the wife's parent's family to the queue
        wife_family = wife.get_parentid()
        if wife_family != None:
            if not tree.does_family_exist(wife_family):
                process_one_family(wife_family)

    process_one_family(family_id)

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(family_id, tree):
    # KEEP this function even if you don't implement it
    #      - Implement breadth first retrieval
    #      - Printing out people and families that are retrieved from the server will help debugging
    family_queue = queue.Queue()
    family_queue.put(family_id)

    def process_one_family(family_id):
        
        nonlocal tree
        nonlocal family_queue

        req_family = Request_thread(f'{TOP_API_URL}/family/{family_id}')
        req_family.start()
        req_family.join()

        new_family = Family(req_family.get_response())
        tree.add_family(new_family)

        husband = None
        wife = None

        # Get husband details
        husband_id = new_family.get_husband()
        # print(f'    Retrieving Husband : {husband_id}')
        req_person1 = Request_thread(f'{TOP_API_URL}/person/{husband_id}')
        req_person1.start()

        # Get wife details
        wife_id = new_family.get_wife()
        # print(f'    Retrieving Wife : {wife_id}')
        req_person2 = Request_thread(f'{TOP_API_URL}/person/{wife_id}')
        req_person2.start()
        
        # Retrieve children
        # print(f'    Retrieving Children : {str(new_family.get_children())[1:-1]}')
        children = []
        children_threads = []
        for child_id in new_family.get_children():
            # Don't request a person if that person is in the tree already
            if not tree.does_person_exist(child_id):
                req_child =  Request_thread(f'{TOP_API_URL}/person/{child_id}')
                children_threads.append(req_child)

        for child in children_threads:
            child.start()

        for child in children_threads:
            child.join()

        for child in children_threads:
            child_person = Person(child.get_response())
            children.append(child_person)
        
        req_person1.join()
        req_person2.join()

        husband = Person(req_person1.get_response())
        wife = Person(req_person2.get_response())

        tree.add_person(husband)
        tree.add_person(wife)
        for c in children:
            tree.add_person(c)

        # Add the husband's parent's family to the queue
        husband_family = husband.get_parentid()
        if husband_family != None:
            if not tree.does_family_exist(husband_family):
                family_queue.put(husband_family)
        
        # Add the wife's parent's family to the queue
        wife_family = wife.get_parentid()
        if not tree.does_family_exist(wife_family):
            family_queue.put(wife_family)

    next_to_process = family_queue.get()
    while next_to_process != None:
        process_one_family(next_to_process)
        next_to_process = family_queue.get()
# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree):
    # KEEP this function even if you don't implement it
    #      - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5
    #      - Printing out people and families that are retrieved from the server will help debugging
    # KEEP this function even if you don't implement it
    # Implement breadth first retrieval
    # Printing out people and families that are retrieved from the server will help debugging
    family_queue = queue.Queue()
    family_queue.put(family_id)
    max_threads_sem = threading.Semaphore(5)

    def process_one_family(family_id, sem):
        
        nonlocal tree
        nonlocal family_queue

        sem.acquire()
        req_family = Request_thread(f'{TOP_API_URL}/family/{family_id}')
        req_family.start()
        req_family.join()
        sem.release()

        new_family = Family(req_family.get_response())
        tree.add_family(new_family)

        husband = None
        wife = None

        # Get husband details
        husband_id = new_family.get_husband()
        # print(f'    Retrieving Husband : {husband_id}')
        sem.acquire()
        req_person1 = Request_thread(f'{TOP_API_URL}/person/{husband_id}')
        req_person1.start()

        # Get wife details
        wife_id = new_family.get_wife()
        # print(f'    Retrieving Wife : {wife_id}')
        sem.acquire()
        req_person2 = Request_thread(f'{TOP_API_URL}/person/{wife_id}')
        req_person2.start()
        
        # Retrieve children
        # print(f'    Retrieving Children : {str(new_family.get_children())[1:-1]}')
        children = []
        children_arrays = []
        
        # Split the children to chunks of 3 so we don't have too many threads going at once
        children_to_process = new_family.get_children()

        while len(children_to_process) > 3:
            children_arrays.append([children_to_process.pop(), children_to_process.pop(), children_to_process.pop()])
        if len(children_to_process) > 0:
            children_arrays.append(children_to_process)

        for children_array in children_arrays:
            children_threads = []
            for child_id in children_array:

                # Don't request a person if that person is in the tree already
                if not tree.does_person_exist(child_id):
                    sem.acquire()
                    req_child =  Request_thread(f'{TOP_API_URL}/person/{child_id}')
                    children_threads.append(req_child)

            for child in children_threads:
                child.start()

            for child in children_threads:
                child.join()
                sem.release()

            for child in children_threads:
                child_person = Person(child.get_response())
                children.append(child_person)
        
        req_person1.join()
        sem.release()
        req_person2.join()
        sem.release()

        husband = Person(req_person1.get_response())
        wife = Person(req_person2.get_response())

        tree.add_person(husband)
        tree.add_person(wife)
        for c in children:
            tree.add_person(c)

        # Add the husband's parent's family to the queue
        husband_family = husband.get_parentid()
        if husband_family != None:
            if not tree.does_family_exist(husband_family):
                family_queue.put(husband_family)
        
        # Add the wife's parent's family to the queue
        wife_family = wife.get_parentid()
        if not tree.does_family_exist(wife_family):
            family_queue.put(wife_family)

    next_to_process = family_queue.get()
    while next_to_process != None:
        process_one_family(next_to_process, max_threads_sem)
        next_to_process = family_queue.get()
