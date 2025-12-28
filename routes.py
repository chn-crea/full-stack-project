"""API routes and view handlers for the Full-Stack Project.

Contains routes for homepage, articles listing, user registration,
authentication, and article management endpoints.
"""

from flask import render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import check_password_hash
from app import app, db
from models import User, Article


@app.route('/')
def index():
    """Home page route."""
    return render_template('index.html')


@app.route('/articles')
def articles():
    """Articles listing page."""
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter_by(is_published=True).paginate(page=page, per_page=10)
    return render_template('articles.html', articles=articles)


@app.route('/article/<slug>')
def article_detail(slug):
    """Single article detail page."""
    article = Article.query.filter_by(slug=slug).first_or_404()
    article.view_count += 1
    db.session.commit()
    return render_template('article.html', article=article)


@app.route('/about')
def about():
    """About page route."""
    return render_template('about.html')


@app.route('/api/users', methods=['GET'])
def get_users():
    """API endpoint to get all users."""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """API endpoint to get a specific user."""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@app.route('/api/users', methods=['POST'])
def create_user():
    """API endpoint to create a new user."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name')
    )
    user.set_password(data.get('password', 'defaultpass'))
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201


@app.route('/api/articles', methods=['GET'])
def get_articles():
    """API endpoint to get all published articles."""
    articles = Article.query.filter_by(is_published=True).all()
    return jsonify([article.to_dict() for article in articles])


@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """API endpoint to get a specific article."""
    article = Article.query.get_or_404(article_id)
    return jsonify(article.to_dict())


@app.route('/api/articles', methods=['POST'])
def create_article():
    """API endpoint to create a new article."""
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    article = Article(
        title=data['title'],
        slug=data['title'].lower().replace(' ', '-'),
        content=data['content'],
        excerpt=data.get('excerpt'),
        user_id=data.get('user_id')
    )
    
    db.session.add(article)
    db.session.commit()
    
    return jsonify(article.to_dict()), 201


@app.route('/api/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    """API endpoint to update an article."""
    article = Article.query.get_or_404(article_id)
    data = request.get_json()
    
    if 'title' in data:
        article.title = data['title']
        article.slug = data['title'].lower().replace(' ', '-')
    if 'content' in data:
        article.content = data['content']
    if 'excerpt' in data:
        article.excerpt = data['excerpt']
    
    db.session.commit()
    return jsonify(article.to_dict())


@app.route('/api/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    """API endpoint to delete an article."""
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    
    return jsonify({'message': 'Article deleted'}), 204


@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('500.html'), 500
