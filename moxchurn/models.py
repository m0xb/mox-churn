from pathlib import Path
import jsonpickle
import re
import datetime


class Offer(object):
	@staticmethod
	def get_class_for_offer_type(offer_type):
		mapping = {t.get_offer_type(): t for t in [CreditCardOffer]}
		if offer_type not in mapping:
			raise Exception(f"Unrecognized offer type: {offer_type}")
		return mapping[offer_type]

	def to_json_encodable(self):
		raise NotImplementedError()

class CreditCardOffer(Offer):

	VERSION = 5

	def __init__(self, name, card_type, issuer, offer_start_date, offer_end_date, cash_bonus_amount, bonus_requirement_purchase_amount, bonus_requirement_purchase_count, bonus_requirement_fulfillment_duration, bonus_requirement_account_open_duration, annual_fee, annual_fee_first_year, offer_url):
		self.version = self.VERSION
		self.name = name
		self.card_type = card_type
		self.issuer = issuer
		self.offer_start_date = offer_start_date
		self.offer_end_date = offer_end_date
		self.cash_bonus_amount = cash_bonus_amount
		self.bonus_requirement_purchase_amount = bonus_requirement_purchase_amount
		self.bonus_requirement_purchase_count = bonus_requirement_purchase_count
		self.bonus_requirement_fulfillment_duration = bonus_requirement_fulfillment_duration
		self.bonus_requirement_account_open_duration = bonus_requirement_account_open_duration
		self.annual_fee = annual_fee
		self.annual_fee_first_year = annual_fee_first_year
		self.offer_url = offer_url
		self.created_date = datetime.datetime.now()

	def to_json_encodable(self):
		d = self.__dict__
		d.pop('version')
		d.pop('created_date')
		return d

	@staticmethod
	def get_offer_type():
		return 'credit'


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
