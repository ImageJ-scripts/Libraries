# Projector.py
# IBP
# i.bonacossapereira@uq.edu.au

import java.lang.Exception
import traceback

import os.path

<<<<<<< HEAD
from threading import Thread

from Queue import Queue

import ij.gui.GenericDialog
import ij.io.FileSaver
from ij import (IJ, ImagePlus, WindowManager, CompositeImage)
from ij.plugin import ZProjector
from IBPlib.ij.Utils.Files import buildList

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

		if self.imgfolder and self.savefolder and self.ext:
			self.search = True
		else:
			self.search = False

	def run(self):
		'''
		Main pipeline to generate the projections images in parallel
		'''
		IJ.log("\n### Z-projector v{0} has started".format(__version__))

		if self.search:
			img_list = buildList(self.imgfolder, extension=self.ext)
			dialog = GenericDialog("Zprojector.py")
			dialog.addMessage("There are {0} images to be processed.\n Proceed?".format(len(img_list)))
			dialog.showDialog()
			if dialog.wasCanceled():
				IJ.log("Canceled by the user.")
				return
			titleslist = [os.path.split(img)[1] for img in img_list]
		else:
			titleslist = WindowManager.getImageTitles()
		
		tasks_q= Queue()
		
		for img in titleslist:
			thread = Thread(target=self.projectorthread_task,
							args=(tasks_q, img),
							name="{0}.{1}".format(__threadname__, img))
			thread.daemon = True
			thread.start()
			tasks_q.put(thread)
		tasks_q.join()

		IJ.log("### Done merging.")

	def doprojection(self, title):
		
		IJ.log("# Processing {0}...".format(title))
		if self.search:
			imgpath = os.path.join(self.imgfolder, title)
			imp = ImagePlus(imgpath)
		else:
			imp = WindowManager.getImage(title)
		calibration = imp.getCalibration()
		composite_imp = CompositeImage(imp, 1)
		projection = ZProjector.run(composite_imp, self.method)
		projection.setCalibration(calibration)
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

			
	def projectorthread_task(self, q, img):
		'''
		Wrapper method to encapsulate doprojection in a Thread inside a Queue object
		'''
		try:
			self.doprojection(img)
		except (Exception, java.lang.Exception):
			print(traceback.format_exc())
		finally:
			q.task_done()
		
if __name__ in ("__builtin__", "__main__"):
	projector = Projector(False, False, False)
=======
from threading import Thread
from Queue import Queue

import ij.io.FileSaver
from ij import (IJ, ImagePlus, CompositeImage)
from ij.plugin import ZProjector
from IBPlib.ij.Utils.Files import buildList

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

	def run(self):
		'''
		Main pipeline to generate the projections images in parallel
		'''
		print("\n### Z-projector v{0} has started".format(__version__))
		img_list = buildList(self.imgfolder, extension=self.ext)
		print("There are {0} images to be processed.\n".format(len(img_list)))
		titleslist = [os.path.split(img)[1] for img in img_list]

		tasks_q= Queue()
		
		for img in titleslist:
			thread = Thread(target=self.projectorthread_task,
							args=(tasks_q, img),
							name="{0}.{1}".format(__threadname__, img))
			thread.daemon = True
			thread.start()
			tasks_q.put(thread)
		tasks_q.join()

		print("### Done merging.")

	def doprojection(self, title):
		
		print("# Processing {0}...".format(title))
		imgpath = os.path.join(self.imgfolder, title)
		imp = ImagePlus(imgpath)
		composite_imp = CompositeImage(imp, 1)
		projection = ZProjector.run(composite_imp, self.method)
		if self.savefolder:
			save_string = os.path.join(self.savefolder, title)
			try:
				ij.io.FileSaver(projection).saveAsTiff(save_string)
				print("## {0} Done processing ".format(title))
			except:
				print("ij.io.FileSaver raised an exception while trying to save img '{0}' as '{1}'.Skipping image."
						.format(title, save_string))
		else:
			imp.close()
			projection.show()

			
	def projectorthread_task(self, q, img):
		'''
		Wrapper method to encapsulate doprojection in a Thread inside a Queue object
		'''
		try:
			self.doprojection(img)
		except (Exception, java.lang.Exception):
			print(traceback.format_exc())
		finally:
			q.task_done()
		
if __name__ in ("__builtin__", "__main__"):
	projector = Projector(False, False, False)
>>>>>>> headless
	projector.run()