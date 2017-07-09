from moxchurn.models import *
from pathlib import Path
from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey, Date, DateTime, Numeric, Interval, Text, Boolean
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, mapper


class SQLiteOfferStorage:

	metadata = None

	def __init__(self, data_dir):
		self.data_dir = data_dir
		self.make_mappers()

		db_file = self.data_dir / 'db.sqlite'
		#print(f"Obtaining SQLite connection to file {db_file}")

		# Note use of three slashes here. See http://docs.sqlalchemy.org/en/latest/core/engines.html
		engine = create_engine('sqlite:///' + str(db_file))
		Session = sessionmaker(bind=engine)
		self.session = Session()

		self.metadata.create_all(bind = engine)

	@classmethod
	def make_mappers(cls):
		if cls.metadata:
			return

		metadata = MetaData()
		credit_card_offer = Table('credit_card_offer', metadata,
			Column('name', String(128), primary_key=True),
			Column('issuer', String(64), primary_key=True),
			Column('card_type', String(16)),
			Column('offer_start_date', Date),
			Column('offer_end_date', Date),
			Column('cash_bonus_amount', Numeric(10,2)),
			Column('bonus_requirement_purchase_amount', Numeric(10,2)),
			Column('bonus_requirement_purchase_count', Integer),
			Column('bonus_requirement_fulfillment_duration', Interval()),
			Column('bonus_requirement_account_open_duration', Interval()),
			Column('annual_fee', Numeric(10,2)),
			Column('annual_fee_first_year', Numeric(10,2)),
			Column('offer_url', Text),
			Column('created_date', DateTime)
		)
		mapper(CreditCardOffer, credit_card_offer)

		checking_account_offer = Table('checking_account_offer', metadata,
			Column('name', String(128), primary_key=True),
			Column('bank', String(128), primary_key=True),
			Column('card_type', String(16)),
			Column('offer_start_date', Date),
			Column('offer_end_date', Date),
			Column('cash_bonus_amount', Numeric(10,2)),
			Column('bonus_requirement_purchase_amount', Numeric(10,2)),
			Column('bonus_requirement_deposit_amount', Numeric(10,2)),
			Column('bonus_requirement_direct_deposit', Boolean),
			Column('bonus_requirement_purchase_count', Integer),
			Column('bonus_requirement_fulfillment_duration', Interval()),
			Column('bonus_requirement_account_open_duration', Interval()),
			Column('monthly_fee', Numeric(10,2)),
			Column('offer_url', Text),
			Column('created_date', DateTime)
		)
		mapper(CheckingAccountOffer, checking_account_offer)

		saving_account_offer = Table('saving_account_offer', metadata,
			Column('name', String(128), primary_key=True),
			Column('bank', String(128), primary_key=True),
			Column('card_type', String(16)),
			Column('offer_start_date', Date),
			Column('offer_end_date', Date),
			Column('cash_bonus_amount', Numeric(10,2)),
			Column('bonus_requirement_purchase_amount', Numeric(10,2)),
			Column('bonus_requirement_deposit_amount', Numeric(10,2)),
			Column('bonus_requirement_direct_deposit', Boolean),
			Column('bonus_requirement_purchase_count', Integer),
			Column('bonus_requirement_fulfillment_duration', Interval()),
			Column('bonus_requirement_account_open_duration', Interval()),
			Column('monthly_fee', Numeric(10,2)),
			Column('offer_url', Text),
			Column('created_date', DateTime)
		)
		mapper(SavingAccountOffer, saving_account_offer)

		def offer_load_listener(offer, context):
			offer.version = Offer.VERSION

		event.listen(CreditCardOffer, 'load', offer_load_listener)
		event.listen(CheckingAccountOffer, 'load', offer_load_listener)

		cls.metadata = metadata

	def save(self, offer):
		self.session.add(offer)
		self.session.commit()

	def load(self, offer_class, issuer = None):
		def query(offer_class):
			query = self.session.query(offer_class)
			if offer_class == CreditCardOffer and issuer:
				return query.filter(CreditCardOffer.issuer == issuer)
			return query

		if not offer_class:
			return query(CreditCardOffer).all() \
				+ query(CheckingAccountOffer).all()
		return query(offer_class).all()

	def load_single(self, offer_class, offer_name):
		return self.session.query(offer_class).filter(offer_class.name == offer_name).one_or_none()
