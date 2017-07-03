from flask import Flask, request
import datetime
import decimal
from flask_json import FlaskJSON, JsonError, json_response, as_json
import json
import jsonpickle
import os
from pathlib import Path
from moxchurn import app
from moxchurn.models import *

app_dir = Path(__file__).parent.parent
data_dir = app_dir / '.mox-churn-data'

offer_storage = JsonOfferStorage(data_dir / 'offers')

@app.route('/')
def index():
	return "Mox Churn"

@app.route('/offer/<offer_type>/<offer_name>', methods=['GET'])
def get_offer(offer_type, offer_name):
	offer = offer_storage.load_single(offer_type, offer_name)

	return json_response(offer=offer)

@app.route('/offer', methods=['POST'])
def create_offer():
	input_json = request.get_json()
	cc_offer_args = input_json.copy()

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

	parse_and_rename(cc_offer_args, 'bonus_requirement_fulfillment_duration_days', 'bonus_requirement_fulfillment_duration', timedelta_from_days)
	parse_and_rename(cc_offer_args, 'bonus_requirement_account_open_duration_days', 'bonus_requirement_account_open_duration', timedelta_from_days)
	parse(cc_offer_args, 'offer_start_date', parse_date)
	parse(cc_offer_args, 'offer_end_date', parse_date)
	parse(cc_offer_args, 'annual_fee', parse_money)
	parse(cc_offer_args, 'annual_fee_first_year', parse_money)
	parse(cc_offer_args, 'cash_bonus_amount', parse_money)
	parse(cc_offer_args, 'bonus_requirement_purchase_amount', parse_money)
	parse(cc_offer_args, 'bonus_requirement_purchase_count', int)

	cc_offer = CreditCardOffer(**cc_offer_args)
	file_name = offer_storage.save(cc_offer)

	return json_response(created = True, fileName = file_name)

@app.route('/offers')
@app.route('/offers/<offer_type>')
def get_offers(offer_type=None):
	def validate_string(s):
		if s == '':
			return None
		return s

	issuer = validate_string(request.args.get('issuer'))

	return json_response(offers=offer_storage.load(offer_type, issuer = issuer))
