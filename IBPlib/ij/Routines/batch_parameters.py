import os
import json
from datetime import date

# Refactor to use serial batchfile names instead.
__BATCH_FILENAME = "IBPlib_batch.json"

	
def save(*args, **kwargs):
	'''
	Saves the parameters to a json file using this analysis standard json
	schema.
	'''
	try:
		validate_th_method(kwargs["th_method"])
		parameters = {
			"raw_images": kwargs["raw_images"],
			"analysed_images": [],
			"th_method": kwargs["th_method"],
			"stroke_width":kwargs["stroke_width"],
			"output_folder": kwargs["output_folder"],
			"analysis_ch": kwargs["analysis_ch"],
			"tracing_ch": kwargs["tracing_ch"],
			"last_update":  str(date.today())
		}
	except KeyError:
		raise ValueError("Invalid kwargs. Use any of [0]".format("raw_images=str, th_method=str, stroke_width=int, output_folder=str, analysis_ch=int, tracing_ch=int"))
	
	batchfile = os.path.join(kwargs["output_folder"], __BATCH_FILENAME)
	with open(batchfile, "w") as jsonfile:
		json.dump(parameters, jsonfile, indent=1)
	return parameters

def validate_th_method(th_method):
	from ij.plugin import Thresholder
	if th_method not in Thresholder.methods:
		raise ValueError("Invalid threshold method.")


def save_from_dict(params_dict, params_filepath):
	'''
	Updates an already saved parameters dict from a dict.
	'''
	batchfile = os.path.join(params_filepath, __BATCH_FILENAME)
	stored_params = load(batchfile)
	for k,v in params_dict.items():
		stored_params.update({k:v})
	with open(batchfile, "w") as jsonfile:
		json.dump(stored_params, jsonfile, indent=1)
	return stored_params
	
	
def load(params_filepath):
	'''
	Load the analysis parameters from a jsonfile then return it as a dict.
	'''
	with open(params_filepath, "r") as param_json:
		parameters = json.load(param_json)
	return parameters

def validate_schema(params_dict):
	'''
	WIP
	'''
	__PARAMS_SCHEMA = {
		"raw_images": list,
		"analysed_images": list,
		"th_method": str,
		"stroke_width": int,
		"output_folder": str,
		"analysis_ch": int,
		"tracing_ch": int,
		"last_update":  str
	}
	pass