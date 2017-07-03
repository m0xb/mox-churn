from flask import Flask
from flask_json import FlaskJSON
from decimal import Decimal
from datetime import datetime, timedelta
from moxchurn.blueprints.offers import offers
from moxchurn.models import JsonOfferStorage

def create_app(data_dir):
	app = Flask(__name__)
	app.config.update(dict(
		DATA_DIR=data_dir,
	))
	json = FlaskJSON(app)

	app.register_blueprint(offers)
	app.offer_storage = JsonOfferStorage(data_dir / 'offers')

	@json.encoder
	def custom_encoder(o):
		if isinstance(o, Decimal):
			return float(o)
		elif isinstance(o, datetime):
			return o.isoformat()
		elif isinstance(o, timedelta):
			return o.days
		elif hasattr(o, 'to_json_encodable'):
			return o.to_json_encodable()
		return None

	return app
