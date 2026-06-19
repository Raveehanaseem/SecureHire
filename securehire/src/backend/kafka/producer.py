"""
Kafka Producer
Event-driven architecture — publish events on key actions
CYC386 Requirement: Apache Kafka with TLS + ACLs
Topics:
  - job-applications: when someone applies
  - job-postings: when job is created/updated
"""

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
import json
import logging
from datetime import datetime, timezone

from config import settings
from utils.metrics import kafka_events_total

logger = logging.getLogger(__name__)

_producer = None


async def init_kafka_producer():
    global _producer
    try:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            security_protocol=settings.KAFKA_SECURITY_PROTOCOL,
            acks="all",           # Wait for all replicas
            enable_idempotence=True,  # Exactly-once semantics
        )
        await _producer.start()
        logger.info("✅ Kafka producer initialized")
    except Exception as e:
        logger.warning(f"Kafka not available: {e} — events will be skipped")
        _producer = None


async def close_kafka_producer():
    global _producer
    if _producer:
        await _producer.stop()
        logger.info("Kafka producer stopped")


async def publish_event(topic: str, event_type: str, payload: dict):
    """Publish an event to Kafka topic"""
    if not _producer:
        logger.warning(f"Kafka unavailable — skipping event: {event_type}")
        kafka_events_total.labels(topic=topic, event_type=f"{event_type}_SKIPPED").inc()
        return

    event = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }

    try:
        await _producer.send_and_wait(topic, event)
        logger.info(f"Event published | Topic: {topic} | Type: {event_type}")
        kafka_events_total.labels(topic=topic, event_type=event_type).inc()
    except KafkaError as e:
        logger.error(f"Kafka publish failed: {e}")
        kafka_events_total.labels(topic=topic, event_type=f"{event_type}_FAILED").inc()


# ─── Event Helpers ─────────────────────────────────────────────────────────────

async def emit_application_submitted(application_id: str, job_id: str, applicant_id: str):
    await publish_event(
        settings.KAFKA_TOPIC_APPLICATIONS,
        "APPLICATION_SUBMITTED",
        {"application_id": application_id, "job_id": job_id, "applicant_id": applicant_id}
    )


async def emit_job_posted(job_id: str, employer_id: str, title: str):
    await publish_event(
        settings.KAFKA_TOPIC_JOBS,
        "JOB_POSTED",
        {"job_id": job_id, "employer_id": employer_id, "title": title}
    )


async def emit_application_status_changed(application_id: str, new_status: str):
    await publish_event(
        settings.KAFKA_TOPIC_APPLICATIONS,
        "APPLICATION_STATUS_CHANGED",
        {"application_id": application_id, "status": new_status}
    )
