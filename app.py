from flask import Flask,render_template,jsonify,abort,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
#from flask_cors import CORS
app=Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["SQLALCHEMY_DATABASE_URI"]="mysql+pymysql://root:7500Monty###@localhost/restApi"
db=SQLAlchemy(app)
migrate=Migrate(app,db)
#CORS(app)
class Movie(db.Model):
    __tablename__="movies"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    runtime=db.Column(db.Integer,nullable=False)
    release_date=db.Column(db.Date)
    reviews=db.relationship("Review",backref="parent",lazy=True,cascade="all,delete",passive_deletes=True)
    
    def format(ins):
        return jsonify({
            "success":True
        })
class Review(db.Model):
    __tablename__="reviews"
    id=db.Column(db.Integer,primary_key=True)
    review_text=db.Column(db.String(20))
    movie_id=db.Column(db.Integer,db.ForeignKey('movies.id',ondelete="cascade"),nullable=False)
    
        
    def format(ins):
        return jsonify({
            "success":True
        })
class User(db.Model):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(10),nullable=False)
    username=db.Column(db.String(10),nullable=False)
    password=db.Column(db.String(10),nullable=False)
  #index page  
@app.route('/')
def index():
    return "Welcome to the api page"

def token(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        token=None

        if 'x-access-token' in request.headers:
            token=request.headers['x-access-token']
        if not token:
            return jsonify({'message':'Token is missing'}),401
        return f(*args,**kwargs)
    return wrapper

#api section
#1.CRUD endpoints related to User
@app.route('/create/user',methods=['POST'])
def create_user():
    try:
        data=request.args.get('name','Default Value')
        return jsonify({'name':data})
    except:
        return jsonify({'message':'hlo'})
@app.route('/delete/user/<int:id>',methods=['DELETE'])
def delete_user():
    pass
@app.route('/update/user',methods=['PUT','PATCH'])
def update_user():
    pass
#2.create a movie
@app.route('/create/movie',methods=['POST'])
def create_movie():
    return jsonify({'message':'you have successfully reached movie creation route'})
#3.Delete a movie
@app.route('/delete/movie/<int:id>',methods=['DELETE'])
def delete_movie(id):
    pass
#Reviews endpoint

#4.Create a review

@app.route('/create/review',methods=['POST'])
def create_review():
    pass

#5.Delete review
@app.route('/delete/movie/<int:movie_id>/review/<int:review_id>',methods=['DELETE'])
def delete_review():
    pass
# error handler section

@app.errorhandler(404)
def not_found_404(error):
    return jsonify({
        "success":False,
        "error_code":404,
        "message":'resource not found'
    }),404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success":False,
        "error_code":405,
        "message":"this method is not allowed on this endpoint"
    }),405

@app.errorhandler(503)
def server_error(error):
    return jsonify({
        "success":False,
        "error_code":503,
        "message":"This request can't be processed. Internal server occured"
    }),503