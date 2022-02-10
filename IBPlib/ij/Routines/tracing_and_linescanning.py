#@Context context

# Boilerplate to extend modules search path #
from sys import path
import os.path
from java.lang.System import getProperty
jython_scripts = os.path.join(getProperty('user.home'), 'Jython_scripts')
path.append(jython_scripts)
#=========================================#

import os
import threading
import csv
import datetime

from sc.fiji.snt import SNTService, Tree
from sc.fiji.snt.analysis import RoiConverter

from ij import IJ
from ij.io import RoiEncoder
from ij.gui import (WaitForUserDialog, Overlay, ProfilePlot)
from ij.plugin.frame import RoiManager

from IBPlib.ij.Routines import batch_parameters
from IBPlib.ij.Utils.Files import imageloader
from IBPlib.ij.Utils.Misc import validate_th_method

__VERSION__ = "1.11"
__NOW__ = datetime.date.today()
__BATCH_NAME__ = "IBPlib.tracing_and_linescanning v{0} {1}".format(__VERSION__,__NOW__)

def get_batch_schema():
	'''
	WIP
	'''
	__PARAMS_SCHEMA = {
		"raw_images": list,
		"analysed_images": list,
		"th_method": str,
		"stroke_width": int,
		"output_folder": str,
		"analysis_ch": int,
		"tracing_ch": int,
	}
	return __PARAMS_SCHEMA

	
def assisted_SNTtrace(context, imp):
	'''
	Calls SNT in a given img for user assisted tracing.
	Uses WaitForUserDialog to confirm the end of tracing operations.
	Returns list of SNT Paths.
	'''
	snt = prepare_SNT(context, imp)
	pafm = snt.getPathAndFillManager()
	dialog = WaitForUserDialog("Go to next step...", "Press ok when tracing is done.")
	dialog.show()
	if dialog.escPressed():
		raise RuntimeError("Canceled by the user.")

	SNTpaths = pafm.getPaths()

	return SNTpaths


def prepare_SNT(context, imp):
	'''
	Do a clean initialization of the SNT plugin
	and returns the working instance of it.
	'''
	snt = SNTService()
	if not snt.getContext():
		snt.setContext(context)
	sntUI = snt.getUI()

	if not sntUI:
		snt.initialize(True)
		sntUI = snt.getUI()
	elif not sntUI.isReady():
		snt.getPlugin().cancelPath()
		snt.getPlugin().cancelSearch(True)
		sntUI.changeState(snt.UI.READY)

	plugin = snt.getPlugin()
	print(imp)
	plugin.initialize(imp)
	plugin.getPathAndFillManager().clear()
	plugin.enableAstar(True)
	#plugin.enableHessian(True)

	return plugin


def convert_SNTpaths_to_roi(SNTpaths):
	'''
	Converts a list of SNT_paths to an Array of imageJ1 rois.
	'''
	roi_list = []
	for SNTpath in SNTpaths:
		as_tree = Tree()
		as_tree.add(SNTpath)
		converter = RoiConverter(as_tree)
		overlay = Overlay()
		converter.convertPaths(overlay)
		roi = overlay.toArray()[0]
		roi_list.append(roi)
	return roi_list


def get_profile(imp, roi, rm):
	'''
	Iteratively get the profile of each roi in a list from give img.
	returns ProfilePlots.
	'''
	i = rm.getCount()
	rm.add(roi, i)
	roi.setName("{0}_{1}".format(imp.getTitle(), i))
	rm.select(imp, i)
	pp = ProfilePlot(imp)
	return pp.getProfile()


def setup_output_folders(output_folder):
	'''
	Returns the rois output folder and the csvs output folder.
	If folders do not exist, will try to create them inside the output folder.
	Will create a folder named rois and another named csvs.
	'''
	outputs = (os.path.join(output_folder, "rois"), os.path.join(output_folder, "csvs"))
	[os.mkdir(folder) for folder in outputs if not os.path.exists(folder)]
	return outputs


