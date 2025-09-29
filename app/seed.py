import argparse
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
import app.models.user  # ensure models are imported
import app.models.log   # ensure models are imported
from app.repositories.user_repository import UserRepository
from app.repositories.log_repository import LogRepository
from app.core import security


SEVERITIES = ["DEBUG", "INFO", "WARN", "ERROR"]
SOURCES = ["system", "auth", "db", "logs", "api"]
MESSAGES = [
	"User action completed",
	"Request processed",
	"Background job finished",
	"Cache miss",
	"Cache hit",
	"Database connection established",
	"Database timeout",
	"Authentication succeeded",
	"Authentication failed",
	"Permission denied",
]


def seed_data(admin_password: str, log_count: int):
	Base.metadata.create_all(bind=engine)
	db: Session = SessionLocal()
	try:
		user_repo = UserRepository(db)
		admin = user_repo.get_by_username("admin")
		if not admin:
			hashed = security.hash_password(admin_password)
			admin = user_repo.create("admin", hashed, name="Administrator", email="admin@example.com")
			admin.is_admin = True
			db.add(admin)
			db.commit()

		log_repo = LogRepository(db)
		# Generate random logs
		for i in range(log_count):
			sev = random.choice(SEVERITIES)
			src = random.choice(SOURCES)
			msg = random.choice(MESSAGES)
			log_repo.create(sev, src, msg)
	finally:
		db.close()


def main():
	parser = argparse.ArgumentParser(description="Seed database with admin user and logs")
	parser.add_argument("--admin-password", default="Admin@12345", help="Password for the admin user")
	parser.add_argument("--logs", type=int, default=50, help="Number of random logs to generate")
	args = parser.parse_args()
	seed_data(args.admin_password, args.logs)


if __name__ == "__main__":
	main()


