from ij import IJ
from ij import Prefs
from ij.gui import GenericDialog, DialogListener
from IBPlib.ij.Constants import LIBPREFSKEY, COLORS

SUBKEY="{0}.colortags".format(LIBPREFSKEY) # Base name for userPrefs key used by Colortags.py

class Colortags:

	def __init__(self):

		self.window = None
		self.tags = {}
		self.prefkeys = ["{0}.{1}".format(SUBKEY, name) for name in COLORS]
		self.userprefs = Prefs()
		self.load()
		while not self.tags:
			self.edit("Please set at least one colortag.\n\n")

	def load(self):
		'''
		Tries to load IBPlib colortags from IJ prefs.
		'''
		for i in range(7):
			storedtags = self.userprefs.getString(".{0}".format(self.prefkeys[i]), "")
			if not storedtags:
				continue
			trimmedtagslist = [t.strip() for t in storedtags.split(",")]
			self.tags.update({i:trimmedtagslist})

	def edit(self, msg=""):
		'''
		Opens the color tags dialog to update color tags
		'''
		self.window = GenericDialog("ColorMerger - Edit color tags")
		self.window.addMessage("{0}Separate tags with a comma.\nBlank values will be ignored.".format(msg))
		for i in range(7):
			try:
				self.window.addStringField(COLORS[i], ", ".join(self.tags[i]), 30)
			except KeyError:
				self.window.addStringField(COLORS[i], "", 30)
		self.window.setOKLabel("Save")
		self.window.showDialog()
		if self.window.wasOKed():
			self.__savetags()
			self.load()

	def __validate(self):

		fields = self.window.getStringFields()
		newvalues = {}
		for i in range(len(fields)):
			txt = fields[i].getText()
			newvalues.update({i: txt.strip()})
		return newvalues

	def __savetags(self):

		newvalues = self.__validate()
		for i, tags in newvalues.items():
			key = self.prefkeys[i]
			self.userprefs.set(key, tags)
			self.userprefs.savePreferences()


if __name__ in ("__builtin__", "__main__"):
	t = Colortags()