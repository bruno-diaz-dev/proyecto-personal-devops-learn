from flask import Blueprint, jsonify, current_app
from app import db
from datetime import datetime
import psutil
import time

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api')

# Variable global para tracking de uptime
start_time = time.time()

# --------------------------------------------------
# LIVENESS PROBE (CI / Docker / Load Balancer)
# --------------------------------------------------
@monitoring_bp.route('/health', methods=['GET'])
def health_check():
    """Liveness probe - application is running"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'uptime': time.time() - start_time
    }), 200


# --------------------------------------------------
# READINESS PROBE (Production / Dependencies)
# --------------------------------------------------
@monitoring_bp.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness probe - checks database connectivity"""
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
        status_code = 200
    except Exception:
        db_status = 'unhealthy'
        status_code = 503

    return jsonify({
        'status': 'ready' if db_status == 'healthy' else 'not_ready',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }), status_code


# --------------------------------------------------
# METRICS ENDPOINT (Prometheus style)
# --------------------------------------------------
@monitoring_bp.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()

        # Application metrics (safe access)
        User = getattr(current_app, 'User', None)
        Task = getattr(current_app, 'Task', None)

        user_count = User.query.count() if User else 0
        task_count = Task.query.count() if Task else 0
        completed_tasks = Task.query.filter_by(completed=True).count() if Task else 0

        metrics_text = f"""# HELP flask_app_users_total Total number of users
# TYPE flask_app_users_total counter
flask_app_users_total {user_count}

# HELP flask_app_tasks_total Total number of tasks
# TYPE flask_app_tasks_total counter
flask_app_tasks_total {task_count}

# HELP flask_app_tasks_completed Total number of completed tasks
# TYPE flask_app_tasks_completed counter
flask_app_tasks_completed {completed_tasks}

# HELP flask_app_cpu_usage CPU usage percentage
# TYPE flask_app_cpu_usage gauge
flask_app_cpu_usage {cpu_percent}

# HELP flask_app_memory_usage Memory usage percentage
# TYPE flask_app_memory_usage gauge
flask_app_memory_usage {memory.percent}

# HELP flask_app_uptime Application uptime in seconds
# TYPE flask_app_uptime counter
flask_app_uptime {time.time() - start_time}
"""
        return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except Exception as e:
        return f"# Error generating metrics: {str(e)}", 500, {'Content-Type': 'text/plain; charset=utf-8'}
