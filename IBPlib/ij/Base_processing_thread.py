import os
from Queue import Queue

# Bootstrap to extend modules search path #
from sys import path
from java.lang.System import getProperty
jython_scripts = os.path.join(getProperty('user.home'), 'Jython_scripts')
path.append(jython_scripts)
#=========================================#

class Processing_Queue:
	__thread_name__ = "IBPlib.{0}.thread"
	__MAXWORKERS__ = 3
	tasks_q = Queue()
	workers = []