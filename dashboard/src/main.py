import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import necessary modules
from flask import Flask, render_template # Added render_template
from src.models import db
from src.models.stats import BotStat # Import the stats model
# from src.routes.user import user_bp # Commented out as it's not used currently and might cause issues if file doesn't exist

# Initialize Flask app, specifying the template folder
app = Flask(__name__, template_folder='templates') # Removed static_folder, added template_folder
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# app.register_blueprint(user_bp, url_prefix='/api') # Commented out

# Configure SQLite database
db_path = os.path.join(os.path.dirname(__file__), 'stats.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Define the main route to display statistics
@app.route('/')
def index():
    """Fetches all stats from the database and renders them in the index template."""
    try:
        # Query all statistics, order by timestamp descending
        all_stats = BotStat.query.order_by(BotStat.timestamp.desc()).all()
        # Render the template, passing the stats data
        return render_template('index.html', stats=all_stats)
    except Exception as e:
        # Log the error (in a real app, use proper logging)
        print(f"Error fetching stats: {e}")
        # Render the template with an error message or empty list
        return render_template('index.html', stats=[], error="Could not fetch statistics.")


# Keep the main execution block
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

