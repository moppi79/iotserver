import os, time, sys
import RPi.GPIO as GPIO
test = {}
test['aa'] = 111

print (test.get('bb', 'bb ist nicht da'))

print (test.get('aa', 'bb ist nicht da'))