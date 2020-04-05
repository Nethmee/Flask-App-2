from flask import Flask ,render_template,session,logging,redirect,url_for,flash,request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import StringField, TextAreaField ,PasswordField ,validators,Form
from passlib.hash import sha256_crypt

#making an instance of a flask class,which means initializing the flask app
app = Flask(__name__)


####### mysql configurations ########
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # to convert the tuples which is returned by default ,to a dictionary

####initializing mysql #######
mysql = MySQL(app)
Articles = Articles()
#########  routes  ###########
##### routes should be declared before app.run() ####

@app.route('/')
def index()  :
        return render_template('home.html') #all html templates should be inside a folder called templates

@app.route('/about')
def about() :
        return render_template('about.html')

@app.route('/articles/<string:id>/')
def singleAtricle(id)  :
       return render_template('Article.html',id=id)

@app.route('/articles')
def ariticles() :
        return render_template('articles.html',articles = Articles)

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    print(username)
    return username  


class RegistrationForm(Form):
    name  = StringField('name', [validators.Length(min=4, max=25),validators.DataRequired()])
    username  = StringField('Username', [validators.Length(min=4, max=25),validators.DataRequired()])
    email = StringField('email', [validators.Length(min=6, max=35),validators.DataRequired()])
    password = PasswordField('Password', [
            validators.Length(min=6, max=15),
            validators.DataRequired(),
            validators.EqualTo('confirm',message='Password  do not match')
    ])   
    confirm =PasswordField('Password',)
    
@app.route('/register', methods =['GET', 'POST'])
def register():
        form = RegistrationForm (request.form)
        if request.method == 'POST' and form.validate():
                name = form.name.data
                username = form.username.data
                email = form.email.data
                password = sha256_crypt.encrypt(str(form.password.data))
                
                #creating the cursor
                cur = mysql.connection.cursor()
                print("works")
                cur.execute("INSERT INTO users(name,email,username,password) VALUES (%s, %s,%s,%s )" ,(name, email,username ,password))
                ## comiiting the database
                mysql.connection.commit()
                #close the connection
                cur.close()
                flash('You are now registered successfully', 'sucess')# with flash messaging we can use 
                
                redirect(url_for('index'))
                
                
                return render_template('register.html')#passing the form instance created above
        return render_template('register.html',form = form)
                

if(__name__) =='__main__':
    app.run(debug=True)
    
    
    
    
