def validate_th_method(th_method):
	from ij.plugin import Thresholder
	if th_method not in Thresholder.methods:
		raise ValueError("Invalid threshold method.")