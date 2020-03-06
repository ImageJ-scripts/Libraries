# Projector.py
# IBP
# i.bonacossapereira@uq.edu.au

import java.lang.Exception
import traceback


import os.path

from threading import Thread

from Queue import Queue

import ij.io.FileSaver
from ij import (IJ, CompositeImage)
from ij.plugin import ZProjector
from IBPlib.ij.Utils.Files import (buildList, imageloader)

try:
	from net.haesleinhuepf.clij import CLIJ
	clij = CLIJ.getInstance()
except ImportError:
	IJ.error("CLIJ not installed, GPU processing won't be available")

__version__ = "1.0"
__threadname__ = "IBPlib.ij.Zprojector" # Threads spawned by Zprojector have this name + name of the final image.

class Projector:
	'''
	If you want to use Zprojector in opened images explicitly pass False or None to the 4 parameters.
    Note that by default it will generate maximum intensity projections when run as a hotkey macro.
	'''

	def __init__(self, savefolder, imgfolder, ext, method="max"):
		self.savefolder = savefolder
		self.imgfolder = imgfolder
		self.ext = ext
		self.method = method

	def run(self, onGPU=False):
		'''
		Main pipeline to generate the projections images in parallel
		'''
		IJ.log("\n### Z-projector v{0} has started".format(__version__))
		img_list = buildList(self.imgfolder, extension=self.ext)
		IJ.log("There are {0} images to be processed.\n".format(len(img_list)))
		if onGPU:
			IJ.log("GPU being used to project. Be aware that only MAX z-projection is supported.")
		titleslist = [os.path.split(img)[1] for img in img_list]

		tasks_q= Queue()

		for img in titleslist:
			thread = Thread(target=self.projectorthread_task,
							args=(tasks_q, img),
							kwargs=({"onGPU":onGPU}),
							name="{0}.{1}".format(__threadname__, img))
			thread.daemon = True
			thread.start()
			tasks_q.put(thread)
		tasks_q.join()

		IJ.log("### Done projecting.")


	def projectorthread_task(self, q, img, onGPU=False):
		'''
		Wrapper method to encapsulate doprojection in a Thread inside a Queue object
		'''
		try:
			self.doprojection(img, onGPU=onGPU)
		except (Exception, java.lang.Exception):
			IJ.log(traceback.format_exc())
		finally:
			q.task_done()


	def doprojection(self, title, onGPU=False):
		'''
		Run ij.plugin.Zprojector on image referenced by title using self.method as
		projection method and saves the projection on self.savefolder.
		'''
		IJ.log("# Processing {0}...".format(title))
		imp = self.load_image(title)
		if onGPU:
			projection = self.CLIJ_max_projection(imp)
		else:
			projection = ZProjector.run(imp, self.method)
		if self.savefolder:
			save_string = os.path.join(self.savefolder, title)
			try:
				ij.io.FileSaver(projection).saveAsTiff(save_string)
				IJ.log("## {0} Done processing ".format(title))
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
		imp = imageloader(imgpath)
		composite_imp = CompositeImage(imp, 1)
		return composite_imp

	
	def CLIJ_max_projection(self, imp):
		'''
		Performs a z-projection on the GPU using CLIJ.
		Returns an imagePLus with the maximum projection of the image.
		'''
		if not CLIJ:
			raise NotImplementedError("CLIJ was not found, cannot perform operations on GPU.")

		imageInput = clij.push(imp)
		imageOutput = clij.create([imageInput.getWidth(), imageInput.getHeight()], imageInput.getNativeType())
		clij.op().maximumZProjection(imageInput, imageOutput)
		projection = clij.pull(imageOutput)
		imageInput.close()
		imageOutput.close()
		return projection

	
if __name__ in ("__builtin__", "__main__"):
	projector = Projector(False, False, False)
	projector.run()