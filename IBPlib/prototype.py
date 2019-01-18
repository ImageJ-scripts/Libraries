# Bootstrap to extend modules search path #
from sys import path
import os.path
from java.lang.System import getProperty
jython_scripts = os.path.join(getProperty('user.home'), 'Jython_scripts')
path.append(jython_scripts)
#=========================================#
from ij import IJ
from ij import ImagePlus
from ij.plugin import ChannelSplitter
from ij.plugin.frame import RoiManager
from ij.plugin.filter import (ThresholdToSelection, Analyzer)
from ij.measure import ResultsTable
from IBPlib.ij.Utils.Files import buildList

THRESHOLD_METHOD = "MinError dark"
IJ.run("Set Measurements...", "area mean integrated redirect=None decimal=3")

root = r"C:\Users\uqibonac\OneDrive - The University of Queensland\Hilliard lab\Projects\Let-805\Raw Data\let-805 tagged\WT\decon\L4\63x OIL\zprojector"

images = buildList(root, ".tif")
rm = RoiManager(False)
rt = ResultsTable()
for img in images:
	imp = ImagePlus(img)
	split_imp = ChannelSplitter.split(imp)
	plm = split_imp[0]
	plm_ip = plm.getProcessor()
	skin = split_imp[1]
	sm = ThresholdToSelection()
	plm_ip.setAutoThreshold(THRESHOLD_METHOD)
	plm_roi = sm.convert(plm_ip)
	
	rm.addRoi(plm_roi)
	rm.select(skin, 0)

	# Measure the selection and saves into the RT
	skin_analyzer= Analyzer(skin, rt)
	skin_analyzer.measure()
	
rt.show("WT L4")