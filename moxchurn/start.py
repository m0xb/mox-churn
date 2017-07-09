from moxchurn import create_app
from moxchurn.common import *
from pathlib import Path

app = create_app(get_storage())
