#!/usr/bin/env python

#################################################################################
# Import libraries
#################################################################################
import time
from pyfsm.Job import Job
from datetime import datetime
from os import environ as ENV
from pyfsm.DropboxStorage import DropboxStorage
from LEDIndicator import LEDIndicator

#################################################################################
# Perform initializations
#################################################################################

#################################################################################
# Class definitions
#################################################################################

# @desc When the job is started, it creates a time entry for the user stored in
#       `card_event_data` and appends it local storage (USB stick)
# @TODO Make it so that only one of these workers can be running at a time, to ensure
#       shared csv data is not corrupted. Can also lock objects, but easiest way is to
#       implement job queue allowing only one job to run at a time
class AsyncWriteTimeEntryJob(Job):
    def __init__(self, card_event_data, localStorage, ledQueue):
        Job.__init__(self)
        self.student_id = card_event_data["id"]
        self.localStorage = localStorage
        self.ledQueue = ledQueue

    def run_test(self):
        # print("Writing time entry...")
        self.run_prod()

    def run_prod(self):
        name = self.localStorage.lookup_id(str(self.student_id))
        if name == "NOT_FOUND":
            # flash red b/c user not in system
            self.ledQueue.put(LEDIndicator.LED_TYPES[4])
        else:
            # flash green b/c user is in system
            self.ledQueue.put(LEDIndicator.LED_TYPES[10])
        epoch = time.time()
        timestamp = datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

        # get the timestamped filename that this entry belongs in
        path_preface = self.localStorage.get_current_time_period()

        # write time entries dependent on student's clock in/out state
        if (str(self.student_id) in self.localStorage.time_in_entries):
            # time entry started, close it out
            # write the "out" entry
            out_entry = [[name, self.student_id, timestamp]]
            self.localStorage.append_rows(path_preface + "time_out_entries.csv", out_entry)
            print("Appended Out entry: " + str(out_entry))
            prev_entry = self.localStorage.time_in_entries[str(self.student_id)]
            # write the "in/out" entry
            elapsed_hours = round(((epoch - prev_entry["epoch_in"]) / 60), 2)
            in_out_entry = \
                [[name, self.student_id, prev_entry["ts_in"], timestamp, elapsed_hours]]
            self.localStorage.append_rows(path_preface + "time_entries.csv", in_out_entry)
            # remove "in" entry from the localStorage hash
            del self.localStorage.time_in_entries[str(self.student_id)]
            print("Appended In/Out entry: " + str(in_out_entry))
        else:
            # now previous entry, start a new one
            # write the "in" entry
            in_entry = [[name, self.student_id, timestamp]]
            self.localStorage.append_rows(path_preface + "time_in_entries.csv", in_entry)
            # add "in" entry to hash
            self.localStorage.time_in_entries[str(self.student_id)] = \
                {"epoch_in": epoch, "ts_in": timestamp}
            print("Appended In entry: " + str(in_entry))

# TODO: this should be paired with a service, jobs are one-off
class AsyncPeriodicSyncWithDropboxJob(Job):
    # @param period Time in seconds to wait between syncs
    def __init__(self, period, file_names):
        Job.__init__(self)
        self.period = period
        self.file_names = file_names
        # necessary since in inf. loop, temporary until ported to service
        self.setDaemon(True)

    def run_prod(self):
        dbx = DropboxStorage(ENV["AT_DROPBOX_AUTH_TOKEN"], ENV["AT_LOCAL_STORAGE_PATH"])
        while True:
            # wait for `period` to run
            time.sleep(self.period)
            # log it
            print("Syncing with dropbox")
            # sync all of self.files
            for file_name in self.file_names:
                dbx.upload(file_name)

# class AsyncChangeLEDIndicatorJob(Job):
#     def __init__(self, error_code, error_param, LEDQueue):
#         Job.__init__(self)
#         self.error_code = error_code
#         self.error_param = error_param
#
#     def run_prod(self):
#         
#         if self.error_code
#             # TODO: .. FINISH implementation to change state (push to queue)


#################################################################################
# House keeping..close interfaces and processes
#################################################################################
