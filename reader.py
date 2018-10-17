#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import hashlib

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.IN, GPIO.PUD_DOWN)

data_period = 1.0

def complete_sync():
  # wait for sync blcok to finish
  while True:
    if GPIO.input(18) == 0:
      print ( "sync done" )
      check_start()
    time.sleep(data_period/10)

def check_start():
  print( "waiting for start character" )
  while True:
    if GPIO.input(18) == 1:
      # the controller is sending in 10ms waves, so we want to be 5ms out of sync to land in the middle
      print( "sync done, waiting 5ms for start message" )
      print (time.time())
      time.sleep(data_period/2)

      start_message = []
      # Grab 4 characters and make sure they're FEFF
      for x in range(0, 16):
        time.sleep(data_period)
        start_message.append(GPIO.input(18))
#        print( start_message[-1] )

      # Check if we have a proper start message, if so start reading data
      if ( "".join(map(str,start_message)) == format(int("0xFEFF", 0), 'b')):
        print ( "start message found" )
        print ( "".join(map(str,start_message)) )
        read_message()

      #got something other than start message
      else:
        print ( "invalid start message" )
        print ( "".join(map(str,start_message)) )
        wait_sync()

    time.sleep(data_period/10)

def read_sync(announce_start):
  while True:
    if ( (time.time() - .50) > announce_start ):
      print ("signal too long for announcement, returning to wait")
      wait_announcement()
    if ( GPIO.input(18) == 0 ):
      print ( "annoncement done, waiting for clock signal" )
      while True:
        if ( (time.time() - 1.0) > announce_start ):
          print ("signal nevver came, returning to wait")
          wait_announcement()
        if ( GPIO.input(18) == 1 ):
          print ("start clock sync")
          sync_clock()

def sync_clock():
  clock_times = []
  current_state = 1
  last_change = time.time()
  while True:
    if not ( GPIO.input(18) == current_state ):
      current_state = GPIO.input(18)
      cur_time = time.time()
      clock_times.append( cur_time - last_change )
      last_change = cur_time
    if ( len(clock_times) == 9 ):
      average_pulse = sum(clock_times)/len(clock_times)
      print ("sync found, average pulse length = {:f}".format(( average_pulse ) ) )
      time.sleep( average_pulse )
      read_message(average_pulse)
    if ( time.time() > ( last_change + 30 ) ):
      print ("failed to sync to master clock")
      wait_announcement()

def read_message(average_pulse):

  # move read to middle of pulse
  time.sleep( average_pulse/2 )

  start_message = []
  received_message = []
  # read start message
  for x in range(0, 16):
    time.sleep( average_pulse )
    start_message.append( GPIO.input(18) )

  if not ( start_message == [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1] ):
    print ( "invalid message" )
    wait_announcement()

  print ("start message found, deconding")
  while True:
    current_character = []
    for x in range(0, 16):
      time.sleep( average_pulse )
      current_character.append( GPIO.input(18) )

   # print ( current_character )
    if ( current_character == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0] ):
      print ( "message complete" )
      run_command(received_message)
    received_message.append( chr(int(''.join(map(str,current_character)), 2 ) ) )
    print(chr(int(''.join(map(str,current_character)), 2 ) ) )
  exit()

def run_command(received_message):
  print (''.join(received_message) )
  wait_announcement()

def wait_announcement():
  print ("waiting for announcement")
  print (time.time())
  sync_counter = 0
  sync_good = 64
  while True:
    if GPIO.input(18) == 1:
      print ("Signal detected")
      announce_start = time.time()
      while True:
        if ( (time.time() - .20) > announce_start ):
          print ("announcement found")
          read_sync(announce_start)
        if GPIO.input(18) == 0:
          print ("not an announcement, returning to wait")
          break

wait_announcement()
