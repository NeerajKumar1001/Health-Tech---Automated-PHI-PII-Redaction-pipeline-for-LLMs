import logging
import uuid
from datetime import datetime

# Set up the logging configuration
logging.basicConfig(
    filename='proxy_audit.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("PHIAudit")

def log_transaction(endpoint: str, original_length: int, safe_length: int):
    """
    Logs metadata about the redaction event for compliance tracking.
    Strictly avoids logging the actual text content.
    """
    # Generate a unique transaction ID for tracking
    transaction_id = str(uuid.uuid4())[:8]
    
    log_message = (
        f"TXN: {transaction_id} | "
        f"Endpoint: {endpoint} | "
        f"Inbound chars: {original_length} | "
        f"Outbound chars: {safe_length} | "
        f"Status: SUCCESS"
    )
    
    logger.info(log_message)
    return transaction_id