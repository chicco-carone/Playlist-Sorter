from flask import Flask, render_template, request
from db_connection import DBConnection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    playlist_name = request.form['playlist_name']
    track_name = request.form['track_name']
    album_name = request.form['album_name']
    artist_name = request.form['artist_name']
    track_id = request.form['track_id']

    with DBConnection() as db_conn:
        db_conn.add_track_data(playlist_name, (track_name, album_name, artist_name, track_id))

    return 'Playlist data saved successfully!'

@app.route('/sorted_playlist')
def sorted_playlist():
    playlist_name = request.args.get('playlist_name')

    with DBConnection() as db_conn:
        sorted_playlist = db_conn.sort_playlist(playlist_name, 'track_name')

    return render_template('sorted_playlist.html', sorted_playlist=sorted_playlist)

if __name__ == '__main__':
    app.run(debug=True)
