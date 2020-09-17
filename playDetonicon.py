#!/usr/bin/python

'''
    Use this script if you want to play one game of Detonicon on one machine.
    You can specify number of bots.
    You can specify your latency.
    You can specify whether or not latency compensation is turned on.
'''

import subprocess
import time
import random
import fileinput
import os
import sys

# Parameters
mapID = 7  # Map id of test
numBotsForAutoStart = 2  # Number of Bots to spawn (your opponents)
lagCompensation = True  # Whether or not you, the player will be using lag compensation
lagInMS = 0  # How much latency will you, the player be have in milliseconds

# Parse command line (if given), otherwise just use the default parameters above
# Script parameters: mapID numBotsForAutoStart lagCompensation lagInMS
if len(sys.argv) == 5:
    mapID = int(sys.argv[1])
    numBotsForAutoStart = int(sys.argv[2])
    if 't' in sys.argv[3]:
        lagCompensation = True
    else:
        lagCompensation = False
    lagInMS = int(sys.argv[4])

configPath = 'df-config.txt'  # Path to config file so we can change and spawn server and bots headless

# Redefine headless mode in df-config.txt file
def setHeadless(trueOrFalse):
    for line in fileinput.input(configPath, inplace=True):
        if 'headless:' in line:
            if trueOrFalse == True:
                print('headless:true,')
            else:
                print('headless:false,')
        else:
            print(line.strip())


# Print parameters
print('mapID: ' + str(mapID))
print('numBotsForAutoStart: ' + str(numBotsForAutoStart))
print('lagCompensation: ' + str(lagCompensation))
print('lagInMS: ' + str(lagInMS) + '\n')

# Processes
sProcess = None  # Holds the Server process
bProcesses = []  # Array that holds Bot spawned processes (Clients)
pProcess = None  # Player process

# Used to set lagCompensation parameter in cmd
if lagCompensation is True:
    lagCompensation = '-lc'
else:
    lagCompensation = '-wolc'

botCmd = 'detonicon\\x64\Release\detonicon.exe -b -lc localhost 0 2 2'  # Command for spawning an unlagged bot
playerCmd = 'detonicon\\x64\Release\detonicon.exe -p' + ' ' + lagCompensation + ' ' + 'localhost' + ' ' + str(lagInMS)  # Command for spawning the player

def playGame():
    global numBotsForAutoStart
    global lagCompensation
    global lagInMS
    global sProcess
    global bProcesses
    global botCmd
    global pProcess

    setHeadless(True)  # Server and bots should be headless and invisible

    # Spawn Server
    sProcess = subprocess.Popen('detonicon\\x64\Release\detonicon.exe -s ' + str(mapID) + ' ' + str(numBotsForAutoStart + 1), stdout=subprocess.PIPE, shell=False)
    time.sleep(5)

    # Spawn Bots
    for botNum in range(numBotsForAutoStart):
        bProcesses.append(subprocess.Popen(botCmd, shell=False))
        time.sleep(2)

    setHeadless(False)  # Server and bots should be headless and invisible

    # Spawn Player
    pProcess = subprocess.Popen(playerCmd, shell=False)

playGame()

# Block until the last player process is finished running
while True:
    isRunning = False

    if pProcess.poll() == None:
        isRunning = True

    time.sleep(1)  # Don't keep checking every loop, wait a bit to check

    if isRunning == False:
        break

try:
    for process in bProcesses:
        process.kill()  # Kill bot process (Clients)
    sProcess.kill()  # Kill Server process
    pProcess.kill()  # Kill player process
except AttributeError as e:
    pass
