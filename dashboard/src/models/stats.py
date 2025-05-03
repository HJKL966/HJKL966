# /home/ubuntu/dashboard_project/dashboard/src/models/stats.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

# Assume db is initialized in main.py or similar
# from src.main import db 
# For now, just define the model structure

# Placeholder for db instance if running standalone
# Remove this if db is imported from the main Flask app
db = SQLAlchemy() 

class BotStat(db.Model):
    __tablename__ = 'bot_stats'

    id = db.Column(db.Integer, primary_key=True)
    # Added bot_identifier to distinguish stats if multiple bots report to the same channel
    bot_identifier = db.Column(db.String(100), nullable=True, index=True) 
    user_id = db.Column(db.BigInteger, nullable=True, index=True)
    username = db.Column(db.String(100), nullable=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    # Use DateTime with timezone awareness
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    message_length = db.Column(db.Integer, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    # Storing raw update data might be large, consider if Text is sufficient or if JSONB/JSON type is better (depends on DB)
    raw_update_data = db.Column(db.Text, nullable=True) 
    # Store the original JSON message for auditing/debugging
    raw_json = db.Column(db.Text, nullable=True) 
    # Track when the dashboard processed this stat
    processed_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<BotStat {self.id} - Action: {self.action} by User: {self.user_id} at {self.timestamp}>'

# Example usage (within Flask app context):
# from src.models.stats import BotStat, db
# new_stat = BotStat(user_id=123, username='test', action='start', timestamp=datetime.now(timezone.utc), raw_json='{}')
# db.session.add(new_stat)
# db.session.commit()