def export_profile(profile_list, title, output, append=False):
	'''
	Exports lists to a csv file specified in profile_csv_path.
	First columnh will be named X and will contain the row number.
	Second column will be named Y and will contain  the list values on each row.
	'''
	if append:
		mode = "a"
	else:
		mode = "wb"
	profile_csv_path = os.path.join(output, "{0}{1}".format(title, ".csv"))
	with open(profile_csv_path, mode) as profile_csv:
		writer = csv.writer(profile_csv)
		writer.writerow(["X", "Y"])
		for i, value in enumerate(profile_list):
			writer.writerow([i, value])


def get_analysis_ch(imp, analysis_ch):
	'''
	Returns an ImagePlus of the channel index specified in analysis_ch
	'''
	from ij.plugin import ChannelSplitter

	analysis_imp = ChannelSplitter.split(imp)[analysis_ch-1]
	return analysis_imp


def apply_threshold(imp, th_method):
	'''
	Sets the ImageProcessor of the supplied imp to a BinayProcessor
	according to th_method.
	'''
	from ij.process import AutoThresholder as at

	ip = imp.getProcessor()
	ip.setAutoThreshold(at.Method.valueOf(th_method), True)
	bp = imp.createThresholdMask()
	imp.setProcessor(bp)


def run(context, imp, output_folder, analysis_ch, th_method, stroke_width, tracing_ch, dispose_snt=True):
	'''
	**dispose_snt kwarg is not implemented.

	Runs the main analysis pipeline.
	Consists in:
	>Opening image
	>Setting up SNT plugin to trace
	>Wait for user to trace paths
	>Converts paths do ImageJ1 Rois
	>Applies the rois to the image analysis channel
	>Gets the profile plot of the roi
	>Save results

	Returns true if run succeded or false if canceled.
	Importantly, the orginal image is not altered in any way.
	'''
	# Validation steps to prevent headaches along the pipeline
	validate_th_method(th_method)
	n_ch = imp.getNChannels()
	if n_ch < analysis_ch:
		raise ValueError("Analysis ch cannot be bigger than total number of channels.")

	rois_output, csvs_output = setup_output_folders(output_folder)
	imp.changes = False
	#imp.setC(tracing_ch)
	try:
		SNTpaths = assisted_SNTtrace(context, imp)
	except RuntimeError:
		SNTService().getPlugin().closeAndResetAllPanes()
		imp.close()
		return False
		
	if not SNTpaths:
		IJ.error("No paths found, reloading image.\nDid you forget to finish the trace?")
		return run(context, imp, output_folder, analysis_ch, th_method, stroke_width, tracing_ch, dispose_snt=dispose_snt)
		
	imp.hide()
	analysis_imp = get_analysis_ch(imp, analysis_ch)
	apply_threshold(analysis_imp, th_method)
	rm = get_clean_RoiManager()
	rois = convert_SNTpaths_to_roi(SNTpaths)
	profile_from_threshold(imp, analysis_ch, rois, stroke_width, th_method, csvs_output)
	for roi in rois:
		try:
			RoiEncoder.save(roi, os.path.join(rois_output, "{0}.roi".format(roi.getName())))
		except:
			IJ.error("Could not save {0}".format(roi.getName()))
	analysis_imp.changes = False
	analysis_imp.close()
	imp.close()
	return True


def get_clean_RoiManager(show=False):
	'''
	Returns a clean instance of RoiManager.
	'''
	rm = RoiManager.getInstance()
	if not rm:
		rm = RoiManager(show)
	rm.reset()
	return rm


