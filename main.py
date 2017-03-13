#!/usr/bin/env python

# @note ENV vars: ATTENDANCE_TRACKER_TEST, and AT_LOCAL_STORAGE_PATH

#####################################################################################
# Import libraries
#####################################################################################
import Jobs
import Events
import Services
import StateHandlers
import EventListeners
from os import environ as ENV
from PyFSM.pyFSM import PyFSM
from PyFSM import EventListener

#####################################################################################
# Main logic
#####################################################################################
def main():
    #################################################################################
    # Perform tests
    #################################################################################
    # Check if test mode enabled
    if not 'ATTENDANCE_TRACKER_TEST' in ENV or \
       not int(ENV['ATTENDANCE_TRACKER_TEST']) == 1:
           print "Attendance Tracker Test Mode DISABLED"
    else:
       print "Attendance Tracker Test Mode ENABLED"

    # run all lib tests
    print("MAIN: Started up! Running tests.")

    # TODOB: run tests here
    # TODOB: check if each test passed and proceed if so

    #################################################################################
    # Perform initializations
    #################################################################################
    services = []
    # services = [Services.AsyncPeriodicSyncWithDropbox(20,["time_in_entries.csv", "time_out_entries.csv", "time_entries.csv"])]
    eventListeners = [ EventListener.TimerEventListener(5.0),
                       EventListeners.CardReadEventListener("MY_CARD_READER") ]
    stateHandlers = [ StateHandlers.InitStateHandler,
                      StateHandlers.TempStateHandler ]
    enabledLibs = [ LocalStorage(ENV["AT_LOCAL_STORAGE_PATH"]) ]
    # enabledLibs = [ LocalStorage(ENV["AT_LOCAL_STORAGE_PATH"]),
    #         DropboxStorage(ENV["AT_DROPBOX_AUTH_TOKEN"], ENV["AT_LOCAL_STORAGE_PATH"])]

    #################################################################################
    # Begin the main FSM runloop
    #################################################################################
    # pyFSM = PyFSM(events, stateHandlers, services, enabledLibs)
    pyFSM = PyFSM(services, eventListeners, stateHandlers, enabledLibs)
    error_message = pyFSM.start()

    # error'd out..print the message
    print("ERROR: " + error_message)

if __name__ == '__main__':
    main()
