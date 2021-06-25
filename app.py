# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for
)
from sqlalchemy import desc
from flask_sqlalchemy import SQLAlchemy
from logging import Formatter, FileHandler
from forms import *
from models import *
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    # display 10 of the most recent created venues and artists
    venues = Venue.query.order_by(desc(Venue.created_date)).limit(10).all()
    artists = Artist.query.order_by(desc(Artist.created_date)).limit(10).all()
    return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
    locations = db.session.query(Venue.city, Venue.state).group_by(
        Venue.city, Venue.state).all()
    data = []

    for [city, state] in locations:
        venues = Venue.query.filter_by(city=city, state=state).all()
        venues_data = []

        for venue in venues:
            upcoming_shows = Show.query.filter(
                Show.venue_id == venue.id,
                Show.start_time >= datetime.now()).all()

            venues_data.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows)
            })

        data.append({
            'city': city,
            'state': state,
            'venues': venues_data
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    search_results = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(search_results),
        "data": search_results,
    }

    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).join(
        Artist, Show.artist_id == Artist.id).all()

    upcoming_shows = []
    past_shows = []

    for show in shows:
        formatted_show = {
            "artist_id": show.artists.id,
            "artist_name": show.artists.name,
            "artist_image_link": show.artists.image_link,
            "start_time": show.start_time
        }

        if show.start_time < datetime.now():
            past_shows.append(formatted_show)
        else:
            upcoming_shows.append(formatted_show)

    data = venue.venue_to_dictionary()
    data['past_shows'] = past_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows'] = upcoming_shows
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    new_venue = Venue()
    form = VenueForm(request.form)
    error = False

    if form.validate_on_submit():
        try:
            form.populate_obj(new_venue)
            db.session.add(new_venue)
            db.session.commit()
            flash('Venue ' + new_venue.name + ' was successfully listed!')
        except Exception as err:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed. ' + err)
            error = True
        finally:
            db.session.close()
            if error:
                return render_template('forms/new_venue.html', form=form)
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash('There was an error in {} - {}'.format(fieldName, err))
        return render_template('forms/new_venue.html', form=form)
    return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id)

    if shows.count() > 0:
        for show in shows:
            try:
                db.session.delete(show)
                db.session.commit()
            except Exception as err:
                db.session.rollback()
                print(sys.exc_info())
                flash('Show could not be deleted. {}'.format(err))
            finally:
                db.session.close()

    error = False

    try:
        db.session.delete(venue)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        print(sys.exc_info())
        error = True
        flash('An error occurred. Venue ' +
              venue.name + ' could not be deleted. ' + err)
    finally:
        db.session.close()
        if error:
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            flash('The venue has been deleted.')
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = []

    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search_results = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(search_results),
        "data": search_results
    }

    return render_template('pages/search_artists.html',
                           results=response,
                           search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id).join(
        Venue, Show.venue_id == Venue.id).all()
    albums = Album.query.filter_by(artist_id=artist_id)
    songs = Song.query.filter_by(artist_id=artist_id)

    upcoming_shows = []
    past_shows = []

    for show in shows:
        formatted_show = {
            "venue_id": show.venues.id,
            "venue_name": show.venues.name,
            "venue_image_link": show.venues.image_link,
            "start_time": show.start_time
        }

        if show.start_time < datetime.now():
            past_shows.append(formatted_show)
        else:
            upcoming_shows.append(formatted_show)

    albums_data = []
    for album in albums:
        album_songs = songs.filter_by(album_id=album.id)
        songs_data = []

        for song in album_songs:
            songs_data.append({
                'title': song.title
            })

        albums_data.append({
            'id': album.id,
            'title': album.title,
            'songs': songs_data
        })

    no_album_songs = songs.filter_by(album_id=None)
    no_album_songs_data = []
    for song in no_album_songs:
        no_album_songs_data.append({
            'title': song.title
        })

    data = artist.artist_to_dictionary()
    data['past_shows'] = past_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows'] = upcoming_shows
    data['upcoming_shows_count'] = len(upcoming_shows)
    data['albums'] = albums_data
    data['songs'] = no_album_songs_data

    return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/<int:artist_id>/albums/<int:album_id>')
