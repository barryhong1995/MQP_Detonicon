#!/usr/bin/python

'''
This script runs a specified numbers of tests on lag
    Test:
        Spawn a Server
        Spawn specified number of bots with 0 lag
        Spawn a player with varying amounts of lag and lag compensation
'''

import subprocess
import time
import random
import fileinput
import os

configPath = 'detonicon\\x64\Release\df-config.txt'
configPath = 'df-config.txt'

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


# Parameters
playerID = 1  # Investigator manually changes this value per participant
mapID = 5  # map ID of test
numBotsForAutoStart = 2  # Number of Bots to spawn

# Print parameters
print('mapID: ' + str(mapID))
print('playerID: ' + str(playerID))
print('numBotsForAutoStart: ' + str(numBotsForAutoStart))

# Processes
sProcess = None  # Holds the Server process
bProcesses = []  # Array that holds Bot spawned processes (Clients)

botCmd = 'detonicon\\x64\Release\detonicon.exe -b -lc localhost 0 2 2'  # Command for spawning an unlagged bot

playerCmds = []  # Array to hold all the cmds used to test the player (varying amounts of lag, with or without lag compensation)
playerCmds.append('detonicon\\x64\Release\detonicon.exe -p -lc localhost 0')  # 0 lag
playerCmds.append('detonicon\\x64\Release\detonicon.exe -p -lc localhost 40')  # 40 lag, lag compensation
playerCmds.append('detonicon\\x64\Release\detonicon.exe -p -wolc localhost 40')  # 40 lag, no lag compensation
playerCmds.append('detonicon\\x64\Release\detonicon.exe -p -lc localhost 80')  # 80 lag, lag compensation
playerCmds.append('detonicon\\x64\Release\detonicon.exe -p -wolc localhost 80')  # 80 lag, no lag compensation
playerCmds.append('detonicon\\x64\Release\detonicon.exe -p -lc localhost 160')  # 160 lag, lag compensation
playerCmds.append('detonicon\\x64\Release\detonicon.exe -p -wolc localhost 160')  # 160 lag, no lag compensation
playerCmds.append('detonicon\\x64\Release\detonicon.exe -p -lc localhost 320')  # 320 lag, lag compensation
playerCmds.append('detonicon\\x64\Release\detonicon.exe -p -wolc localhost 320')  # 320 lag, no lag compensation
playerCmds.append('detonicon\\x64\Release\detonicon.exe -p -lc localhost 640')  # 640 lag, lag compensation
playerCmds.append('detonicon\\x64\Release\detonicon.exe -p -wolc localhost 640')  # 640 lag, no lag compensation

random.shuffle(playerCmds)  # Shuffle so players don't know what test comes next

def runTest():
    global numBotsForAutoStart
    global botCmd
    global playerCmds
    global sProcess
    global bProcesses

    # All player tests have been run, return false
    if not playerCmds:
        return 'No tests left!'

    setHeadless(True)  # Server and bots should be headless and invisible

    # Spawn Server
    sProcess = subprocess.Popen('detonicon\\x64\Release\detonicon.exe -s ' + str(mapID) + ' ' + str(numBotsForAutoStart + 1), stdout=subprocess.PIPE, shell=False)
    time.sleep(5)

    # Spawn Bots
    for botNum in range(numBotsForAutoStart):
        bProcesses.append(subprocess.Popen(botCmd, shell=False))
        time.sleep(2)

    # Spawn Player
    setHeadless(False)  # Player should not be headless
    playerCmd = playerCmds.pop()
    bProcesses.append(subprocess.Popen(playerCmd, shell=False))

    # Another player test is ran
    return playerCmd

# Is there a test currently running?
isRunningTest = False

# File to print cmd used for each run of player (So we know which run had which lag/lag compensation), sandwich BEGIN
pFileName = 'results/' + str(int(time.time())) + '_playerCmds_id_' + str(playerID) + '_sandwichBEGIN.txt'
with open(pFileName, 'a') as myfile:
    myfile.write('Beginning log of player commands:\n')

# Infinite loop to run tests
while len(playerCmds) > 0:
    # Test is not running, time to start another one
    if isRunningTest == False:
        try:
            for process in bProcesses:
                process.kill()  # Kill bot process (Clients)
            sProcess.kill()  # Kill Server process
        except AttributeError as e:
            pass
        bProcesses = []  # Reset array of running Client processes
        sProcess = None  # Reset holder of Server process
        playerCmd = runTest()  # Run test

        # Write to log file the cmd for this run
        with open(pFileName, 'a') as myfile:
            myfile.write(str(playerCmd) + '\n')

        print("Running new Test! ID: " + str(playerCmd))
        if '!' in playerCmd:
            break  # Break out of infinite loop once all player tests have been run

    time.sleep(1)  # Don't keep checking every loop, wait a bit to check

    # Loop through all Bot processes to check if test is running
    isRunningTest = False
    for process in bProcesses:
        if process.poll() == None:  # If bot process is still running, continue
            isRunningTest = True
            break

# Block until the last script has finished running
while True:
    isRunningTest = False
    for process in bProcesses:
        if process.poll() == None:  # If bot process is still running, continue
            isRunningTest = True
            break

    if sProcess.poll() == None:
        isRunningTest = True

    time.sleep(1)  # Don't keep checking every loop, wait a bit to check

    if isRunningTest == False:
        break

# Sandwich end logfile (a copy of the logfile, but with later timestamp name so both logfiles SANDWICH the player tests)
with open(pFileName) as myfile:
    lines = myfile.readlines()
    with open('results/' + str(int(time.time())) + '_playerCmds_id_' + str(playerID) + '_sandwichEND.txt', "w") as myfile2:
        myfile2.writelines(lines)
