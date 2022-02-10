# ColorMerger.py
# Dev: Igor Bonacossa Pereira.
# Email: i.bonacossapereira@uq.edu.au

import os.path
import java.lang.Exception
import traceback

from threading import (Thread, current_thread)
from Queue import Queue
from time import clock


# Bootstrap to extend modules search path #
from sys import path
from java.lang.System import getProperty
jython_scripts = os.path.join(getProperty('user.home'), 'Jython_scripts')
path.append(jython_scripts)
#=========================================#

from ij import IJ
from ij.io import FileSaver
from ij.plugin import RGBStackMerge
from IBPlib.ij.Colortags import Colortags
from IBPlib.ij.Utils.Files import (buildList, imageloader)

__version__ = "1.1"
__threadname__ = "IBPlib.ij.ColorMerger" # Threads spawned by ColorMerger have this name + name of the final image.

class ColorMerger:
	'''
	If you want to use ColorMerger in opened images explicitly pass False or None to the 3 parameters.
	'''

	def __init__(self, savefolder, imgfolder, ext, debug=False):
		self.debug=debug
		self.Colortags = Colortags()
		self.savefolder = savefolder
		self.imgfolder = imgfolder
		self.ext = ext
		self.MAXWORKERS = 3
		self.tasks_q = Queue()
		self.workers = []
		

	def run(self, onGPU=False, postProcessingMethod=None, postProcessingMethodArgs=[]):
		'''
		Main pipeline to merge images in parallel
		'''
		IJ.log("\n### ColorMerger v{0} has started".format(__version__))
		if self.debug:
			IJ.log("\n*** Debug mode")
		img_list = buildList(self.imgfolder, extension=self.ext, debug=self.debug)
		IJ.log("\n{0} images are being processed.".format(len(img_list)))
		titleslist = [os.path.split(img)[1] for img in img_list]
		sortedtitles = self.sortbytag(titleslist)
		if self.debug:
			print("\nColorMerger.run() -> titleslist = {0}\n\nsortedtitles = {1}".format(titleslist, sortedtitles))
		IJ.log("\n#########\n")
   
		for root, channels in sortedtitles.items():
			self.tasks_q.put((root, channels, onGPU,
				postProcessingMethod,
				postProcessingMethodArgs),
			block=True)
		IJ.log("Tasks ready")
		self.setup_workers()

		self.tasks_q.join()
		IJ.log("\n### Done merging.")


	def dummy_task(self):
		import time.sleep
		while not self.tasks_q.empty():
			root, sortedchannels, onGPU, postProcessingMethod, postProcessingMethodArgs = self.tasks_q.get()
			IJ.log("Working on {0}".format(root))
			time.sleep(5)
			IJ.log("Done working on {0}".format(root))
			self.tasks_q.task_done()


	def setup_workers(self):
		task = self.mergerthread_task
		if self.debug:
			task = self.dummy_task
		 
		for i in range(self.MAXWORKERS):
			t = Thread(target=task, name="{0}.{1}".format(__threadname__, i))
			self.workers.append(t)
			t.start()


	def sortbytag(self, titleslist):
		'''
		Sorts and indexes images based on the root of the image title and color tag index.
		Image gets excluded from sorted list if it has only one channel.
		'''
		sortedimgs = {}
		if self.debug:
			print("Checking user defined colortags -> {0}".format(self.Colortags.tags))
		for img in titleslist:
			imgtitleroot = ""
			for index, tagstuple in self.Colortags.tags.items():
				for colortag in tagstuple:
					if colortag not in img:
						continue
					imgtitleroot = "".join(img.split(colortag))
					if imgtitleroot not in sortedimgs:
						impsbucket = [None]*7
						impsbucket[index] = img
						sortedimgs.update({imgtitleroot:impsbucket})
					else:
						sortedimgs[imgtitleroot][index] = img
		singlets = []
		for root, channels in sortedimgs.items():
			channelcount = len([True for title in channels if title])
			if channelcount < 2:
				IJ.log("\nSkipping <{0}> as it had only one channel.".format(root))
				singlets.append(root)
		[sortedimgs.pop(root) for root in singlets]
		return sortedimgs


	def mergerthread_task(self):
		'''
		Wrapper method to encapsulate mergechannels in a Thread inside a Queue object
		'''
		while not self.tasks_q.empty():
			root, sortedchannels, onGPU, postProcessingMethod, postProcessingMethodArgs = self.tasks_q.get()
			try:
				self.mergechannels(root,
						sortedchannels,
						onGPU=onGPU,
						postProcessingMethod=postProcessingMethod,
						postProcessingMethodArgs=postProcessingMethodArgs)
			except (Exception, java.lang.Exception):
				IJ.log(traceback.format_exc())
			finally:
				self.tasks_q.task_done()


	def mergechannels(self, root, sortedchannels, onGPU=False, postProcessingMethod=None,
		postProcessingMethodArgs=[]):
		'''
		Merge sorted channels(list of titles) under a given root title.
		If ColorMerger was initialized with a savefolder it will try to save img in savefolder
		else will merge channels, close original images and show the resulting composite.
		'''
		IJ.log("\n## Merging <{0}>".format(root))
		imgpaths = [os.path.join(self.imgfolder, title) if title else None for title in sortedchannels]
		imps = [imageloader(path) if path else None for path in imgpaths]
		for img in imps:
			if img:
				calibration = img.getCalibration()
				break
		merger = RGBStackMerge()
		
		try:
			composite = merger.mergeChannels(imps, False)
			composite.setTitle(root)
		except (Exception, java.lang.Exception):
			t_name = current_thread().name
			IJ.log("# {0}\t{1} images skipped as channels have different dimensions".format(t_name, root))
			return
			
		try:	
			if postProcessingMethod:
				postProcessingMethod(composite, *postProcessingMethodArgs)
		except Exception as e:
			t_name = current_thread().name
			IJ.log("# {0}\t{1} post processing skipped due to error.\n{2}".format(t_name, root, e))
			
		composite.setCalibration(calibration)
		if self.savefolder:
			save_string = os.path.join(self.savefolder, root)
			try:
				FileSaver(composite).saveAsTiff(save_string)
				IJ.log("{0}".format(save_string))
			except (Exception, java.lang.Exception) as e:
				IJ.log("ij.io.FileSaver raised an {0} exception while trying to save img '{1}' as '{2}'. Skipping image."
						.format(e, root, save_string))
		else:
			composite.setTitle(root)
			[imp.close() for imp in imps if imp]
			composite.show()
			


if __name__ in ("__builtin__", "__main__"):

	savefolder = r"C:\Users\uqibonac\Desktop\temp\colormerged"
	ext = ".ics"
	imgfolder = r"C:\Users\uqibonac\Desktop\temp"
	cm = ColorMerger(savefolder, imgfolder, ext, debug=True)
	cm.run()