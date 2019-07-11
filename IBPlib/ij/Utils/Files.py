# Files utlities
# Igor Bonacossa-Pereira
# i.bonacossapereira@uq.edu.au
import os

BIOFORMATS = (".sld", ".ics", ".hdf5", ".czi", ".icd", ".ids")

def buildList(path, extension=".tif", exclusionFlag="done"):
	'''
	Returns a list with all the binary paths to files in the given path of the choosen extension that do not contain
	the exclusion flag in the title
	'''
	if not os.path.exists(path):
		raise IOError("buildList couldn't find {0}".format(path))
	elif not os.path.isdir(path):
		raise IOError("buildList only accepts directory paths")

	files = []
	for f in os.listdir(path):
		if not f.lower().endswith(extension) or f.find(exclusionFlag)>0:
			continue
		files.append(os.path.join(path, f))
	return files

def imageloader(path, ext):
	'''
	Wrapper to deal with opening bioformat images properly in macros
	Returns an ImagePlus if successful and exception if not.
	Read ij.ImagePlus and loci.plugins.BF.openImagePlus for details.
	'''
	from ij import ImagePlus
	from loci.plugins import BF

	if ext in BIOFORMATS:
		return BF.openImagePlus(path)[0]
	else:
		return ImagePlus(path)