def batch_run(context, batch_parameters):
	'''
	Runs the analysis pipeline for each img inside the raw_images key
	then updates the parameter dictionary and saves it.
	'''
	IJ.log("Running pipeline...")
	images = batch_parameters.get("raw_images")
	total_images = len(images)
	if not batch_parameters.get("analysed_images"):
		analysed_images = []
	else:
		analysed_images = batch_parameters.get("analysed_images")
	i=1
	while len(images) >0:
		progress = "{0}/{1}".format(i, total_images)
		IJ.log("Progress: {0}".format(progress))
		imp = imageloader(images[0])
		if not run(context, imp, batch_parameters.get("output_folder"),
			batch_parameters.get("analysis_ch"), batch_parameters.get("th_method"),
			batch_parameters.get("stroke_width"), batch_parameters.get("tracing_ch")):
			IJ.log("Batch run canceled.")
			batch_parameters.to_json_file(batch_parameters.get("output_folder"))
			return
		i += 1
		analysed_images.append(images[0])
		batch_parameters.set("analysed_images", analysed_images)
		images.pop(0)
		batch_parameters.set("raw_images", images)
	batch_parameters.to_json_file(batch_parameters.get("output_folder"))
	IJ.log("Done ...")
	IJ.log("Results stored in '{0}'".format(batch_parameters.get("output_folder")))


def profile_from_threshold(imp, analysis_ch, rois, stroke_width, th_method, csvs_output):
	'''
	Thresholds the desired channel using the threshold method specified and saves the
	roi profile in the csv_output.
	Rois will be set to the width in pixels specified by stroke_width.
	'''
	n_ch = imp.getNChannels()
	if n_ch < analysis_ch:
		raise ValueError("Analysis ch cannot be bigger than total number of channels.")
	analysis_imp = get_analysis_ch(imp, analysis_ch)
	apply_threshold(analysis_imp, th_method)
	rm = get_clean_RoiManager()
	for roi in rois:
		roi.setStrokeWidth(stroke_width)
		IJ.log("\n#Roi properties:\n##Name:{0}\n##Width:{1}\n##Length:{2}".format(roi.getName(), roi.getStrokeWidth(), roi.getLength()))
		profile = get_profile(analysis_imp, roi, rm)
		export_profile(profile, roi.getName(), csvs_output)
	analysis_imp.changes = False
	analysis_imp.close()
	return True


def batch_profile_from_threshold(batch_parameters):
	'''
	Thresholds the desired channel using the threshold method specified and saves the
	roi profile in the csv_output.
	Rois will be set to the width in pixels specified by stroke_width.
	Provide a batch parameters dict to operate on images.

	WIP:
	PUT A BETTER ALGO IN PLACE TO DETERMINE THE CORRECT ROI TO USE.
	'''
	from ij.io import Opener
	from IBPlib.ij.Utils.Files import buildList

	opener = Opener()
	rois_folder, csvs_folder = setup_output_folders(batch_parameters.get("output_folder"))
	IJ.log("Plotting profiles...")

	for i, img in enumerate(batch_parameters.get("analysed_images")):
		progress = "{0}/{1}".format(i+1, len(batch_parameters.get("analysed_images")))
		IJ.log("\n# Progress: {0}\n".format(progress))

		imp = imageloader(img)
		#title = os.path.basename(os.path.splitext(img)[0])
		title = os.path.basename(img)
		IJ.log("\nMeasuring -> {0}".format(title))
		rois_path_list = buildList(rois_folder, extension=".roi")
		rois = [opener.openRoi(roi) for roi in rois_path_list if roi.find(title) > 0]
		if not rois:
			IJ.log("## No rois found for {0}".format(title))

		if not profile_from_threshold(imp, batch_parameters.get("analysis_ch"),
			rois, batch_parameters.get("stroke_width"),
			batch_parameters.get("th_method"), csvs_folder):
			IJ.log("Batch run canceled.")
			return

	IJ.log("Done ...")
	IJ.log("{0}".format(csvs_folder))


if __name__ in ("__builtin__", "__main__"):
	imp = IJ.getImage()
	analysis_imp = get_analysis_ch(imp, 2)
	apply_threshold(analysis_imp, "Li")
	analysis_imp.show()

