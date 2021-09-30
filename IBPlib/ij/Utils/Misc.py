def validate_th_method(th_method):
	'''
	Validates a string against ImageJ valid threshold methods
	'''
	from ij.plugin import Thresholder
	
	if th_method not in Thresholder.methods:
		raise ValueError("Invalid threshold method.")


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

	validate_th_method(th_method)
	ip = imp.getProcessor()
	ip.setAutoThreshold(at.Method.valueOf(th_method), True)
	bp = imp.createThresholdMask()
	imp.setProcessor(bp)


def get_clean_RoiManager(show=False):
	'''
	Returns a clean instance of RoiManager.
	'''
	from ij.plugin.frame import RoiManager
	
	rm = RoiManager.getInstance()
	if not rm:
		rm = RoiManager(show)
	rm.reset()
	return rm


def export_profile(profile_list, title, output, append=False):
	'''
	Exports lists to a csv file specified in profile_csv_path.
	First columnh will be named X and will contain the row number.
	Second column will be named Y and will contain  the list values on each row.
	'''
	import csv
	
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


def get_profile(imp, roi, rm):
	'''
	Gets the profile plot of a roi from a given img.
	returns a list containing the measured intensities on each pixel.
	'''
	from ij.gui import ProfilePlot
	
	i = rm.getCount()
	rm.add(roi, i)
	roi.setName("{0}_{1}".format(imp.getTitle(), i))
	rm.select(imp, i)
	pp = ProfilePlot(imp)
	return pp.getProfile()