import __init__
import argparse
import datetime
import moxchurn
from moxchurn.common import *
from moxchurn.persistence.sqlite import *
from moxchurn.models import *
import sys

def main(args):
	#print(f"args={args}")

	offer_storage = get_storage()

	offers = list(offer_storage.load(CreditCardOffer))
	print(f"{len(offers)} offer(s): {offers}")


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Interactive program to query offers database')
	main(parser.parse_args())
