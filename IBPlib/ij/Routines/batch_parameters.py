import os
import json
from datetime import date

# Refactor to use serial batchfile names instead.
__BATCH_FILENAME = "IBPlib_batch.json"


class Batch_Parameters:
	'''
	Main object to store batch run parameters used in IBPlib routines.
	'''
	def __init__(self,schema, batch_name="IBPlib_batch"):
		'''
		Instanciates Batch_parameters from a dict schema.
		Resulting class has each key of the dict as a property with 
		a proper validator set with a setter for that property.
		'''
		if not isinstance(schema, dict):
			raise ValueError("Schema should be a dict.")
		self.__parameters__ = {}
		for k, v in schema.items():
			self.__parameters__.update({k:(v,None)})
		self.__parameters__.update({"last_update": (str, str(date.today()))})
		self.name = batch_name

	def __str__(self):
		msg = "Batch Name: {0}\n".format(self.name)
		for k,v in self.__parameters__.items():
			line = "# {0}:\t{1}\n".format(k,v[1])
			msg += line
		msg.join("#######")
		return msg
				
	def set(self, attr, value):
		attr_type = self.__parameters__.get(attr)[0]
		value_type = type(value)
		#if value_type != attr_type and value and not self.__parameters__.get(attr)[1]:
		#	raise ValueError("{0} should be of {1}. {2} {3} given.".format(attr, attr_type, value_type, value))
		self.__parameters__.update({attr:(attr_type, value), "last_update": (str, str(date.today()))})

		
	def get(self, attr):
		return self.__parameters__.get(attr)[1]
			

	def to_json_file(self, output_folder):
		'''
		Saves the parameters to a json file.
		'''
		filename = "{0}.json".format(self.name)
		filepath = os.path.join(output_folder, filename)
		with open(filepath, "w") as jsonfile:
			params = {k:v[1] for k,v in self.__parameters__.items()}
			json.dump(params, jsonfile, indent=1)
		return True


	@classmethod
	def from_json(cls, json_file):
		'''
		Load the analysis parameters from a jsonfile then return it as a dict.
		'''
		with open(json_file, "r") as param_json:
			parameters = json.load(param_json)
		name = os.path.splitext(os.path.basename(json_file))[0]
		schema = {}
		[schema.update({k:type(v)}) for k, v in parameters.items()]
		bp = cls(schema, batch_name=name)
		[bp.set(k,v) for k,v in parameters.items() if k != "last_update"]
		#bp.set("last_update", str(parameters["last_update"]))
		return bp
	
	@classmethod
	def from_dict(params_dict, params_filepath):
		'''
		WIP
		Updates an already saved parameters dict from a dict.
		'''
		raise NotImplementedError
		batchfile = os.path.join(params_filepath, __BATCH_FILENAME)
		stored_params = load(batchfile)
		for k,v in params_dict.items():
			stored_params.update({k:v})
		with open(batchfile, "w") as jsonfile:
			json.dump(stored_params, jsonfile, indent=1)
		return stored_params	


def get_schema():
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
	}
	return __PARAMS_SCHEMA

	
if __name__ in ("__builtin__", "__main__"):
	savepath = r"I:\LET805IBP-Q1894\Yokogawa\QH7066\38H\let-805 localisation analysis\IBPlib.tracing_and_linescanning.json"
	bp = Batch_Parameters.from_json(savepath)
	print(bp)
