#!/usr/bin/python

'''
This script runs the autoTestingScript_lag.py script with differing amounts of lag
    Differing amounts of lag are between 40 and 640, step starts at 80 then doubles each run until hitting 640
'''

import subprocess
import time
import sys
import winsound

# Script Process
script = None  # Holds process that runs the autoTestingScript_lag.py script

# Parameters (for this script)
pythonPath = 'A:\python\python.exe'
lagTestScriptName = 'autoTestingScript_lag.py'
minLag = 160  # Minimum lag to test bot (in milliseconds)
maxLag = 640  # Maximum lag to test bot (in milliseconds)
lagStep = minLag  # How much to decrement lag by each step (test run) (in milliseconds)

# Parameters (for autoTestingScript_lag.py)
mapID = 7  # map ID of tests
numBotsForAutoStart = 3  # Number of Bots to spawn, one will be lagged
lagCompensation = 't'  # Whether or not the lagged bot will be using lagCompensation
lagInMS = minLag  # How much latency will the lagged bot be under in milliseconds
numOfTest = 30  # How many tests to run using these parameters before terminating
maxTestTime = 120  # Maximum time (in seconds) allowed for test before killing the test (in case something goes wrong)

# Parse command line (if given)
# Script parameters: pythonPath numBotsForAutoStart minLag maxLag lagStep numOfTest maxTestTime
if len(sys.argv) == 8:
    pythonPath = sys.argv[1]
    numBotsForAutoStart = int(sys.argv[2])
    minLag = int(sys.argv[3])
    maxLag = int(sys.argv[4])
    lagStep = int(sys.argv[5])
    numOfTest = int(sys.argv[6])
    maxTestTime = int(sys.argv[7])

# Print parameters
print('pythonPath: ' + pythonPath)
print('numBotsForAutoStart: ' + str(numBotsForAutoStart))
print('minLag: ' + str(minLag))
print('maxLag: ' + str(maxLag))
print('lagStep: ' + str(lagStep))
print('numOfTest: ' + str(numOfTest))
print('maxTestTime: ' + str(maxTestTime) + '\n')

# Current lag used in current test (for one bot)
currLag = minLag

# Command used
cmd = pythonPath + ' ' + lagTestScriptName + ' ' + str(mapID) + ' ' + str(numBotsForAutoStart) + ' ' + str(
    lagCompensation) + ' ' + str(currLag) + ' ' + str(numOfTest) + ' ' + str(maxTestTime)
print('Command: ' + cmd)

# Call command
for run in range(2):  # Run twice, once with lag compensation at all lag values, once with lag compensation off
    while True:
        time.sleep(1)  # No need to poll immediately, so wait a bit

        if script is None or script.poll() is not None:  # Start another test, but decrement lag given to bot by step
            # Script parameters: numBotsForAutoStart lagCompensation lagInMS numOfTest maxTestTime
            cmd = pythonPath + ' ' + lagTestScriptName + ' ' + str(numBotsForAutoStart) + ' ' + str(
                lagCompensation) + ' ' + str(currLag) + ' ' + str(numOfTest) + ' ' + str(maxTestTime)
            script = subprocess.Popen(cmd, stdout=sys.stdout, shell=False)
            if script.poll() is None:
                print('Running new test (' + str(numOfTest) + ' times) with lag: ' + str(currLag) + ' and lag compensation: ' + lagCompensation + '!')

            # Break from infinite loop once minimum lag has been reached
            if currLag == maxLag:
                break

            # Increase lag until hitting max
            currLag += lagStep
            lagStep *= 2
            if currLag >= maxLag:
                currLag = maxLag
        else:
            continue  # Don't start a new test if one is already running

    currLag = minLag  # Reset lag value for next run
    lagStep = currLag
    if lagCompensation == 't':
        lagCompensation = 'f'  # Except now reverse the lag compensation
    else:
        lagCompensation = 't'

# Block until the last script has finished running
while script.poll() is None:
    time.sleep(1)

winsound.Beep(1000, 500)  # Play sound to notify me the script finished
winsound.Beep(1200, 500)  # Play sound to notify me the script finished
winsound.Beep(1400, 500)  # Play sound to notify me the script finished