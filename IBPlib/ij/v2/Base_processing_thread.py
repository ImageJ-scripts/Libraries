import os

# Bootstrap to extend modules search path #
from sys import path
from java.lang.System import getProperty
jython_scripts = os.path.join(getProperty('user.home'), 'Jython_scripts')
path.append(jython_scripts)
#=========================================#

class Base_processing_thread:
	pass