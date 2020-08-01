import os
import json
from datetime import date

# Refactor to use serial batchfile names instead.
__BATCH_FILENAME = "IBPlib_batch.json"


class Batch_Parameters(object):

	def __init__(self, schema, output_folder="", batch_name="IBPlib_batch"):
		'''
		Instanciates Batch_parameters from a dict schema.
		Resulting class has each key of the dict as a property with 
		a proper validator set with a setter for that property.
		Basic parameters already set:
			raw_iamges -> Stack to store images to be analysed.
			analysed_images -> List to store analysed images.
			output_folder -> Path where output and Batch_parameters are to be saved.
		'''
		self.validate_parameters_schema(schema)
		self._raw_images = []
		self._analysed_images = []
		self._output_folder = "default"
		self._parameters = {}
		
		[self._parameters.update({k:(v,None)}) for k, v in schema.items()]
		
		self._parameters.update({"last_update": (str, str(date.today()))})
		self.name = batch_name
	

	@property
	def raw_images(self):
		return self._raw_images


	def next_raw_image(self):
		'''
		Pops an item from raw_images and returns it.
		If stack is empty returns none
		'''
		return self._raw_images.pop()


	@raw_images.setter
	def raw_images(self, image_list):
		if not isinstance(image_list, list):
			raise TypeError("raw_images can only take a list of images.")
		self._raw_images = image_list

	
	@raw_images.deleter
	def raw_images(self):
		self._raw_images = []

	
	@property
	def analysed_images(self):
		return self._analysed_images


	@analysed_images.setter
	def analysed_images(self, image_list):
		if not isinstance(image_list, list):
			raise TypeError("raw_images can only take a list of images.")
		self._analysed_images = image_list


	def append_analysed_image(self, image):
		self._analysed_images.append(image)

		
	def append_raw_image(self, image):
		self._raw_images.append(image)

			
	@analysed_images.deleter
	def analysed_images(self):
		self._analysed_images = []

		
	@property
	def output_folder(self):
		return self._output_folder
	
	
	@output_folder.setter
	def output_folder(self, destination_path):
		if os.path.exists(destination_path):
			real_path = destination_path
		else:
			real_path = os.path.realpath(destination_path)
		
		if not os.path.exists(real_path) or not os.path.isdir(real_path):
			raise IOError("{0} is not a valid path.".format(real_path))
				
		self._output_folder = destination_path

	
	def validate_parameters_schema(self, params_schema):
		'''
		Validates a parameter schema dict.
		If validation fails a SchemaError exception will be raised.
		'''
		if not isinstance(params_schema, dict):
			raise SchemaError("Schema should be a dict.")
			
		
	def __repr__(self):
		msg = "Batch Name: {0}\n".format(self.name)
		for k,v in self.__parameters__.items():
			line = "# {0}:\t{1}\n".format(k,v[1])
			msg += line
		msg.join("#######")
		return msg
				
				
	def set(self, attr, value):
		'''
		Setter for parameters set by the user.
		For standard parameters access their special setters.
		'''
		try:
			attr_type = self._parameters.get(attr)[0]
		except TypeError:
			raise KeyError("{0} is not a parameter for {1}".format(attr, self.name))
			
		value_type = type(value)
		if not isinstance(value, self._parameters.get(attr)[0]):
			raise TypeError("Parameter is of wrong type.")
			
		self._parameters.update({attr:(attr_type, value), "last_update": (str, str(date.today()))})
	

	def get(self, attr):
		'''
		Getter for parameters set by the user.
		For standard parameters access their special getters.
		'''
		try:
			return self._parameters.get(attr)[1]
		except TypeError:
			raise KeyError("{0} is not a parameter for {1}".format(attr, self.name))
			
			
	def to_json_file(self, output_folder):
		'''
		Saves the parameters to a json file.
		'''
		filename = "{0}.json".format(self.name)
		filepath = os.path.join(output_folder, filename)
		with open(filepath, "w") as jsonfile:
			params = {k:v[1] for k,v in self._parameters.items()}
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

class SchemaError(Exception):
	pass
		
	
if __name__ in ("__builtin__", "__main__"):
	savepath = r"C:\Users\Igor\Jython_scripts\IBPlib\ij\Routines\test"
	schema = {"stroke_width": int,
		"th_method": str}
	bp = Batch_Parameters(schema, output_folder=savepath)
	bp.raw_images = ["img1", "img2", "img3"]
	bp.set("th_method", "Otsu")

	while bp.raw_images:
		img = bp.next_raw_image()
		print(img)
	
