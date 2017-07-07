import __init__
import argparse
import datetime
import moxchurn
from moxchurn.common import *
from moxchurn.models import *
import sys

def parse_date(s):
	try:
		return datetime.datetime.strptime(s, "%Y-%m-%d").date()
	except Exception as e:
		raise argparse.ArgumentTypeError(e)

def main(args):
	#print(f"args={args}")

	app_dir = Path(__file__).parent.parent
	data_dir = app_dir / Constants.DEFAULT_DATA_DIR_NAME
	offer_storage = JsonOfferStorage(data_dir / 'offers')
	offer = offer_storage.load_single('credit', args.offer)
	if not offer:
		print(f"No such offer: {args.offer}")
		sys.exit(1)

	application_date = args.date
	bonus_complete_deadline = application_date + offer.bonus_requirement_fulfillment_duration
	account_cancel_ok_date = application_date + offer.bonus_requirement_account_open_duration

	date_fmt = '%Y-%m-%d'
	event_fmt = '{} * {}\n'
	spacer = ' ' * 11 + '|\n'

	timeline = ''
	timeline += event_fmt.format(offer.offer_start_date.strftime(date_fmt), f"Offer issued for {offer.name} credit card")
	timeline += spacer
	timeline += spacer
	timeline += event_fmt.format(application_date.strftime(date_fmt), "Application submitted (hypothetical)")
	timeline += spacer
	timeline += spacer
	timeline += event_fmt.format(bonus_complete_deadline.strftime(date_fmt), f"Deadline to complete offer terms to receive bonus (${offer.cash_bonus_amount})")
	timeline += spacer
	timeline += spacer
	timeline += event_fmt.format(account_cancel_ok_date.strftime(date_fmt), "Credit card may be cancelled")
	print(timeline)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Display a timeline of important dates for the specified offer')
	parser.add_argument('offer', help='Name of the offer')
	parser.add_argument('date', help='Hypothetical date to submit an application', type=parse_date)
	main(parser.parse_args())
