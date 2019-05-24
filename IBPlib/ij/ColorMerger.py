# ColorMerger.py
# Dev: Igor Bonacossa Pereira.
# Email: i.bonacossapereira@uq.edu.au

import os.path
import java.lang.Exception
import traceback

from threading import Thread
from Queue import Queue
from time import clock

from ij import (ImagePlus, IJ)
from ij.io import FileSaver
from ij.plugin import RGBStackMerge
from IBPlib.ij.Colortags import Colortags
from IBPlib.ij.Utils.Files import buildList

__version__ = "1.0"
__threadname__ = "IBPlib.ij.ColorMerger" # Threads spawned by ColorMerger have this name + name of the final image.

class ColorMerger:
	'''
	If you want to use ColorMerger in opened images explicitly pass False or None to the 3 parameters.
	'''

	def __init__(self, savefolder, imgfolder, ext):
		self.Colortags = Colortags()
		self.savefolder = savefolder
		self.imgfolder = imgfolder
		self.ext = ext


	def run(self):
		'''
		Main pipeline to merge images in parallel
		'''
		IJ.log("\n### ColorMerger v{0} has started".format(__version__))
		img_list = buildList(self.imgfolder, extension=self.ext)
		IJ.log("\n{0} images are being processed.".format(len(img_list)))
		titleslist = [os.path.split(img)[1] for img in img_list]
		sortedtitles = self.sortbytag(titleslist)
		tasks_q= Queue()
		for root, channels in sortedtitles.items():
			thread = Thread(target=self.mergerthread_task,
							args=(tasks_q, root, channels),
							name="{0}.{1}".format(__threadname__, root))
			thread.daemon = True
			thread.start()
			tasks_q.put(thread)
		tasks_q.join()
		IJ.log("\n### Done merging.")


	def sortbytag(self, titleslist):		
		'''
		Sorts and indexes images based on the root of the image title and color tag index.
		Image gets excluded from sorted list if it has only one channel.
		'''
		sortedimgs = {}
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


	def mergechannels(self, root, sortedchannels):
		'''
		Merge sorted channels(list of titles) under a given root title.
		If ColorMerger was initialized with a savefolder it will try to save img in savefolder
		else will merge channels, close original images and show the resulting composite.
		'''
		IJ.log("\n## Merging <{0}>".format(root))
		imgpaths = [os.path.join(self.imgfolder, title) if title else None for title in sortedchannels]
		imps = [ImagePlus(path) if path else None for path in imgpaths]
		for img in imps:
			if img:
				calibration = img.getCalibration()
				break
		merger = RGBStackMerge()
		composite = merger.mergeChannels(imps, False)
		composite.setCalibration(calibration)
		if self.savefolder:
			save_string = os.path.join(self.savefolder, root)
			IJ.log("\tSaving {0}".format(save_string))
			try:
				FileSaver(composite).saveAsTiff(save_string)
			except (Exception, java.lang.Exception) as e:
				IJ.log("ij.io.FileSaver raised an {0} exception while trying to save img '{1}' as '{2}'. Skipping image."
						.format(e, root, save_string))
		else:
			composite.setTitle(root)
			[imp.close() for imp in imps if imp]
			composite.show()

	def mergerthread_task(self, q, root, sortedchannels):
		'''
		Wrapper method to encapsulate mergechannels in a Thread inside a Queue object
		'''
		try:
			self.mergechannels(root, sortedchannels)
		except (Exception, java.lang.Exception):
			IJ.log(traceback.format_exc())
		finally:
			q.task_done()
		

if __name__ in ("__builtin__", "__main__"):

	savefolder = r"C:\Users\uqibonac\Desktop\temp\test"
	ext = ".tif"
	imgfolder = r"G:\Igor\Projects\Let-805\Raw Data\Microscopies\Yokogawa Spinning Disk\let-805(syb381)\unc-70(n493)\1DOA\63x OIL\raw"
	cm = ColorMerger(savefolder, imgfolder, ext)
	cm.run()