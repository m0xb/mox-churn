from flask import Flask
from flask_json import FlaskJSON
from decimal import Decimal
from datetime import datetime, timedelta
from moxchurn.blueprints.offers import offers

def create_app(offer_storage):
	app = Flask(__name__)
	app.config.update(dict(
		OFFER_STORAGE=offer_storage,
	))
	json = FlaskJSON(app)

	app.register_blueprint(offers)
	app.offer_storage = offer_storage

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
