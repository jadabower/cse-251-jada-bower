import multiprocessing

def worker(num, callback):
  """Worker function that prints the given number and calls the given callback function with the number."""
  print('Worker:', num)
  return num

def callback(num):
  """Callback function that simply prints the given number."""
  print('Callback:', num)

def main():
  """Main function that creates an asynchronous pool and submits 10 tasks to it. The main function then waits for all of the tasks to finish executing before exiting."""
  p = multiprocessing.Pool(5)
  for i in range(10):
    p.apply_async(worker, (i, callback))

  # Close the pool to prevent any further tasks from being executed.
  p.close()

  # Wait for all of the tasks to finish executing.
  p.join()

if __name__ == '__main__':
  main()
