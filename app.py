from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

# instance of the Flask application, setup database config and create db object
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/movie'
db = SQLAlchemy(app)


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
class MovieSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Movie
        sqla_session = db.session
    id = fields.Number(dump_only=True)
    title = fields.String(required=True)
    movie_description = fields.String(required=True)


# creating the endpoints

@app.route('api/v1/movie', methods=['POST'])
def post_movie():
    data = request.get_json()
    movie_schema = MovieSchema()
    movie = movie_schema.load(data)
    result = movie_schema.dump(movie.create())
    return make_response(jsonify({ 'movie': result}), 200)

@app.route('api/v1/movie', methods=['GET'])
def index():
    get_movies = Movie.query.all()
    movie_schema = MovieSchema(many=True)
    movies = movie_schema.dump(get_movies)
    return make_response(jsonify({ 'movies': movies}))
