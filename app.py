import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/fullstack_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# ==================== DATABASE CONNECTION ====================
def get_db_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'fullstack_db'),
            user=os.getenv('DB_USER', 'user'),
            password=os.getenv('DB_PASSWORD', 'password'),
            port=os.getenv('DB_PORT', 5432)
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# ==================== BASIC ROUTES ====================

@app.route('/', methods=['GET'])
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'API is running',
        'version': '1.0.0'
    }), 200

@app.route('/api/database', methods=['GET'])
def database_status():
    """Check database connection status"""
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({
                'status': 'success',
                'message': 'Database connection successful',
                'database': os.getenv('DB_NAME', 'fullstack_db')
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to connect to database'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500

# ==================== PLACEHOLDER CRUD ROUTES ====================

@app.route('/api/items', methods=['GET'])
def get_items():
    """Get all items from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM items LIMIT 100;')
        items = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': items,
            'count': len(items)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching items: {str(e)}'
        }), 500

@app.route('/api/items', methods=['POST'])
def create_item():
    """Create a new item"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        # Example: INSERT INTO items (name, description) VALUES (...)
        # Modify based on your actual schema
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Item created successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error creating item: {str(e)}'
        }), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Run the Flask app
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=debug_mode
    )
