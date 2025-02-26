from enum import Enum


class EMAIL_STATUS(Enum):
    SENT = "SENT"
    PENDING = "PENDING"
    FAILED= "FAILED"





EMAIL_PREFIX = "email:"
PENDING_EMAILS = "pending_emails"
PROCESSING_EMAILS = "processing_emails"
FAILED_EMAILS = "failed_emails"
BATCH_SIZE = 10
SCHEDULER_INTERVAL_SECONDS = 60


