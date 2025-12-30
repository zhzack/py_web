from datetime import datetime


def ping() -> dict:
    return {
        "status": "ok",
        "service": "minimal-web-demo",
        "timestamp": datetime.utcnow().isoformat()
    }


def ping2() -> dict:
    return {
        "status": "ok",
        "service": "minimal-web-demo",
        "timestamp": datetime.utcnow().isoformat()
    }
