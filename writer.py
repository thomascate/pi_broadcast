#!/usr/bin/env python3
import sys
import time
import RPi.GPIO as GPIO
import hashlib

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(16, GPIO.OUT, initial = 0)
data_period = 0.1

#GPIO.output(16, 0)
#exit()


input_string = sys.argv[1]
output_binary = []
output_binary.append(format(int("0xFEFF", 0), 'b'))

for character in list(input_string):
  binary_char = format(ord(character), 'b')
  utf_16_bchar = ""
  if len(binary_char) < 16:
    for x in range(0, 16 - len(binary_char)):
      utf_16_bchar+=("0")
  utf_16_bchar+=(binary_char)
  output_binary.append(utf_16_bchar)

#output_binary = output_binary[0]
output_binary.append(format(int("0xFFFE", 0), 'b'))

#send listen signal
print (time.time())
GPIO.output(16, 1)
time.sleep(0.25)

#clear signal
print (time.time())
GPIO.output(16, 0)
time.sleep(0.25)

#send clock pattern
for X in range(0, 5):
  GPIO.output(16,1)
  time.sleep(data_period)
  GPIO.output(16,0)
  time.sleep(data_period)

print (output_binary)
for character in output_binary:
  for bit in list(character):

    time.sleep(data_period)
    if bit=="1":
      GPIO.output(16, 1)
    if bit=="0":
      GPIO.output(16, 0)

  print (type(character))
  print (character)
  print(chr(int(character, 2)))
  print (time.time())
exit()