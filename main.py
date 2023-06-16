from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5
import requests
import os
from dotenv import load_dotenv


load_dotenv("C:/Users/Popuś/Desktop/Python/environment_variables/.env")
MOVIE_DB_API_KEY = os.getenv("api_key_movieDB")


MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap5(app)

##-----------------------------------Create DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
app.app_context().push()


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), unique=True, nullable=False)


    def __repr__(self):
        return f'<Movie {self.title}>'

db.create_all()

#First information to db
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

# db.session.add(new_movie)
# db.session.commit()

##------------------------------Flaskforms
class EditForm(FlaskForm):
    rating = FloatField(label="Your Rating out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Update")

class AddForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    submit = SubmitField(label="Add movie")



@app.route("/")
def home():
    '''Show all movie in database'''

    all_movies = Movie.query.all()
    return render_template("index.html", html_all_movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    '''Edit rating and review (use movie_id)'''

    #Get book from db to edit
    id_movie_to_edit = request.args.get("movie_id")
    # movie_to_edit = Movie.query.filter_by(id=id_movie_to_edit).first()
    movie_to_edit = Movie.query.get(id_movie_to_edit)

    #Create flaskform to  add new value for review and rating to movie_to_edit
    python_form = EditForm()
    if python_form.validate_on_submit():
        new_rating = python_form.rating.data
        new_review = python_form.review.data
        movie_to_edit.rating= new_rating
        movie_to_edit.review = new_review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", html_form=python_form, html_movie_to_edit=movie_to_edit)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    '''Delete movie from database'''

    #Get book from db to delete
    id_movie_to_delete = request.args.get("movie_id")
    movie_to_delete = Movie.query.filter_by(id=id_movie_to_delete).first()
    db.session.delete(movie_to_delete)
    db.session.commit()
    flash(f'{movie_to_delete.title} Successfully deleted', 'success')
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    '''Add movie to database movieDB(make API request)'''

    add_form = AddForm()
    if add_form.validate_on_submit():
        new_movie_title =  add_form.title.data

        # headers = {
        # "accept": "application/json",
        # "Authorization": "Bearer token"
        # }

        params={
            "api_key":MOVIE_DB_API_KEY,
            "query": new_movie_title,
        }

        # response = requests.get(MOVIE_DB_SEARCH_URL, headers=headers, params=params)
        response = requests.get(MOVIE_DB_SEARCH_URL, params=params)
        optional_movies = response.json()["results"]

        return render_template("select.html", html_optional_movies=optional_movies)
    return render_template("add.html", html_add_form=add_form )

@app.route("/details", methods=["GET", "POST"])
def add_movie_details():
    '''Get information about movie from movie DB (make API request). 
    Save data in database.'''

    #Get movie_id from select.html
    select_movie_id = request.args.get("movie_id")
    #Make API url
    movie_api_url = f"{MOVIE_DB_INFO_URL}/{select_movie_id}"

    #Get information from MovieDB
    #Params to url
    params={
        "api_key":MOVIE_DB_API_KEY,
        "language": "en-US",
        }
    response = requests.get(movie_api_url, params=params)
    movie_data = response.json()

    #Save data to SQLite database (use class Movie)
    new_movie=Movie(title=movie_data["title"],
                    year=movie_data["release_date"].split("-")[0],
                    img_url=f'{MOVIE_DB_IMAGE_URL}{movie_data["poster_path"]}',
                    description=movie_data["overview"],
                    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
