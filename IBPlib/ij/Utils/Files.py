# Files utlities
# Igor Bonacossa-Pereira
# i.bonacossapereira@uq.edu.au
import os

def buildList(path, extension=".tif", exclusionFlag="done"):
	'''
	Returns a list with all the binary paths to files in the given path of the choosen extension that do not contain
	the exclusion flag in the title 
	'''
	if not os.path.exists(path):
		raise IOError("buildList couldn't find {0}".format(path))
	files = []
	for f in os.listdir(path):
		if not f.endswith(extension) or f.find(exclusionFlag)>0:
			continue
		files.append(os.path.join(path, f))
	return files