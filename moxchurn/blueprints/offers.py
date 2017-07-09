from flask import Blueprint, Flask, request, current_app
import datetime
import decimal
from flask_json import FlaskJSON, JsonError, json_response, as_json
import json
import jsonpickle
import os
from pathlib import Path
from moxchurn.models import *


offers = Blueprint('moxchurn', __name__)

@offers.route('/')
def index():
	return "Mox Churn"

@offers.route('/offer/<offer_type>/<offer_name>', methods=['GET'])
def get_offer(offer_type, offer_name):
	offer = current_app.offer_storage.load_single(Offer.get_class_for_offer_type(offer_type), offer_name)
	if not offer:
		return json_response(status_=404, offer = None)
	return json_response(offer=offer)

@offers.route('/offer/<offer_type>', methods=['POST'])
def create_offer(offer_type):
	input_json = request.get_json()
	offer_args = input_json.copy()

	def parse_and_rename(d, old, new, parse):
		v = d.pop(old)
		v = parse(v)
		d[new] = v

	def parse(d, key, parse):
		d[key] = parse(d[key])

	def timedelta_from_days(num_days):
		return datetime.timedelta(days=num_days)

	def parse_date(s):
		return datetime.datetime.strptime(s, '%Y-%m-%d').date()

	def parse_money(s):
		return decimal.Decimal(s)

	def validate_boolean(b):
		if not (b is True or b is False):
			raise Exception(f'Invalid boolean: {b}')
		return b


	parse(offer_args, 'cash_bonus_amount', parse_money)
	parse(offer_args, 'offer_start_date', parse_date)
	parse(offer_args, 'offer_end_date', parse_date)
	parse_and_rename(offer_args, 'bonus_requirement_fulfillment_duration_days', 'bonus_requirement_fulfillment_duration', timedelta_from_days)
	parse_and_rename(offer_args, 'bonus_requirement_account_open_duration_days', 'bonus_requirement_account_open_duration', timedelta_from_days)
	parse(offer_args, 'bonus_requirement_purchase_amount', parse_money)
	parse(offer_args, 'bonus_requirement_purchase_count', int)

	if offer_type == CreditCardOffer.get_offer_type():
		parse(offer_args, 'annual_fee', parse_money)
		parse(offer_args, 'annual_fee_first_year', parse_money)
		offer = CreditCardOffer(**offer_args)
	elif offer_type == CheckingAccountOffer.get_offer_type():
		parse(offer_args, 'bonus_requirement_deposit_amount', parse_money)
		parse(offer_args, 'bonus_requirement_direct_deposit', validate_boolean)
		parse(offer_args, 'monthly_fee', parse_money)
		offer = CheckingAccountOffer(**offer_args)
	else:
		raise JsonError(description=f'Invalid offer type: {offer_type}')

	current_app.offer_storage.save(offer)

	return json_response(
		created = True,
		offerType = offer_type,
		name = offer_args['name'],
	)

@offers.route('/offers')
@offers.route('/offers/<offer_type>')
def get_offers(offer_type=None):
	def validate_string(s):
		if s == '':
			return None
		return s

	issuer = validate_string(request.args.get('issuer'))

	return json_response(offers=current_app.offer_storage.load(Offer.get_class_for_offer_type(offer_type) if offer_type else None, issuer = issuer))
