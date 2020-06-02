from flask import Flask,render_template,jsonify,abort,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from flask_cors import CORS
app=Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["SQLALCHEMY_DATABASE_URI"]="mysql+pymysql://root:7500Monty###@localhost/api"
db=SQLAlchemy(app)
migrate=Migrate(app,db)
#CORS(app)
class Parent(db.Model):
    __tablename__="parents"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    age=db.Column(db.Integer,nullable=False)
    childrens=db.relationship("Child",backref="parent",lazy=True)
    
    def format(ins):
        return jsonify({
            "name":ins.name,
            "age":ins.age
        })
class Child(db.Model):
    __tablename__="childrens"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    age=db.Column(db.Integer,nullable=False)
    parent_id=db.Column(db.Integer,db.ForeignKey('parents.id'),nullable=False)
    
        
    def format(ins):
        return jsonify({
            "name":ins.name,
            "age":ins.age
        })
  #index page  
@app.route('/')
def index():
    return "Welcome to the api page"

#api section

#1.Get parent by Id . Id should be an Integer
@app.route('/parents/<int:parent_id>',methods=['GET'])
def get_parent(parent_id=None):
    if parent_id==None:
        return jsonify({
            "success":False,
            "message":"Parent id isn't specififed."
        })
    try:
        parent=Parent.query.filter(Parent.id==parent_id).one_or_none()
        if parent is None:
            abort(404)
            
        return parent.format()
    except:
        abort(503)

#2.Create a Parent
@app.route('/parent/create/',methods=['POST'])
def create_parent():
    data=request.get_json()
    if data is None:
        abort(404)
    else:
        parent=Parent(name=data["name"],age=data["age"])
        db.session.add(parent)
        db.session.commit()
        return jsonify({
            "sucess":True,
            "message":"Record successfully created",
            "code":200
        })
#3. create a child . Accepted methods POST . Url:/parent/<parent_id>/child/create/
@app.route('/parents/<int:parent_id>/child/create/',methods=["POST"])
def create_child(parent_id):
    data=request.get_json()
    data_keys=[i for i in data.keys()]

    parent=Parent.query.filter(Parent.id==parent_id).one_or_none()
    if parent is None:
        return jsonify({
            "success":False,
            "message":"Invalid parent Id",
            "error_code":404
        })
    if "name" not in data_keys:
        return jsonify({
            "success":False,
            "message":"Invalid input format.name and age both should be provided in the input"
        })
    if "age" not in data_keys:
        return jsonify({
            "success":False,
            "message":"Invalid input format.name and age both should be provided in the input"
        })
    else:
        try:
            child=Child(name=data["name"],age=data["age"])
            child.parent=parent
            db.session.add(child)
            db.session.commit()
            return jsonify({
                "success":True,
                "message":"Child added succcessfully"
            })
        except:
            abort(503)
            db.session.rollback()

#4. get all the childrens of a parent by parent Id
@app.route('/parents/<int:parent_id>/childrens/')
def get_chidlren_of_parent(parent_id):
    parent=Parent.query.filter(Parent.id==parent_id).one_or_none()
    if parent is None:
        return jsonify({
            "success":False,
            "message":"Invalid parent Id",
            "error_code":404
        })
    else:
        try:
            childrens=Child.query.filter(Child.parent_id==parent_id).order_by(Child.age).all()
            return childrens[0].format()
        except:
            abort(500)

    

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