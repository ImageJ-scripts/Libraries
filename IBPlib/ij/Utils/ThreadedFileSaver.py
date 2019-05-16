import java.lang.Exception
import traceback

from threading import Thread
from Queue import Queue

import ij.io.FileSaver
from ij import (ImagePlus, IJ)

__version__ = "1.0"
__threadname__ = "IBPlib.ij.ThreadedFileSaver" # Threads spawned by ThreadedFileSaver have this name + name of the saved image.

class ThreadedFileSaver(Thread):
	'''
	This is a wrapper for ij.io.FileSaver class to be used as a Thread subclass.
	'''
	def __init__(self, f, savepath, command):
		'''
		'f' should be the file object to be saved.
		'savepath' the string for the saving path
		'command' the saving comand name to be used by ij.io.FileSaver.
		This class is only exposing the saveAs... methods
		See ij.io.FileSaver for available saveAs methods.
		'''
		super(t_filesaver,self).__init__(name="{0}.{1}".format(__threadname__, savepath))
		self.args = (f, savepath, command)
		
	def run(self):
		fs = ij.io.FileSaver(self.args[0])
		if "saveAs" not in self.args[2]:
			raise AttributeError("{0} only exposes the 'saveAs...' methods from ij.io.FileSaver.".format(__threadname__))
	
		command = getattr(fs, self.args[2])
		if not command(self.args[1]):
			IJ.log("# '{0}' could not be saved.".format(self.args[1]))
		IJ.log("# '{0}' was saved successfully.".format(self.args[1]))


if __name__ in ("__builtin__", "__main__"):
	pass