from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venues', lazy=True)

    def venue_to_dictionary(self):
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres.strip('{}').split(','),
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website_link": self.website_link,
            "facebook_link": self.facebook_link,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
        }


class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artists', lazy=True)
    albums = db.relationship('Album', backref='artists', lazy=True)
    songs = db.relationship('Song', backref='artists', lazy=True)

    def artist_to_dictionary(self):
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres.strip('{}').split(','),
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website_link": self.website_link,
            "facebook_link": self.facebook_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
        }


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.now())


class Album(db.Model):
    __tablename__ = 'albums'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    songs = db.relationship('Song', backref='albums', lazy=True)


class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey(
        'albums.id'))
