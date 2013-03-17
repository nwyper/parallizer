#!/usr/bin/python

import time
import subprocess
import sys


class Parallizer:
    def __init__(self, jobs=1, poll_time=0.1):
        self.jobs = jobs
        self.poll_time = poll_time
        self.processlist = []
        self.activeprocesses = []

    def update(self):
        # remove each completed proces
        for process in self.activeprocesses:
            if process.poll():
                self.activeprocesses.remove(process)

        # add processes until the active process list is full
        while len(self.activeprocesses) < self.jobs:

            # if no processes are waiting, there's nothing to do!
            if len(self.processlist) < 1:
                break

            # remove the process from the incoming list
            process = self.processlist.pop(0)

            print "starting new process: %s" % process['args']

            # start a new subprocess in a new shell
            process['shell'] = True
            process = subprocess.Popen(**process)

            # add the new process to the active list
            self.activeprocesses.append(process)

    def addprocess(self, args, **kwargs):
        kwargs['args'] = args
        self.processlist.append(kwargs)

    def poll(self):
        """ return the number of presently running processes """
        # count how many processes are running
        activecount = len(self.activeprocesses)
        if activecount < self.jobs:
            waitcount = len(self.processlist)
            if activecount + waitcount >= self.jobs:
                activecount = self.jobs

        # return the count
        return activecount

    def mainloop(self):
        while True:
            self.update()
            if self.poll() == 0:
                break
            time.sleep(self.poll_time)


if __name__ == '__main__':
    count = int(sys.argv[1])
    jobs = int(sys.argv[2])
    command = ' '.join(sys.argv[3:])
    print command

    parallizer = Parallizer(jobs=jobs)
    for i in xrange(count):
        parallizer.addprocess(command)

    parallizer.mainloop()