def show_album(artist_id, album_id):
    album = Album.query.get(album_id)
    artist = Artist.query.get(artist_id)

    songs_data = []
    for song in album.songs:
        songs_data.append({
            'title': song.title
        })

    album_data = {
        'title': album.title,
        'songs': songs_data,
        'artist_name': artist.name,
        'artist_id': artist_id
    }

    return render_template('pages/show_album.html', album=album_data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    form.genres.data = artist.genres
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm()

    if form.validate_on_submit():
        try:
            artist.name = form.name.data
            artist.genres = form.genres.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.website_link = form.website_link.data
            artist.facebook_link = form.facebook_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            artist.image_link = form.image_link.data

            db.session.commit()
            flash('Artist ' + form.name.data + ' was successfully updated!')
        except Exception as err:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be updated. ' + err)
        finally:
            db.session.close()
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash('There was an error in {} - {}'.format(fieldName, err))
        return render_template('forms/edit_artist.html',
                               form=form, artist=artist)
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    form.genres.data = venue.genres
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm()

    if form.validate_on_submit():
        try:
            venue.name = form.name.data
            venue.genres = form.genres.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.website_link = form.website_link.data
            venue.facebook_link = form.facebook_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.image_link = form.image_link.data

            db.session.commit()
            flash('Venue ' + venue.name + ' was successfully updated!')
        except Exception as err:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be updated. ' + err)
        finally:
            db.session.close()
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash('There was an error in {} - {}'.format(fieldName, err))
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    new_artist = Artist()
    form = ArtistForm(request.form)
    error = False

    if form.validate_on_submit():
        try:
            form.populate_obj(new_artist)
            db.session.add(new_artist)
            db.session.commit()
            flash('Artist ' + new_artist.name + ' was successfully listed!')
        except Exception as err:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed. ' + err)
            error = True
        finally:
            db.session.close()
            if error:
                return render_template('forms/new_artist.html', form=form)
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash('There was an error in {} - {}'.format(fieldName, err))
        return render_template('forms/new_artist.html', form=form)
    return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = []

    for show in shows:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)

        data.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time,
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    new_show = Show()
    form = ShowForm(request.form)
    artist_id = form.artist_id.data
    artist = Artist.query.get(artist_id)
    venue_id = form.venue_id.data
    venue = Venue.query.get(venue_id)
    start_time = form.start_time.data
    shows = Show.query.filter_by(artist_id=artist_id).all()

    if (not artist):
        flash('Artist does not exists')
        return render_template('forms/new_show.html', form=form)

    if (not venue):
        flash('Venue does not exists')
        return render_template('forms/new_show.html', form=form)

    for show in shows:
        show_venue = Venue.query.get(show.venue_id)

        # Less than 3 hours difference between current show and artist's show
        # (venue and artist's show are at the same city).
        if (abs(start_time - show.start_time).total_seconds() < 10800 and
                show_venue.state == venue.state and
                show_venue.city == venue.city):
            flash('Artist is busy at that time. Select ' +
                  'a different time or artist.')
            return render_template('forms/new_show.html', form=form)

        # Less than 1 day difference between current show and artist's show
        # (venue and artist's show are in different cities).
        if (abs(start_time - show.start_time).total_seconds() < 86400 and
                show_venue.state != venue.state and
                show_venue.city != venue.city):
            flash('Artist is busy at that time. Select ' +
                  'a different time or artist.')
            return render_template('forms/new_show.html', form=form)

    if form.validate_on_submit():
        try:
            form.populate_obj(new_show)
            db.session.add(new_show)
            db.session.commit()
            flash('Show was successfully listed!')
        except Exception as err:
            db.session.rollback()
            print(sys.exc_info())
            error = True
            flash('An error occurred. Show could not be listed. ' + err)
        finally:
            db.session.close()
            if error:
                return render_template('forms/new_show.html', form=form)
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash('There was an error in {} - {}'.format(fieldName, err))
        return render_template('forms/new_show.html', form=form)
    return redirect(url_for('index'))


@app.errorhandler(400)
def bad_request_error(error):
    return render_template('errors/400.html'), 400


@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('errors/401.html'), 401


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(405)
def invalid_method_error(error):
    return render_template('errors/405.html'), 405


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s ' +
            '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
'''
