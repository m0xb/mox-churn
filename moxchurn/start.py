from moxchurn import create_app
from moxchurn.common import *
from pathlib import Path

app_dir = Path(__file__).parent.parent
data_dir = app_dir / Constants.DEFAULT_DATA_DIR_NAME
data_dir.mkdir(exist_ok=True)
app = create_app(data_dir)
