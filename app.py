from flask import Flask ,render_template,session,logging,redirect,url_for,flash,request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import StringField, TextAreaField ,PasswordField ,validators,Form
from passlib.hash import sha256_crypt
from functools import wraps


#making an instance of a flask class,which means initializing the flask app
app = Flask(__name__)
app.secret_key ='secret123' #this secret key will be used to encode the session content



    

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

@app.route('/FeaturedArticles')
def featured_ariticles() :
        
        cur = mysql.connection.cursor()
        featured_Articles = cur.execute("SELECT * FROM featuredarticles")
        print("result")
        
        print(str(featured_Articles))
        if featured_Articles >0:
                 articles = cur.fetchall()
                 print("featured articles successfully retrieved")
                 
        else:
                print("no Featured Articles found")
                
       
        #print(articles)
        mysql.connection.commit()
        cur.close()
        
        return render_template('articles.html',articles = articles)

@app.route('/Display_Farticles/<string:id>/')
def single_Featured_Atricle(id)  :
       cur = mysql.connection.cursor()
       featured_Articles = cur.execute("SELECT * FROM featuredarticles WHERE id=%s",[id])
       print(featured_Articles)
       if featured_Articles > 0:
               print("single featured article found")
               article = cur.fetchone()
               print(article)
       else:
              print("no such article found") 
               
       return render_template('Article.html',id=id,featured_Article=article)

@app.route('/delete_article/<string:id>/')
def Delete_Atricle(id)  :
       cur = mysql.connection.cursor()
       delete_article = cur.execute("DELETE FROM articles WHERE id=%s",[id])
     
       if delete_article > 0:
               print("single article deleted")
               mysql.connection.commit()
          
       else:
              print("no such article found to delete") 
         
       
                
        #close the connection
       cur.close()      
       return "sucessfully deleted !!"


@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    print(username)
    return username  
@app.route('/logout')
#@is_logged_in  
def logout():
        session.clear()
        flash('You are logged out')
        return redirect(url_for('login'))
        
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
        print (form)
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
                
                
                return render_template('register.html',form = form)#passing the form instance created above
        return render_template('register.html',form = form)
             
@app.route('/Login',methods=['GET','POST'])
def login() :
        if request.method == "POST":
               req = request.form 
               email=req["Email"]
               session["logged_in"] = True
               session['email'] = email
               print(session.get('email'))
               password_candidate=req["password"]
               print(req["Email"])
               print("password candidate :%s ",password_candidate)
                 #creating the cursor
               cur = mysql.connection.cursor()
               result = cur.execute("SELECT * FROM users WHERE users.email=%s" ,[email])
               if result > 0:
                      row =cur.fetchone()# This method retrieves the next row of a query result set and returns a single sequence,
                #       while row is not None:
                #         print(row['password'])
                #         row = cur.fetchone()
                        
                      password =row['password']
                      if sha256_crypt.verify(password_candidate,password):
                               msg="Passwords matched"
                               app.logger.info("passwords match")
                               session['logged_in'] = True
                               session['email'] = email
                               getUsername = cur.execute("SELECT username FROM users WHERE users.email=%s" ,[email])
                               if getUsername > 0:
                                        Username =cur.fetchone()
                                        session['username'] = Username
                              
                               print(session['email'])
                               print(session)
                               flash("You are now logged in")
                               return redirect(url_for('dashboard'))
                      else:    
                               error ="passwords do not match"
                               app.logger.info("passwords do not match") 
                               return render_template('LogIn.html',error=error)
                      cur.close()  
               else:
                       error ="No user found with this email "
                       #app.logger.info("No user found with the email :%s",email)
                       return render_template('LogIn.html',error=error)
               
               
               app.logger.info("hii")
        return render_template('LogIn.html')
#check if the user is already logged in
def is_logged_in(f):
        @wraps(f)
        def wrap(*args,**kwargs):
                if 'logged_in' in session:
                        return f(*args, **kwargs)
                else:
                        flash("Unauthorised ,PLease login")
                        return redirect(url_for('login'))
                
        return wrap


class ArticleAddForm(Form):
    title  = StringField('title', [validators.Length(min=5, max=200),validators.DataRequired()])
    author  = StringField('author', [validators.Length(min=4, max=25),validators.DataRequired()])
    body = TextAreaField('body', [validators.Length(min=60),validators.DataRequired()])
    
    
    
@app.route('/add_article',methods=['POST','GET'])
@is_logged_in  
def addArticle():
        form =ArticleAddForm(request.form)
        if request.method=='POST' and form.validate():
               title=request.form['title']
               author=request.form['author']
               body=request.form['body']
               #creating the cursor
               cur = mysql.connection.cursor()
               cur.execute("INSERT INTO articles(title,author,body) VALUES (%s, %s,%s )" ,(title,author,body))
                ## comiiting the database
               mysql.connection.commit()
               cur.close()
               flash('successfully posted', 'sucess')# with flash messaging we can use 
               return redirect(url_for('dashboard'))
               
               
        return render_template('ArticleEditor.html',form=form)




@app.route('/edit_article/<string:id>',methods=['POST','GET'])
@is_logged_in  
def edit_single_article(id):
        print(id)
        if request.method =="GET":
                cur = mysql.connection.cursor()
                result = cur.execute("SELECT * FROM articles WHERE articles.id=%s" ,[id])
                if result > 0:
                        article = cur.fetchone()    
                        print("###################") 
                        print(article) 
                        print(" ") 
                        return render_template('EditSingleArticle.html',article=article, id=id)
                
        
        # if request.method =="POST":
        #         req = request.form 
        #         print("update values")
                
        #         print(req)
        #         print(" ")
                #title=req["title"]
                #cur = mysql.connection.cursor()
                #result = cur.execute('UPDATE articles SET title=%s,author=%s,body=%s WHERE id=%s',(title,author,body))                
       
        return render_template('EditSingleArticle.html',id=id)


                     
@app.route('/dashboard')
@is_logged_in
def dashboard():
        cur = mysql.connection.cursor()
        #get articles
        result = cur.execute("SELECT * FROM articles")
        articles = cur.fetchall()
        if result> 0:
                print(articles)
                return render_template('dashboard.html',articles=articles)
        else:
                msg ="No articles found"
                return render_template('dashboard.html', msg=msg)
        
@app.route('/updateArticle/<string:id>',methods=['POST'])
@is_logged_in
def update_article(id):
       print(id)
       if request.method =="POST":
                req = request.form
                print("update values")
                print(req)
                title=req["title"]
                author=req["author"]
                body=req["body"]
                cur = mysql.connection.cursor()
                result = cur.execute('UPDATE articles SET title=%s,author=%s,body=%s WHERE id=%s',(title,author,body,id))   
                if result > 0:
                       print(str(result))
                       return "sucess !!"
       
       
       return "hii"
          
        
        
        
        

if(__name__) =='__main__':
    app.run(debug=True)
   
    
    
    
#INSERT INTO articles(title,author,body) VALUES ("", ""," " )