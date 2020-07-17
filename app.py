from flask import Flask,render_template,jsonify,abort,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash,check_password_hash
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
    username=db.Column(db.String(10),nullable=False)
    password=db.Column(db.String(100),nullable=False)

    def update_db(self,data):
        for (key,value) in data.items():
            setattr(self,key,value)
        db.session.commit()
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
        data=request.get_json()
        username=data["username"]
        password=data["password"]
        #password=generate_password_hash(password)
        user=User(username=username,password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message':'user created successfully'}),200
    except :
        db.session.rollback()
        return jsonify({'success':False,'error_message':"couldn't create a user account"})
@app.route('/user/<int:id>',methods=['DELETE'])
def delete_user(id=0):
    try:
        user=User.query.filter_by(id=id).one_or_none()
        if user is None:
            abort(404)
        else:
            db.session.delete(user)
            db.session.commit()
            return jsonify({
                "success":True,
                "code":200,
                'message':"User deleted successfully",
                }),200
    except:
        db.session.rollback()
        return jsonify({'message':'Some error occured'})
@app.route('/update/user/<int:id>',methods=['PUT','PATCH'])
def update_user(id):
    try:
        user=User.query.filter_by(id=id).one_or_none()
        if user is None:
            abort(404)
        else:
            keys=0
            data=request.get_json()
            #if no data is provided in the url
            if data is None:
                return jsonify({
                    'success':False,
                    'message':'No data to update was provided in the url',
                    'error_code':400
                    }),400
            if data and  "username" in data.keys():
                keys+=1
            if data and "password" in data.keys():
                keys+=1
            # if data provided is gibrish data i.e does not match the fields of the database
            if keys ==0:
                return jsonify({
                    'success':False,
                    'message':'Data provided doesn\'t match with the columns of database',
                    'error_code':400
                    }),400
            else:
                user.update_db(data)
                return jsonify({
                    'success':True,
                    'message':'user updated successfully',
                    'code':200
                }),200

    except:
        return jsonify({'message':'Some error occured'})
#2.create a movie
@app.route('/create/movie',methods=['POST'])
def create_movie():
    return jsonify({'message':'you have successfully reached movie creation route'})
#3.Delete a movie
@app.route('/movie/<int:id>',methods=['DELETE'])
def delete_movie(id):
    pass
#Reviews endpoint

#4.Create a review

@app.route('/create/review',methods=['POST'])
def create_review():
    pass

#5.Delete review
@app.route('/movie/<int:movie_id>/review/<int:review_id>',methods=['DELETE'])
def delete_review():
    pass
# error handler section
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success":False,
        "error_code":400,
        "message":"Bad request"
    }),400
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