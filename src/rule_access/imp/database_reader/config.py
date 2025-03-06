import os
from threading import Lock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

PG_DATABASE_URL = os.getenv('PG_DATABASE_URL')

engine = create_engine(PG_DATABASE_URL)
Base = declarative_base()
import rule_access.imp.database_reader.models
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class SessionManager:
    _instance = None
    _lock = Lock()
    _active_sessions = []

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance
    
    def get_session(self):
        with self._lock:
            if len(self._active_sessions) < 2:
                session = SessionLocal()
                self._active_sessions.append(session)
                return session
            else:
                raise Exception("⚠️ Límite de 2 sesiones abiertas alcanzado.")

    def close_session(self, session):
        with self._lock:
            if session in self._active_sessions:
                session.close()
                self._active_sessions.remove(session)



