from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ege_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'safonoff'


db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), default='user')
class questions(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        number = db.Column(db.Integer, nullable=False)
        q_type = db.Column(db.String(20), default = 'text')
        content = db.Column(db.Text, nullable=False)
        options = db.Column(db.String(200))  
        answer = db.Column(db.String(100), nullable=False)
        hint = db.Column(db.Text)
        
with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods = ["POST", "GET"])
def register():
    if request.method == 'POST':
            u=request.form.get("username")
            p=request.form.get("password")
            existing_user = Users.query.filter_by(username=u).first()
            if existing_user:
                return "Этот логин уже занят! <a href='/register'>Попробуй другой</a>"
            new_user = Users(username=u,password=p, role = 'user')
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        user = Users.query.filter_by(password=p,username=u).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return "Ошибка! Неверный логин или пароль. <a href='/login'>Попробовать снова</a>"
    return render_template('login.html')
@app.route('/admin', methods=["GET","POST"])
def admin_panel():
    if session.get('role') != 'admin':
        return "<h1>403 Forbidden</h1>Доступ только для админов.", 403
    
    if request.method == 'POST':
        num = request.form.get('number')
        cont = request.form.get('content')
        ans = request.form.get('answer')
        h = request.form.get('hint')
        new_q = questions(number=num,content=cont,answer=ans,hint=h)
        
        db.session.add(new_q)
        db.session.commit()
        print(f"Задание {num} успешно добавлено!")
        return redirect(url_for('admin_panel'))
    
    all_questions = questions.query.order_by(questions.number).all()
    return render_template('admin.html', qs=all_questions)

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    user_data = Users.query.get(user_id)
    if not user_data:
        session.clear()
        return redirect('/login')
    return render_template('profile.html', user=user_data)
        

@app.route('/task/<int:num>', methods=['GET', 'POST'])
def view_task(num):
    if not session.get('user_id'):
        return redirect('/login')
        
    q = questions.query.filter_by(number=num).first()
    if not q:
        return "Задание пока не добавлено Григорием, ждите!!!", 404
        
    if request.method == 'POST':
        user_ans = request.form.get('user_answer')
        if user_ans == q.answer:
            return "<h1>Правильно!</h1> <a href='/dashboard'>К списку</a>"
        else:
            return f"<h1>Ошибка!</h1> <a href='/task/{num}'>Попробовать еще раз</a>"

    return render_template('task.html', q=q)

if __name__ == "__main__":
    app.run(debug=True)