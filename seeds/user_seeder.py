from flask_seeder import Seeder
from models.user import User
from werkzeug.security import generate_password_hash
from datetime import datetime

class UserSeeder(Seeder):
    def run(self):
        user = User.query.filter_by(username="admin").first()
        if not user:
            user = User(
                username="admin",
                email="admin@example.com",
                password_hash=generate_password_hash("password"),
                created_at=datetime.utcnow(),
                active=True
            )
            self.db.session.add(user)
            self.db.session.commit()
            print("User admin created.")
        else:
            print("User admin already exists.")
