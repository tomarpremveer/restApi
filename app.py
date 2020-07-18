from flask import Flask,render_template,jsonify,abort,request
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from datetime import datetime
#from flask_cors import CORS
app=Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["SQLALCHEMY_DATABASE_URI"]="mysql+pymysql://root:7500Monty###@localhost/restApi"
db=SQLAlchemy(app)
migrate=Migrate(app,db)
cache_config={
    'DEBUG':True,
    "CACHE_TYPE":"simple",
    "CACHE_DEFAULT_TIMEOUT":300
}
app.config.from_mapping(cache_config)
cache=Cache(app)
#CORS(app)
class Movie(db.Model):
    __tablename__="movies"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    runtime=db.Column(db.Integer,nullable=False)
    release_date=db.Column(db.Date)
    reviews=db.relationship("Review",backref="parent",lazy=True,cascade="all,delete",passive_deletes=True)
    
    def __str__(self):
        return "The name of the movie is %s" % (self.name)
    def __repr__(self):
        return "The name of the movie is %s" % (self.name)
    # def format(ins):
    #     return jsonify({
    #         "success":True
    #     })
class Review(db.Model):
    __tablename__="reviews"
    id=db.Column(db.Integer,primary_key=True)
    review_text=db.Column(db.String(40))
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
@app.route('/users',methods=['POST'])
def create_user():
    try:
        username,password="",""
        data=request.get_json()
        if data is None:
            return jsonify({
                    'success':False,
                    'message':'No data to update was provided in the url',
                    'error_code':400
                    }),400
        if data and 'username' in data.keys():
            username=data["username"]
        if data and 'password' in data.keys():
            password=data["password"]
        if username=="" or password=="":
            return jsonify({
                    'success':False,
                    'message':'No data to update was provided in the url',
                    'error_code':400
                    }),400
        #password=generate_password_hash(password)
        user=User(username=username,password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message':'user created successfully'}),200
    except :
        db.session.rollback()
        return jsonify({'success':False,'error_message':"couldn't create a user account"})
@app.route('/users/<int:id>',methods=['DELETE'])
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
@app.route('/update/users/<int:id>',methods=['PUT','PATCH'])
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
        return jsonify({'message':'Some error occured. Please try again'})
#2.create a movie
@app.route('/movies',methods=['POST'])
def create_movie():
    try:
        data=request.get_json()
        if data is None:
            return jsonify({'message':'some errror occured. Please try again'})
        else:
            movie=Movie(name=data["name"],runtime=data["runtime"],release_date=datetime.now())
            db.session.add(movie)
            db.session.commit()
            return jsonify({
                'success':True,
                'message':'Movie created successfully',
                'code':200
            }),200
    except:
        db.session.rollback()
        return jsonify({'message':'some errror occured. Please try again'})
#3.Delete a movie
@app.route('/movies/<int:id>',methods=['DELETE'])
def delete_movie(id):
    try:
        movie=Movie.query.filter_by(id=id).one_or_none()
        if movie is None:
            abort(404)
        else:
            db.session.delete(movie)
            db.session.commit()
            return jsonify({
                'movieName':movie.name,
                'success':True,
                'message':'Movie successfully deleted',
                'code':200
            }),200
    except:
        db.session.rollback()
        return jsonify({
            'success':False,
            'message':'Some error occurred. Please try again',
            'error_code':503,
        }),503
#4. search for movie
@app.route('/search/<string:search_term>',methods=["GET"])
def get_movie(search_term):
    pass
#Reviews endpoint

#4.Create a review

@app.route('/movies/<int:movie_id>/reviews/',methods=['POST'])
def create_review(movie_id):
    try:
        movie=Movie.query.filter_by(id=movie_id).one_or_none()
        if movie is None:
            abort(404)
        else:
            data=request.get_json()
            if "review_text" not in data.keys():
                return jsonify({
                    'success':False,
                    'message':'No data to update was provided in the url',
                    'error_code':400
                    }),400
            else:
                review_t=data["review_text"]
                review=Review(review_text=review_t)
                review.parent=movie
                # return jsonify({
                #     'review':review.review_text,
                #     'review_parent':review.parent.id
                # })
                db.session.add(review)
                db.session.commit()
                return jsonify({
                    'success':True,
                    'message':'Review successfully created',
                    'code':200
                })
    except:
        db.session.rollback()
        return jsonify({
            'success':False,
            'message':' review Error occurred. Please try again later'
        }),503
# List reviews of a movie
@app.route('/movies/<int:id>/reviews/',methods=["GET"])
def get_movie_reviews(id):
    try:
        movie=Movie.query.filter_by(id=id).one_or_none()
        if movie is None:
            abort(404)
        else:
            reviews=Review.query.filter_by(movie_id=movie.id).all()
            if reviews is not None:
                return jsonify({
                    'success':True,
                    'reviews':reviews,
                    'total_reviews':len(reviews)
                })
    except:
        return jsonify({
            'success':False,
            'message':'Some error occured .Please try again',
            'error_code':503
        }),503

#5.Delete review
@app.route('/movies/<int:movie_id>/reviews/<int:review_id>',methods=['DELETE'])
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