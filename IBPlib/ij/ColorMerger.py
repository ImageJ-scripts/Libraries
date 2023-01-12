# @OpService ops

# Bootstrap to extend modules search path #
import os
from sys import path
from java.lang.System import getProperty
jython_scripts = os.path.join(getProperty('user.home'), 'Jython_scripts')
path.append(jython_scripts)
#=========================================#
from net.imagej.ops import Ops as ops

from IBPlib.ij.Colortags import Colortags
from IBPlib.ij.Utils.Files import (buildList, imageloader)
	
			


if __name__ in ("__builtin__", "__main__"):
	print(ops)