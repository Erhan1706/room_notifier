import logging
import sys

# Logger config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('my_log_file.log', mode='a'),
        logging.StreamHandler(sys.stdout)  # Optional: also print to console
    ]
)

logger = logging.getLogger(__name__)
