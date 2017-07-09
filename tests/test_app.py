import json
import moxchurn
from moxchurn.common import get_storage
import os
from pathlib import Path
import random
import unittest
import tempfile

class AppTestCase(unittest.TestCase):

	def setUp(self):
		self.tmp_data_dir = tempfile.TemporaryDirectory()
		self.app = moxchurn.create_app(get_storage(data_dir=Path(self.tmp_data_dir.name)))
		self.client = self.app.test_client()

	def tearDown(self):
		self.app.offer_storage.session.close()
		self.client = None
		self.app = None
		self.tmp_data_dir.cleanup()

	def test_not_found(self):
		result = self.client.get('/offer/credit/DOES_NOT_EXIST')
		self.assertEqual(404, result.status_code)
		data = json.loads(result.get_data())
		self.assertEqual(None, data['offer'])

	def test_cc_offer(self):
		result = self.client.post('/offer/credit',
			data=json.dumps({
				'name': 'Chase Sapphire Preferred',
				'card_type': 'Visa',
				'issuer': 'Chase',
				'offer_start_date': '2017-01-01',
				'offer_end_date': '2017-12-31',
				'cash_bonus_amount': 500.00,
				'bonus_requirement_purchase_amount': 4000.00,
				'bonus_requirement_purchase_count': 0,
				'bonus_requirement_fulfillment_duration_days': 90,
				'bonus_requirement_account_open_duration_days': 180,
				'annual_fee': 95.00,
				'annual_fee_first_year': 0.00,
				'offer_url': 'https://creditcards.chase.com/a1/sapphire/compare?CELL=64DW'
			}),
			content_type='application/json'
		)
		self.assertEqual(200, result.status_code)
		data = json.loads(result.get_data())
		self.assertEqual(True, data['created'])
		self.assertEqual('Chase Sapphire Preferred', data['name'])

		result = self.client.get('/offer/credit/Chase Sapphire Preferred')
		self.assertEqual(200, result.status_code)
		data = json.loads(result.get_data())
		self.assertEqual('Chase Sapphire Preferred', data['offer']['name'])
		self.assertEqual('Visa', data['offer']['card_type'])
		self.assertEqual('Chase', data['offer']['issuer'])
		self.assertEqual('2017-01-01', data['offer']['offer_start_date'])
		self.assertEqual('2017-12-31', data['offer']['offer_end_date'])
		self.assertEqual(500, data['offer']['cash_bonus_amount'])
		self.assertEqual(4000, data['offer']['bonus_requirement_purchase_amount'])
		self.assertEqual(0, data['offer']['bonus_requirement_purchase_count'])
		self.assertEqual(90, data['offer']['bonus_requirement_fulfillment_duration'])
		self.assertEqual(180, data['offer']['bonus_requirement_account_open_duration'])
		self.assertEqual(95, data['offer']['annual_fee'])
		self.assertEqual(0, data['offer']['annual_fee_first_year'])
		self.assertEqual('https://creditcards.chase.com/a1/sapphire/compare?CELL=64DW', data['offer']['offer_url'])

	def test_checking_offer(self):
		result = self.client.post('/offer/checking',
			data=json.dumps({
				'name': 'Everyday Checking',
				'bank': 'Wells Fargo',
				'offer_start_date': '2017-01-01',
				'offer_end_date': '2017-12-31',
				'cash_bonus_amount': 200.00,
				'bonus_requirement_purchase_amount': 2000.00,
				'bonus_requirement_deposit_amount': 0.00,
				'bonus_requirement_direct_deposit': False,
				'bonus_requirement_purchase_count': 0,
				'bonus_requirement_fulfillment_duration_days': 90,
				'bonus_requirement_account_open_duration_days': 180,
				'monthly_fee': 10.00,
				'offer_url': 'https://www.wellsfargo.com/checking/everyday/'
			}),
			content_type='application/json'
		)
		self.assertEqual(200, result.status_code)
		data = json.loads(result.get_data())
		self.assertEqual(True, data['created'])
		self.assertEqual('Everyday Checking', data['name'])

		result = self.client.get('/offer/checking/Everyday Checking')
		self.assertEqual(200, result.status_code)
		data = json.loads(result.get_data())
		self.assertEqual('Everyday Checking', data['offer']['name'])
		self.assertEqual('Wells Fargo', data['offer']['bank'])
		self.assertEqual('2017-01-01', data['offer']['offer_start_date'])
		self.assertEqual('2017-12-31', data['offer']['offer_end_date'])
		self.assertEqual(200, data['offer']['cash_bonus_amount'])
		self.assertEqual(2000, data['offer']['bonus_requirement_purchase_amount'])
		self.assertEqual(0, data['offer']['bonus_requirement_deposit_amount'])
		self.assertEqual(False, data['offer']['bonus_requirement_direct_deposit'])
		self.assertEqual(0, data['offer']['bonus_requirement_purchase_count'])
		self.assertEqual(90, data['offer']['bonus_requirement_fulfillment_duration'])
		self.assertEqual(180, data['offer']['bonus_requirement_account_open_duration'])
		self.assertEqual(10, data['offer']['monthly_fee'])
		self.assertEqual('https://www.wellsfargo.com/checking/everyday/', data['offer']['offer_url'])

	def test_search_offers(self):
		TestHelper.create_cc_offer(self.client, 'Offer #1 C', 'Chase')
		TestHelper.create_cc_offer(self.client, 'Offer #2 WF', 'Wells Fargo')
		TestHelper.create_cc_offer(self.client, 'Offer #3 C', 'Chase')
		TestHelper.create_cc_offer(self.client, 'Offer #4 WF', 'Wells Fargo')
		TestHelper.create_cc_offer(self.client, 'Offer #5 B', 'Barclays')

		result = self.client.get('/offers')
		self.assertEqual(200, result.status_code)
		data = json.loads(result.get_data())
		self.assertEqual(5, len(data['offers']))

		result = self.client.get('/offers/credit')
		self.assertEqual(200, result.status_code)
		data = json.loads(result.get_data())
		self.assertEqual(5, len(data['offers']))

		result = self.client.get('/offers?issuer=')
		self.assertEqual(200, result.status_code)
		data = json.loads(result.get_data())
		self.assertEqual(5, len(data['offers']))

		result = self.client.get('/offers?issuer=XXX')
		self.assertEqual(200, result.status_code)
		data = json.loads(result.get_data())
		self.assertEqual(0, len(data['offers']))

		result = self.client.get('/offers?issuer=Chase')
		self.assertEqual(200, result.status_code)
		data = json.loads(result.get_data())
		self.assertEqual(2, len(data['offers']))

		result = self.client.get('/offers?issuer=Barclays')
		self.assertEqual(200, result.status_code)
		data = json.loads(result.get_data())
		self.assertEqual(1, len(data['offers']))


class TestHelper:
	@staticmethod
	def create_cc_offer(test_client, offer_name, issuer):
		result = test_client.post(f'/offer/credit',
			data=json.dumps({
				'name': offer_name,
				'card_type': random.choice(['Visa', 'American Express']),
				'issuer': issuer,
				'offer_start_date': '2017-01-01',
				'offer_end_date': '2017-12-31',
				'cash_bonus_amount': random.randrange(1, 5) * 100,
				'bonus_requirement_purchase_amount': random.randrange(1, 5) * 1000,
				'bonus_requirement_purchase_count': random.randrange(0, 20),
				'bonus_requirement_fulfillment_duration_days': random.randrange(1, 4) * 30,
				'bonus_requirement_account_open_duration_days': 180,
				'annual_fee': random.choice([0.00, 49.00, 95.00, 300.00]),
				'annual_fee_first_year': 0.00,
				'offer_url': 'https://example.com/creditcards/fake'
			}),
			content_type='application/json'
		)
		if result.status_code != 200:
			raise Exception(f"Error {result.status_code} creating offer: {result.get_data()}")
		return result

if __name__ == '__main__':
	unittest.main()
