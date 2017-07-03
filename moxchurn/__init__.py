from flask import Flask
from flask_json import FlaskJSON
from decimal import Decimal
from datetime import datetime, timedelta

app = Flask(__name__)
json = FlaskJSON(app)

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

import moxchurn.endpoints

