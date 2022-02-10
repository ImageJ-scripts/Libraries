# Projector.py
# IBP
# i.bonacossapereira@uq.edu.au


# Boilerplate to extend modules search path #
from sys import path
import os.path
from java.lang.System import getProperty
jython_scripts = os.path.join(getProperty('user.home'), 'Jython_scripts')
path.append(jython_scripts)
#=========================================#

import java.lang.Exception
import traceback


import os.path

from threading import Thread

from Queue import Queue

import ij.io.FileSaver
from ij import (IJ, CompositeImage, ImagePlus)
from ij.plugin import ZProjector
from IBPlib.ij.Utils.Files import (buildList, imageloader)

try:
	from net.haesleinhuepf.clij2 import CLIJ2
	clij2 = CLIJ2.getInstance()
except ImportError:
	IJ.error("Warning: CLIJ not installed, GPU processing unavailable.")

__version__ = "1.1"
__threadname__ = "IBPlib.ij.Zprojector" # Threads spawned by Zprojector have this name + name of the final image.

class Projector:
	'''
	If you want to use Zprojector in opened images explicitly pass False or None to the 4 parameters.
    Note that by default it will generate maximum intensity projections when run as a hotkey macro.
	'''

	def __init__(self, savefolder, imgfolder, ext, method="max", debug=False):
		self.debug=debug
		self.savefolder = savefolder
		self.imgfolder = imgfolder
		self.ext = ext
		self.method = method
		self.MAXWORKERS = 3
		self.tasks_q = Queue()
		self.workers = []


	def run(self, onGPU=False, exclusionFlag="488",):
		'''
		Main pipeline to generate the projections images in parallel
		'''
		IJ.log("\n### Z-projector v{0} has started".format(__version__))
		img_list = buildList(self.imgfolder, extension=self.ext, debug=self.debug, exclusionFlag=exclusionFlag)
		IJ.log("There are {0} images to be processed.\n".format(len(img_list)))
		titleslist = [os.path.split(img)[1] for img in img_list]

		for img in titleslist:
			self.tasks_q.put((img, onGPU))
		self.setup_workers()
		self.tasks_q.join()
		IJ.log("### Done projecting.")


	def dummy_task(self):
		import time.sleep
		while not self.tasks_q.empty():
			img, onGPU = self.tasks_q.get()
			IJ.log("Working on {0}".format(img))
			time.sleep(5)
			IJ.log("Done working on {0}".format(img))
			self.tasks_q.task_done()

	def setup_workers(self):
		task = self.projectorthread_task
		if self.debug:
			task = self.dummy_task
		 
		for i in range(self.MAXWORKERS):
			t = Thread(target=task, name="{0}.{1}".format(__threadname__, i))
			self.workers.append(t)
			t.start()

			
	def projectorthread_task(self):
		'''
		Wrapper method to encapsulate doprojection in a Thread inside a Queue object
		'''
		while not self.tasks_q.empty():
			img, onGPU = self.tasks_q.get()
			try:
				self.doprojection(img, onGPU=onGPU)
			except (Exception, java.lang.Exception):
				IJ.log(traceback.format_exc())
			finally:
				self.tasks_q.task_done()


	def doprojection(self, titleOrImp, onGPU=False):
		'''
		Run ij.plugin.Zprojector on image referenced by title or imp using self.method as
		projection method and saves the projection on self.savefolder.
		'''
		if isinstance(titleOrImp, ImagePlus):
			imp = titleOrImp
			title = titleOrImp.getTitle()
		else:
			imp = self.load_image(titleOrImp)
			title = titleOrImp
			
		IJ.log("# Projecting {0}...".format(title))
		if onGPU:
			projection = self.CLIJ2_max_projection(imp)
		else:
			projection = ZProjector.run(imp, self.method)
		if self.savefolder:
			save_string = os.path.join(self.savefolder, title)
			try:
				ij.io.FileSaver(projection).saveAsTiff(save_string)
				IJ.log("{0}".format(save_string))
			except:
				IJ.log("ij.io.FileSaver raised an exception while trying to save img '{0}' as '{1}'.Skipping image."
						.format(title, save_string))
		else:
			imp.close()
			projection.show()

	
	def load_image(self, title):
		'''
		Loads an image according to its title.
		Returns an imageplus.
		'''
		imgpath = os.path.join(self.imgfolder, title)
		imp = imageloader(imgpath, debug=self.debug)
		composite_imp = CompositeImage(imp, 1)
		return composite_imp

	
	def CLIJ2_max_projection(self, imp):
		'''
		Performs a z-projection on the GPU using CLIJ.
		Returns an imagePLus with the maximum projection of the image.
		'''
		
		imageInput = clij2.push(imp)
		imageOutput = clij2.create([imageInput.getWidth(), imageInput.getHeight()], imageInput.getNativeType())
		clij2.op().maximumZProjection(imageInput, imageOutput)
		projection = clij2.pull(imageOutput)
		imageInput.close()
		imageOutput.close()
		return projection

	
if __name__ in ("__builtin__", "__main__"):
	
	test_img_folder = r"I:\LET805IBP-Q1894\Yokogawa\Staging area\111021\ColorMerged"
	test_output_folder = r"I:\LET805IBP-Q1894\Yokogawa\Staging area\111021\Z-Projections"
	projector = Projector(test_output_folder, test_img_folder, ".ics", debug=False)
	projector.run(onGPU=False, exclusionFlag="done",)