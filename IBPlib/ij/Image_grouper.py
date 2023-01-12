# Boilerplate to extend modules search path #
import os
from sys import path
from java.lang.System import getProperty
jython_scripts = os.path.join(getProperty('user.home'), 'Jython_scripts')
path.append(jython_scripts)
#=========================================#
from IBPlib.ij.Utils.Files import buildList
from IBPlib.ij.Colortags import Colortags
from collections import defaultdict

class Image_grouper:
	def __init__(self, img_dir, ext=".tif", debug=False):
		img_list = buildList(img_dir, ext=ext, debug=debug)
		
		self.debug = debug
		self.Colortags = Colortags()
		self.base_dir = img_dir
		self.titles_list = [os.path.split(img)[1] for img in img_list]
		self.group_by_root()
		
		
	def group_by_root(self):
		'''
		Group images based on image title.
		'''
		grouped_imgs = defaultdict(list)
		
		for img in self.titles_list:		
			for index, tagstuple in self.Colortags.tags.items():
				title_root = ["".join(img.split(tag)) for tag in tagstuple if tag in img]
				if not title_root:
					continue
					
				grouped_imgs[title_root.pop()].append(os.path.join(self.base_dir, img))
		self.__groups = grouped_imgs
	
	@property
	def groups(self):
		return self.__groups
		
if __name__ in ("__builtins__", "__main__"):
	
	test_dir = r"C:\Users\uqibonac\Jython_scripts\test"
	ig = Image_grouper(test_dir, ext=".txt")
	print(ig.groups)
	

	