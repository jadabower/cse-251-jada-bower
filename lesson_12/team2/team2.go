/* ---------------------------------------
Course: CSE 251
Lesson Week: ?12
File: team.go
Author: Brother Comeau

Purpose: team activity - finding primes

Instructions:

- Process the array of numbers, find the prime numbers using goroutines

worker()

This goroutine will take in a list/array/channel of numbers.  It will place
prime numbers on another channel

readValue()

This goroutine will display the contents of the channel containing
the prime numbers

--------------------------------------- */
package main

import (
  "fmt"
  "math/rand"
  "time"
  "sync"
)

func isPrime(n int) bool {
  // Primality test using 6k+-1 optimization.
  // From: https://en.wikipedia.org/wiki/Primality_test

  if n <= 3 {
    return n > 1
  }

  if n%2 == 0 || n%3 == 0 {
    return false
  }

  i := 5
  for (i * i) <= n {
    if n%i == 0 || n%(i+2) == 0 {
      return false
    }
    i += 6
  }
  return true
}

func worker(receive_from_ch chan int, send_to_ch chan int, wg *sync.WaitGroup, chunk_to_process int) {
  // Process numbers on one channel and place prime number on another
  for i := 0; i < chunk_to_process; i++ {
    possible_prime := <- receive_from_ch
    if isPrime(possible_prime) {
      send_to_ch <- possible_prime
    }
  }
  wg.Done()
}

func readValues(send_to_ch chan int, wg *sync.WaitGroup) {
  // Display prime numbers from a channel
  valuesToGet := true
  for valuesToGet {
      prime := <- send_to_ch
      if prime == -1 {
          valuesToGet = false
      } else {
          fmt.Println("Prime: ", prime)
      }
  }
  wg.Done()
}

func main() {

  workers := 10
  numberValues := 100

  // Create any channels that you need
  receive_from_ch := make(chan int)
  send_to_ch := make(chan int)
  
  // Create any other "things" that you need to get the workers to finish(join)
  var wg sync.WaitGroup
  wg.Add(workers + 1)

  // create workers
  chunk_per_worker := numberValues / workers
  for w := 1; w <= workers; w++ {
    go worker(receive_from_ch, send_to_ch, &wg, chunk_per_worker)
  }

  randSource := rand.NewSource(time.Now().UnixNano())
  randGenerator := rand.New(randSource)
  
  go readValues(send_to_ch, &wg)
  
  // rand.Seed(time.Now().UnixNano())
  for i := 0; i < numberValues; i++ {
    receive_from_ch <- randGenerator.Int()
  }

  send_to_ch <- -1
  
  wg.Wait()
  
  close(receive_from_ch)
  close(send_to_ch)

  fmt.Println("All Done!")
}
