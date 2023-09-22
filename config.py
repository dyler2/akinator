from json import load
from os import getenv
from dotenv import load_dotenv
load_dotenv()

#AKI_MONGO_HOST = os.environ.get('', "")
TOKEN = getenv("BOT_TOKEN", "")