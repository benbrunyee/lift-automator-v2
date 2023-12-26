import argparse
import logging
import os
import sys

from cryptography.fernet import Fernet
from lib.FbHelpers import FbHelpers

parser = argparse.ArgumentParser()
parser.add_argument(
    "--debug",
    help="Enable debug logging.",
    action="store_true",
)

args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(re.sub(r"\.py$", "", sys.argv[0]) + ".log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


FB_HELPER = FbHelpers()
DRIVER = None
FERNET = None

KEY_PATH = "../service-account-key.json"

if not os.path.exists(KEY_PATH):
    logger.error("No service account key found. Exiting.")
    exit(1)

# Set the service account key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

# Set the service account key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./service-account-key.json"


def main():
    global DRIVER
    DRIVER = FB_HELPER.load_chromedriver()

    # Listen for messages from the queue


def decrypt_string(string: str) -> str:
    if not FERNET:
        logger.info("Loading Fernet key.")
        with open("./key.txt", "rb") as f:
            key = f.read()
            FERNET = Fernet(key)

    return FERNET.decrypt(string.encode()).decode()


if __name__ == "__main__":
    main()
