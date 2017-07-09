from pathlib import Path
from moxchurn.persistence.sqlite import *
from moxchurn.persistence.json import *

class Constants:
	DEFAULT_DATA_DIR_NAME = '.mox-churn-data'

def get_storage(data_dir=None, type=None, **kwargs):
	if not data_dir:
		app_dir = Path(__file__).parent.parent
		data_dir = (app_dir / Constants.DEFAULT_DATA_DIR_NAME).resolve()
		data_dir.mkdir(exist_ok=True)
	if type == 'json':
		return JsonOfferStorage(data_dir / 'offers')
	else:
		return SQLiteOfferStorage(data_dir)
