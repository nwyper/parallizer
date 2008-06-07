#!/usr/bin/python

import time
import subprocess
import thread
import threading
import signal
import os
import sys


class Parallizer:
  def __init__(self, count=2):
    self.count = count
    self.processlist = []
    self.activeprocesses = []
    self.lock = threading.Lock()
    self.runthread = thread.start_new_thread(Parallizer.run,\
        (self, self.lock))


  def addprocess(self, args, **kwargs):
    # add another job to the list of processes
    self.lock.acquire()

    kwargs['args'] = args
    self.processlist.append(kwargs)

    self.lock.release()


  def run(self, lock):
    while True:
      # acquire the lock for the process lists
      self.lock.acquire()

      # remove each completed proces
      for process in self.activeprocesses:
        if process.poll() != None:
          self.activeprocesses.remove(process)

      # add processes until the active process list is full
      while len(self.activeprocesses) < self.count:

        # if no processes are waiting, there's nothing to do!
        if len(self.processlist) < 1:
          break

        # grab the first process in the list
        process = self.processlist[0]

        # remove the process from the incoming list
        self.processlist.pop(0)

        print "starting new process: %s" % process['args']

        # start a new subprocess in a new shell
        process['shell'] = True
        process = subprocess.Popen(**process)

        # add the new process to the active list
        self.activeprocesses.append(process)

      # release the lock
      self.lock.release()

      # kill some time
      time.sleep(0.01)


  def poll(self):
    """ return the number of presently running processes """

    # acquire the lock for the process lists
    self.lock.acquire()

    # count how many processes are running
    activecount = len(self.activeprocesses)
    if activecount < self.count:
      waitcount = len(self.processlist)
      if activecount + waitcount >= self.count:
        activecount = self.count

    # release the lock
    self.lock.release()

    # return the count
    return activecount

  def wait(self):
    """ wait until all processes complete """

    while self.poll():
      time.sleep(0.01)


if __name__ == '__main__':
  parallizer = Parallizer(count=1)

  outdir = 'out'
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  for path, dirs, files in os.walk('/home/neil/photography'):
    for f in files:
      if f[-3:] == 'jpg':
        filename = os.path.join(path, f)
        outname = os.path.join(outdir, os.path.basename(filename))
        parallizer.addprocess('/usr/bin/convert -resize 50x50 %s %s' %
          (filename, outname))

  parallizer.wait()

