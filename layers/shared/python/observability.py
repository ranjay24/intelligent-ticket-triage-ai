import json
import logging
from datetime import datetime
from decimal import Decimal

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cloudwatch = boto3.client("cloudwatch")

NAMESPACE = "TicketTriageAI"


def _json_default(obj):
    """Make log payloads JSON-safe.

    DynamoDB returns numbers as Decimal, and the processor logs
    confidence (a Decimal). Without this, json.dumps raises
    TypeError and the log call crashes the request.
    """
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def log_info(event, **kwargs):

    payload = {
        "level": "INFO",
        "event": event,
        "timestamp": datetime.utcnow().isoformat()
    }

    payload.update(kwargs)

    logger.info(json.dumps(payload, default=_json_default))


def log_error(event, error=None, **kwargs):

    payload = {
        "level": "ERROR",
        "event": event,
        "timestamp": datetime.utcnow().isoformat(),
        "error": str(error)
    }

    payload.update(kwargs)

    logger.error(json.dumps(payload, default=_json_default))


def publish_metric(metric_name, value=1, unit="Count"):

    try:

        cloudwatch.put_metric_data(
            Namespace=NAMESPACE,
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Value": value,
                    "Unit": unit
                }
            ]
        )

    except Exception as e:

        logger.error(
            json.dumps(
                {
                    "event": "METRIC_FAILED",
                    "metric": metric_name,
                    "error": str(e)
                },
                default=_json_default
            )
        )
