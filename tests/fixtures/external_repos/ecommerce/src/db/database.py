from src.config.settings import settings


def connect_database():
    return {"url": settings.database_url, "connected": True}


def run_migration(name: str):
    return {"migration": name, "status": "applied"}
