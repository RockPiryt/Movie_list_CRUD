from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap5(app)

#Create DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
app.app_context().push()

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), unique=True, nullable=False)


    def __repr__(self):
        return f'<Movie {self.title}>'

db.create_all()

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


class EditForm(FlaskForm):
    rating = FloatField(label="Your Rating out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Update")



@app.route("/")
def home():
    all_movies = Movie.query.all()
    return render_template("index.html", html_all_movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    #Get book from db to edit
    id_movie_to_edit = request.args.get("movie_id")
    movie_to_edit = Movie.query.filter_by(id=id_movie_to_edit).first()

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

@app.route("/delete")
def delete():
    pass

if __name__ == '__main__':
    app.run(debug=True)
