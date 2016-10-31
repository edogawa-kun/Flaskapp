import os
from flask import Flask, request, render_template, url_for, redirect, flash, send_from_directory, session
from flask_mysqldb import MySQL
from MySQLdb import escape_string as thwart
from wtforms import Form, StringField, TextAreaField, validators, PasswordField, RadioField
from werkzeug.utils import secure_filename
from passlib.hash import sha256_crypt
import gc
import music

MEDIA_MUSIC = "/media/anubhav/OS/music"
fname = os.listdir("/media/anubhav/OS/music")

UPLOAD_FOLDER = '/media/anubhav/OS/Flask/static/media'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4', 'mkv', 'DAT'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'many random bytes'
mysql = MySQL()
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'arnav123'
app.config['MYSQL_DB'] = 'flaskapp'
app.config['MYSQL_HOST'] = 'localhost'
mysql.init_app(app)

# app = Flask(static_folder="static")
app.config['STATIC_FOLDER'] = 'static'


class BlogPost(Form):
    topic = StringField('topic', [validators.Length(min=4, max=40)])
    content = TextAreaField('content', [validators.DataRequired()])
    file = StringField('file')

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Length(min=3),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class MusicDown(Form):
    search = StringField('search')
    name = StringField('file')


@app.route('/index')
def index():
    return render_template("home.html")


@app.route('/blogs/', methods=['GET', 'POST'])
def blog():
    if session['login']:
        print(session)
        global filename
        filename = ""
        conn = mysql.connection
        c = conn.cursor()
        form = BlogPost(request.form)
        print("Fine here")
        x = c.execute("SELECT * FROM blog;")
        print(x)
        data = c.fetchall()

        flash("Got here 1")
        print("1")
        if request.method == 'POST' and form.validate():
            print("Got here 2")
            print(request.files)
            print(request)
            print("WHAT")
            # flash("WHAT")


            if 'file' in request.files:
                flash('No file part')

                file = request.files['file']
                print("Hell no")
                print(file)
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == '':
                    flash('No selected file')
                    print('No selected file')
                    filename = None

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            t = str(form.topic.data)
            cu = str(form.content.data)
            print(filename)
            sql = """INSERT INTO blog(topic, content, file, date) VALUES(%s, %s, %s, NOW())"""
            c.execute(sql, (thwart(t), thwart(cu), thwart(str(filename))))

            conn.commit()

            c.close()
            if conn.open:
                flash("open")

            gc.collect()
            flash("Thanks")
            print("3")
            # return render_template('blog.html', filename=filename)

        print("WTF")
        if len(data) > 0:
            print(str(filename) + "1")
            return render_template("blog.html", form=form, data=data)
        else:
            print(str(filename) + "2")
            return render_template("blog.html", form=form)

    else:
        flash("You need to log in\n\n\n\n\login")
        return redirect(url_for('login'))

@app.route('/register/', methods=['GET','POST'])
def register():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            print(password)
            print(len(password))

            conn = mysql.connection
            c = conn.cursor()

            x = c.execute("SELECT * FROM user WHERE username = (%s)",
                          (thwart(username),))
            print(x)

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                sql = """INSERT INTO user (username, password, email) VALUES (%s, %s, %s)"""
                c.execute(sql, (thwart(username), thwart(password), thwart(email)))

                conn.commit()
                flash("Thanks for registering!")
                print("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('index'))

        return render_template("register.html", form=form)

    except Exception as e:
        return (str(e))

@app.route('/', methods=['GET', 'POST'])
def login():
    error=''
    conn = mysql.connection
    c = conn.cursor()
    try:
        if request.method == "POST":
            print("yo")
            data = c.execute("SELECT * FROM user WHERE username = (%s)", (thwart(request.form['username']),))
            data = c.fetchone()
            print(data)
            print("Back!!")
            if data == None: error = "Invalid credentials"


            if sha256_crypt.verify(request.form['password'], data[3]):
                session['login'] = True
                session['username'] = request.form['username']
                c.close()
                conn.close()
                gc.collect()
                return redirect(url_for('index'))
            else:
                error = "Invalid credentials"

        gc.collect()
        print(error)
        return render_template("login.html" ,error=error)
    except Exception as e:
        flash(e)
        print(e)
        return render_template("login.html", error=error)

@app.route('/logOut')
def logout():
    session.clear()
    flash("thanks")
    return redirect(url_for('login'))

@app.route('/music-downloader', methods=["GET", "POST"])
def down():
    form = MusicDown(request.form)
    dic = {}

    if request.method=='POST':
        print(request.form)
        if not 'name' in request.form:
            search = request.form['search']
            arr = music.so(search)
            return render_template('musicDown.html', arr=arr, form=form)

        choice = request.form['choice']
        name = request.form['name']
        print(dic)
        print(choice)
        music.download(choice, name)

    print("here")
    print(fname)
    return render_template('musicDown.html', fname=fname, form=form)

@app.route('/music-downloader/<filename>')
def download_file(filename):
    return send_from_directory(MEDIA_MUSIC, filename, as_attachment=True)

@app.route('/music-downloader/play/<filename>')
def play(filename):
    return render_template('mplayer.html', filename=filename)
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
