#!/usr/bin/python

'''
This script runs a specified numbers of tests on lag
    Test:
        Spawn a Server
        Spawn 1 bot with a specified lag (using or without using lag compensation)
        Spawn the other bots with 0 lag
'''

import subprocess
import time
import random
import sys
import winsound

# Parameters
mapID = 7  # Map id of test
numBotsForAutoStart = 3  # Number of Bots to spawn, one will be lagged
lagCompensation = True  # Whether or not the lagged bot will be using lagCompensation
lagInMS = 320  # How much latency will the lagged bot be under in milliseconds
numOfTest = 1  # How many tests to run using these parameters before terminating
maxTestTime = 120  # Maximum time (in seconds) allowed for test before killing the test (in case something goes wrong)

# Parse command line (if given)
# Script parameters: mapID numBotsForAutoStart lagCompensation lagInMS numOfTest maxTestTime
if len(sys.argv) == 7:
    mapID = int(sys.argv[1])
    numBotsForAutoStart = int(sys.argv[2])
    if 't' in sys.argv[3]:
        lagCompensation = True
    else:
        lagCompensation = False
    lagInMS = int(sys.argv[4])
    numOfTest = int(sys.argv[5])
    maxTestTime = int(sys.argv[6])

# Print parameters
print('mapID: ' + str(mapID))
print('numBotsForAutoStart: ' + str(numBotsForAutoStart))
print('lagCompensation: ' + str(lagCompensation))
print('lagInMS: ' + str(lagInMS))
print('numOfTest: ' + str(numOfTest))
print('maxTestTime: ' + str(maxTestTime) + '\n')

# Processes
sProcess = None  # Holds the Server process
bProcesses = []  # Array that holds Bot spawned processes (Clients)

# Used to set lagCompensation parameter in cmd
if lagCompensation is True:
    lagCompensation = '-lc'
else:
    lagCompensation = '-wolc'

def runTest():
    global numBotsForAutoStart
    global lagCompensation
    global lagInMS
    global sProcess
    global bProcesses

    # Spawn Server
    sProcess = subprocess.Popen('detonicon\\x64\Release\detonicon.exe -s ' + str(mapID) + ' ' + str(numBotsForAutoStart), stdout=subprocess.PIPE, shell=False)
    time.sleep(5)

    # Set up cmds
    cmds = []
    for i in range(numBotsForAutoStart - 1):
        cmds.append('detonicon\\x64\Release\detonicon.exe -b -lc localhost 0 2 2')  # Spawn unlagged bot
    cmds.append('detonicon\\x64\Release\detonicon.exe -b ' + lagCompensation + ' localhost ' + str(lagInMS) + ' 2 2')  # Spawn lagged bot
    random.shuffle(cmds)  # Shuffle because order of spawn should not matter

    # Spawn Bots
    for cmd in cmds:
        bProcesses.append(subprocess.Popen(cmd, shell=False))
        time.sleep(2)

# Is there a test currently running?
isRunningTest = False

# Infinite loop to run tests
testId = 0  # Just keeps track of test #
startTime = time.time()
while True:
    # Test is not running, time to start another one
    if isRunningTest == False:
        try:
            for process in bProcesses:
                process.kill()  # Kill bot process (Clients)
            sProcess.kill()  # Kill Server process
        except AttributeError as e:
            pass
        bProcesses = []  # Reset array of running Bot processes (Clients)
        sProcess = None  # Reset holder of Server process
        runTest()  # Run test
        startTime = time.time()  # Start timer for test
        testId += 1
        print("Running new Test! ID: " + str(testId))

    # Loop through all Bot processes to check if test is running
    isRunningTest = False
    for process in bProcesses:
        if process.poll() == None:  # If bot process is still running, continue
            isRunningTest = True
            break

    time.sleep(1)  # Don't keep checking every loop, wait a bit to check

    print(time.time() - startTime)
    # The test is taking too long, so kill the processes and move on to another test
    if time.time() - startTime >= maxTestTime:
        print('Terminating test.')
        try:
            for process in bProcesses:
                process.kill()  # Kill bot process (Clients)
            sProcess.kill()  # Kill Server process
        except AttributeError as e:
            pass
        isRunningTest = False

    # Break from infinite loop once specified # of tests are run and all Server process has died
    if numOfTest - testId <= 0:
            break

# Block until the last script has finished running
while True:
    isRunningTest = False
    for process in bProcesses:
        if process.poll() == None:  # If bot process is still running, continue
            isRunningTest = True
            break

    time.sleep(1)  # Don't keep checking every loop, wait a bit to check
    print(time.time() - startTime)

    if isRunningTest == False:
        break

winsound.Beep(750, 2000)  # Play sound to notify me the script finished