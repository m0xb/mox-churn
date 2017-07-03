from moxchurn import create_app
from pathlib import Path

app_dir = Path(__file__).parent.parent
data_dir = app_dir / '.mox-churn-data'
app = create_app(data_dir)
