from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from database import db, User, Todo
import os

print("ENVIRONMENT VARIABLES:")
print(os.environ)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'postgres://910f3c0ee7c2259b53f42cf620f8dc127c7fd97b28311a51c5f767ea6b24c4ae:sk_AiPuONVNb1SkhBUvFTZfH@db.prisma.io:5432/?sslmode=require'  # Change this to a secure secret key
# Database configuration
if os.environ.get('prisma+postgres://accelerate.prisma-data.net/?api_key=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqd3RfaWQiOjEsInNlY3VyZV9rZXkiOiJza19BaVB1T05WTmIxU2toQlV2RlRaZkgiLCJhcGlfa2V5IjoiMDFLMkNSRTlYS0FRR1NLR1RITUpZS1BXMDgiLCJ0ZW5hbnRfaWQiOiI5MTBmM2MwZWU3YzIyNTliNTNmNDJjZjYyMGY4ZGMxMjdjN2ZkOTdiMjgzMTFhNTFjNWY3NjdlYTZiMjRjNGFlIiwiaW50ZXJuYWxfc2VjcmV0IjoiOGViZTBiMjUtZGEyMS00MTkwLTgzNGMtZjE1OWM4ZGM0Nzk1In0.g1M3UjElMyuJmPVjsWTf3_ysiS5hT4Rilkikg5LPZawL'):
    # Use PostgreSQL on Vercel
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('prisma+postgres://accelerate.prisma-data.net/?api_key=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqd3RfaWQiOjEsInNlY3VyZV9rZXkiOiJza19BaVB1T05WTmIxU2toQlV2RlRaZkgiLCJhcGlfa2V5IjoiMDFLMkNSRTlYS0FRR1NLR1RITUpZS1BXMDgiLCJ0ZW5hbnRfaWQiOiI5MTBmM2MwZWU3YzIyNTliNTNmNDJjZjYyMGY4ZGMxMjdjN2ZkOTdiMjgzMTFhNTFjNWY3NjdlYTZiMjRjNGFlIiwiaW50ZXJuYWxfc2VjcmV0IjoiOGViZTBiMjUtZGEyMS00MTkwLTgzNGMtZjE1OWM4ZGM0Nzk1In0.g1M3UjElMyuJmPVjsWTf3_ysiS5hT4Rilkikg5LPZaw').replace("postgres://", "postgresql://", 1)
else:
    # Use SQLite for local development
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'todo.db')
    # Ensure the instance folder exists
    try:
        os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'))
    except OSError:
        pass
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)

# This creates the database tables from your models
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# API endpoint to get all todos
@app.route('/api/todos')
@login_required
def get_todos():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return jsonify([{'id': todo.id, 'title': todo.title, 'complete': todo.complete} for todo in todos])

@app.route('/')
@login_required
def index():
    # The index now just serves the container page.
    # The todos will be fetched by JavaScript.
    return render_template('index.html')

@app.route('/api/add_todo', methods=['POST'])
@login_required
def add_todo():
    data = request.get_json()
    title = data.get('title')
    if title:
        todo = Todo(title=title, user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
        return jsonify({'id': todo.id, 'title': todo.title, 'complete': todo.complete}), 201
    return jsonify({'error': 'Title is required'}), 400

@app.route('/api/toggle_todo/<int:id>', methods=['POST'])
@login_required
def toggle_todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id == current_user.id:
        todo.complete = not todo.complete
        db.session.commit()
        return jsonify({'id': todo.id, 'title': todo.title, 'complete': todo.complete})
    return jsonify({'error': 'Unauthorized'}), 403

@app.route('/api/delete_todo/<int:id>', methods=['DELETE'])
@login_required
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id == current_user.id:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'result': 'Todo deleted'})
    return jsonify({'error': 'Unauthorized'}), 403

@app.route('/api/update_todo/<int:id>', methods=['PUT'])
@login_required
def update_todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    new_title = data.get('title')
    if not new_title:
        return jsonify({'error': 'Title is required'}), 400
    todo.title = new_title
    db.session.commit()
    return jsonify({'id': todo.id, 'title': todo.title, 'complete': todo.complete})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            if User.query.filter_by(username=username).first():
                return "Username already exists!"
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
    