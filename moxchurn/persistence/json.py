from moxchurn.models import *

class JsonOfferStorage:

	def __init__(self, data_dir):
		self.data_dir = data_dir
		self.ensure_folder()

	def ensure_folder(self):
		self.data_dir.mkdir(exist_ok=True)

	@staticmethod
	def escape_for_file_name(s):
		return re.sub(r'[^-\w_$]', lambda m: '_' if m.group(0) == ' ' else '', s)

	@staticmethod
	def get_offer_type_prefix(offer_type):
		return Offer.get_class_for_offer_type(offer_type).__name__ + '_'

	def save(self, offer):
		self.ensure_folder()
		file_name = self.get_offer_type_prefix(offer.get_offer_type()) + self.escape_for_file_name(offer.name) + '.json'
		with open(self.data_dir / file_name, 'w') as fp:
			fp.write(jsonpickle.encode(offer))
		return file_name

	def load(self, offer_type = None, issuer = None):
		entities = []
		for file_path in self.data_dir.iterdir():
			if offer_type is None or file_path.name.startswith(self.get_offer_type_prefix(offer_type)):
				entities.append(self.load_from_path(file_path))
		def search_filter(offer):
			if issuer is not None and offer.issuer != issuer:
				return False
			return True
		return filter(search_filter, entities)

	def load_single(self, offer_type, offer_name):
		file_stem = self.get_offer_type_prefix(offer_type) + offer_name
		if file_stem != self.escape_for_file_name(file_stem):
			raise Exception(f"Invalid offer name: {offer_name}")
		file_name = f"{file_stem}.json"
		file_path = self.data_dir / file_name
		if not file_path.exists():
			return None
		return self.load_from_path(file_path)

	def load_from_path(self, file_path):
		with open(file_path, 'r') as fp:
			return jsonpickle.decode(fp.read())
