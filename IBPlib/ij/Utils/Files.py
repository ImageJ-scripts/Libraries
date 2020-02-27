# Files utlities
# Igor Bonacossa-Pereira
# i.bonacossapereira@uq.edu.au
import os


# Boilerplate to extend modules search path #
#from sys import path
#import os.path
#from java.lang.System import getProperty
#jython_scripts = os.path.join(getProperty('user.home'), 'Jython_scripts')
#path.append(jython_scripts)
#=========================================#


from IBPlib.ij.Constants import (__STORAGE_DIR__, __MAGNIFICATION_DIR__)

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

def imageloader(path):
	'''
	Wrapper to deal with opening bioformat images properly in macros
	Returns an ImagePlus if successful and exception if not.
	Read ij.ImagePlus and loci.plugins.BF.openImagePlus for details.
	'''
	from ij import ImagePlus
	from loci.plugins import BF
	ext = os.path.splitext(path)[1]
	if ext in BIOFORMATS:
		return BF.openImagePlus(path)[0]
	else:
		return ImagePlus(path)

def validate_token_group_schema(groups_dict):
	'''
	Validates against the schema below.
	group_dict = dict(
		str: Union[tuple[str], group_dict],
		...
	)
	Future:
	 Maybe use ordered dicts instead?
	'''
	for k,v in groups_dict.items():
		if not isinstance(k,str):
			raise TypeError("Keys of token groups should be of type strings.")
		if not isinstance(v, (tuple, dict)):
			raise TypeError("Tokens should be grouped into tuples with names or another token group dict.")
		for i in v:
			if not isinstance(i, str):
				raise TypeError("Tokens should be strings.")

def tokenize(name, tokens_dict):
	'''
	Scans and tokenize name according to the groups dict.
	Returns dict containing the found tokens indexed by category.
	'''
	validate_token_group_schema(tokens_dict)
	present_tokens = {}
	for token_name, tokens in tokens_dict.items():
		if isinstance(tokens, dict):
			group_name = tokenize(name, tokens).keys()[0]
			present_tokens.update({token_name: group_name})
			continue

		for token in tokens:
			if token in name:
				present_tokens.update({token_name:token})
	return present_tokens

def sort_to_storage(name, groups_dict):
	'''
	Sorts the file to the appropriate storage path.
	Returns the determined storage path.
	Future:
	Abstractaway the final path in order to reutilzie this in
	other situations.
	'''
	tokens = tokenize(name, groups_dict)
	path = os.path.join(
		__STORAGE_DIR__,
		tokens.get("group"),
		tokens.get("marker"),
		tokens.get("stage"),
		__MAGNIFICATION_DIR__,
		tokens.get("flags"), name)

	return path

if __name__ == "__main__":
	name = "111219_let-805_vab-10aGFP_2DOA_worm3_ - 2__cmle.tif"

	groups = {
		"let-805(syb381)": ("syb515", "syb381", "let-805", "M"),
		"let-805": ("QH7062", "syb380", "wt")
	}

	markers = {
		"vab-10a": ("vab-10aGFP", "vab-10a-GFP", "vab-10a"),
		"lam-2-mKate": ("lam-2mKate", "lam-2-mKate")
	}

	flags = {
		"decon": ("cmle", "decon"),
		"raw": ("raw",)
	}

	tokens = {
		"group": groups,
		"marker": markers,
		"stage": ("L4", "2DOA"),
		"flags": flags
	}

	print(sort_to_storage(name, tokens))
	
if __name__ in ("__builtin__", "__main__"):
	path = r"R:\Igor BP\Projects\Let-805\Raw Data\Microscopies\Yokogawa Spinning Disk\let-805\unc-70(s1502)\38AH\63x OIL\decon\z-projections\050220_QH7726_38AH_worm1__cmle.tif"
	imageloader(path).show()
