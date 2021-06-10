from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


# instance of the Flask application, setup database config and create db object
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysqlpassmacrob@localhost:3306/movie'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


# create movie model
class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    movie_description = db.Column(db.String(100))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, title, movie_description):
        self.title = title
        self.movie_description = movie_description

    def __repr__(self):
        return f"{self.id}"

db.create_all()

# the movie schema makes it possible to return JSON from the Python objects from SQLALCHEMY
class MovieSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Movie
        sqla_session = db.session
    id = fields.Number(dump_only=True)
    title = fields.String(required=True)
    movie_description = fields.String(required=True)


# creating the endpoints

# route that posts a movie
@app.route('/api/v1/movie', methods=['POST'])
def create_movie():
    data = request.get_json()
    movie_schema = MovieSchema()
    movie = movie_schema.load(data)
    result = movie_schema.dump(movie.create())
    return make_response(jsonify({"movie": result}), 200)

# route that returns a list of movies
@app.route('/api/v1/movie', methods=['GET'])
def index():
    get_movies = Movie.query.all()
    movie_schema = MovieSchema(many=True)
    movies = movie_schema.dump(get_movies)
    return make_response(jsonify({ 'movies': movies}))

# route that retrieves a movie by passing a specific id
@app.route('/api/v1/movie/<id>', methods=['GET'])
def get_movie_by_id(id):
    get_movie = Movie.query.get(id)
    movie_schema = MovieSchema()
    movie = movie_schema.dump(get_movie)
    return make_response(jsonify({ 'movie': movie}))

# update a movie by passing a specific id
@app.route('/api/v1/movie/<id>', methods=['PUT'])
def update_movie_by_id(id):
    data = request.get_json()
    get_movie = Movie.query.get(id)
    if data.get('title'):
        get_movie.title = data['title']
    if data.get('movie_description'):
        get_movie.movie_description = data['movie_description']
    db.session.add(get_movie)
    db.session.commit()
    movie_schema = MovieSchema(only=['id', 'title', 'movie_description'])
    movie = movie_schema.dump(get_movie)
    
    return make_response(jsonify({ 'movie': movie}))

# delete a movie by a specific id
@app.route('/api/v1/movie/<id>', methods=['DELETE'])
def delete_movie_by_id(id):
    get_movie = Movie.query.get(id)
    db.session.delete(get_movie)
    db.session.commit()
    return make_response("", 204)
