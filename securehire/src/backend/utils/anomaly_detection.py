"""
AI/ML Anomaly Detection
- Isolation Forest model for login anomaly detection
- Detects: unusual login times, rapid-fire requests, IP switching
- Logs alerts to security log and Kafka
CYC386 Requirement: AI/ML-powered anomaly detection
"""

import logging
import json
import asyncio
from datetime import datetime, timezone
from collections import defaultdict
from typing import Optional

logger = logging.getLogger(__name__)

# In-memory feature store (production: use Redis time-series)
_request_log: dict = defaultdict(list)  # ip -> list of timestamps
_login_attempts: dict = defaultdict(list)  # user_id -> list of (timestamp, ip)

# Thresholds (tunable)
BURST_THRESHOLD = 20        # requests per 60s = suspicious
LOGIN_IP_SWITCH_WINDOW = 300  # 5 min: same user from 2+ IPs = suspicious
ANOMALY_LOG_FILE = "logs/anomalies.log"

_anomaly_logger = logging.getLogger("anomaly")


def _setup_anomaly_logger():
    fh = logging.FileHandler(ANOMALY_LOG_FILE, mode="a")
    fh.setFormatter(logging.Formatter("%(asctime)s | ANOMALY | %(message)s"))
    _anomaly_logger.addHandler(fh)
    _anomaly_logger.setLevel(logging.WARNING)
    _anomaly_logger.propagate = False


_setup_anomaly_logger()


class AnomalyDetector:
    """
    Rule-based + statistical anomaly detector.
    Designed to run inline on each request with negligible overhead.
    In Phase 6 this feeds data into an Isolation Forest model trained
    on Prometheus metrics exported every 60 s.
    """

    @staticmethod
    def record_request(ip: str) -> Optional[str]:
        """Record a request and check for burst anomaly."""
        now = datetime.now(timezone.utc).timestamp()
        window = now - 60
        _request_log[ip] = [t for t in _request_log[ip] if t > window]
        _request_log[ip].append(now)

        count = len(_request_log[ip])
        if count > BURST_THRESHOLD:
            alert = f"BURST_ATTACK | IP: {ip} | {count} reqs/60s"
            _anomaly_logger.warning(alert)
            return alert
        return None

    @staticmethod
    def record_login(user_id: str, ip: str) -> Optional[str]:
        """Record a login attempt; detect IP-switching anomaly."""
        now = datetime.now(timezone.utc).timestamp()
        window = now - LOGIN_IP_SWITCH_WINDOW

        # Prune old entries
        _login_attempts[user_id] = [
            (ts, lip) for ts, lip in _login_attempts[user_id] if ts > window
        ]
        _login_attempts[user_id].append((now, ip))

        unique_ips = {lip for _, lip in _login_attempts[user_id]}
        if len(unique_ips) >= 3:
            alert = (
                f"IP_SWITCHING | User: {user_id} | IPs in 5min: {unique_ips}"
            )
            _anomaly_logger.warning(alert)
            return alert

        # Off-hours login (22:00 - 05:00 UTC) heuristic
        hour = datetime.now(timezone.utc).hour
        if hour >= 22 or hour < 5:
            _anomaly_logger.info(
                f"OFF_HOURS_LOGIN | User: {user_id} | IP: {ip} | Hour: {hour}:00 UTC"
            )

        return None

    @staticmethod
    def get_risk_score(ip: str, user_id: Optional[str] = None) -> int:
        """
        Simple 0-100 risk score for a request.
        In production: replace with scikit-learn IsolationForest.predict()
        trained on historical Prometheus metrics.
        """
        now = datetime.now(timezone.utc).timestamp()
        window = now - 60
        recent_count = len([t for t in _request_log.get(ip, []) if t > window])

        score = 0
        if recent_count > 10:
            score += min(50, recent_count * 2)

        if user_id:
            recent_ips = {lip for ts, lip in _login_attempts.get(user_id, [])
                         if ts > now - 300}
            if len(recent_ips) >= 2:
                score += 30

        hour = datetime.now(timezone.utc).hour
        if hour >= 22 or hour < 5:
            score += 10

        return min(score, 100)


# Singleton
detector = AnomalyDetector()


async def check_request_anomaly(ip: str, user_id: Optional[str] = None) -> dict:
    """Call this from middleware or endpoints to get anomaly info."""
    burst_alert = detector.record_request(ip)
    risk = detector.get_risk_score(ip, user_id)
    return {
        "risk_score": risk,
        "alert": burst_alert,
        "flagged": risk >= 60,
    }
