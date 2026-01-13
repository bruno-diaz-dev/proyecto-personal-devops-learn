from flask import Blueprint, jsonify
from datetime import datetime
import time
import psutil
import os

monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/api")

start_time = time.time()


@monitoring_bp.route("/health", methods=["GET"])
def health_check():
    """
    Liveness probe.
    Must NEVER depend on DB, cache, external services.
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time() - start_time,
        "service": "backend"
    }), 200


@monitoring_bp.route("/ready", methods=["GET"])
def readiness_check():
    """
    Readiness probe.
    This MAY depend on DB.
    """
    try:
        from app import db
        from sqlalchemy import text

        db.session.execute(text("SELECT 1"))
        db_status = "ready"
        status_code = 200
    except Exception:
        db_status = "not_ready"
        status_code = 503

    return jsonify({
        "status": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }), status_code


@monitoring_bp.route("/metrics", methods=["GET"])
def metrics():
    try:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent

        return f"""# HELP flask_app_cpu_usage CPU usage
# TYPE flask_app_cpu_usage gauge
flask_app_cpu_usage {cpu}

# HELP flask_app_memory_usage Memory usage
# TYPE flask_app_memory_usage gauge
flask_app_memory_usage {memory}

# HELP flask_app_uptime Application uptime
# TYPE flask_app_uptime counter
flask_app_uptime {time.time() - start_time}
""", 200, {"Content-Type": "text/plain"}
    except Exception as e:
        return f"# Metrics error: {e}", 500
