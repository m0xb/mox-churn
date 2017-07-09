from pathlib import Path
import jsonpickle
import re
import datetime


class Offer(object):
	VERSION = 7

	@staticmethod
	def get_class_for_offer_type(offer_type):
		mapping = {t.get_offer_type(): t for t in [CreditCardOffer, CheckingAccountOffer, SavingAccountOffer]}
		if offer_type not in mapping:
			raise Exception(f"Unrecognized offer type: {offer_type}")
		return mapping[offer_type]

	def __init__(self):
		self.version = self.VERSION
		self.created_date = datetime.datetime.now()

	def to_json_encodable(self):
		d = self.__dict__
		d.pop('version')
		d.pop('created_date')
		# FIXME: Hack for SQLAlchemy junk
		if '_sa_instance_state' in d:
			d.pop('_sa_instance_state')
		return d

class CreditCardOffer(Offer):

	def __init__(self, name, card_type, issuer, offer_start_date, offer_end_date, cash_bonus_amount, bonus_requirement_purchase_amount, bonus_requirement_purchase_count, bonus_requirement_fulfillment_duration, bonus_requirement_account_open_duration, annual_fee, annual_fee_first_year, offer_url):
		super().__init__()
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

	@staticmethod
	def get_offer_type():
		return 'credit'

class BankAccountOffer(Offer):

	def __init__(self, name, bank, offer_start_date, offer_end_date, cash_bonus_amount, bonus_requirement_purchase_amount, bonus_requirement_deposit_amount, bonus_requirement_direct_deposit, bonus_requirement_purchase_count, bonus_requirement_fulfillment_duration, bonus_requirement_account_open_duration, monthly_fee, offer_url):
		super().__init__()
		self.name = name
		self.bank = bank
		self.offer_start_date = offer_start_date
		self.offer_end_date = offer_end_date
		self.cash_bonus_amount = cash_bonus_amount
		self.bonus_requirement_purchase_amount = bonus_requirement_purchase_amount
		self.bonus_requirement_deposit_amount = bonus_requirement_deposit_amount
		self.bonus_requirement_direct_deposit = bonus_requirement_direct_deposit
		self.bonus_requirement_purchase_count = bonus_requirement_purchase_count
		self.bonus_requirement_fulfillment_duration = bonus_requirement_fulfillment_duration
		self.bonus_requirement_account_open_duration = bonus_requirement_account_open_duration
		self.monthly_fee = monthly_fee
		self.offer_url = offer_url

class CheckingAccountOffer(BankAccountOffer):
	@staticmethod
	def get_offer_type():
		return 'checking'

class SavingAccountOffer(BankAccountOffer):
	@staticmethod
	def get_offer_type():
		return 'savings'
