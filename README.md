# MELOMIX

## Description
MELOMIX is a multi-user music streaming app like spotify, gaana. It is used for reading & listening songs. A user can
register as creator to upload songs & albums. Users can rate and report songs, playlists and albums.


## Technologies used

- [Flask]: for basic backend Implementation.
- [Flask_sqlalchemy]: Flask-SQLAlchemy is an extension for Flask that adds support for SQLAlchemy to your application, for implementing Database.
- [Flask_Login]: for implementing the login functionality, user session management. common tasks of logging in, logging out, and remembering your users’ sessions over extended periods of time.
- [Datetime]: to storing the date and time (date of creation).
- [pytz]: for date-time conversion
- [flash]: to show alerts
- [Flask-Restful]: to create Apis
- [matplotlib]: for ploting graphs
- [werkzeug.security]: for hashing the password 
- [jinja2]: It is a text-based template language and thus can be used to generate any markup as well as source code
- [render_template]: render_template is a Flask function that typically imported directly from the flask. It is used to generate output from a template file based on the Jinja2 engine that is found in the application's templates folder Some libraries imprender_template, redirect, and url_for displaying HTML content

## API Design
There are three API:
- UserAPI
    - It has two endpoints:
        • /api/users : With this endpoint, we can read all users details in database, creating user.
        • /api/user/<int:user_id> : With this endpoint, we can get user with input id,
            update user with respective input id, delete user with respective input id
- SongAPI
    - It has four endpoints:
        • /api/songs : With this endpoint, we can read all songs details in database.
        • /api/song/<int:song_id> : With this endpoint, we can read song with respective input id
        • /api/creator/<int:creator_id>/songs: With this endpoint, we can read all songs of respective
            creator and also create songs under respective creator
        • /api/creator/<int:creator_id>/song/<int:song_id>: With this endpoint, we can get respective
            song of respective creator. We can also update and delete respective song associated with
            respective creator with this endpoint.
- PlaylistAPI
    - It has four endpoints:
        • /api/playlists: With this endpoint, we can read all playlists in database
        • /api/playlist/<int:playlist_id>: With this endpoint, we can read playlist with respective input id
        • /api/user/<int:user_id>/playlists: With this endpoint, we can read all playlists of respective user
            and also create playlists under respective user
        • /api/user/<int:user_id>/playlist/<int:playlist_id>: With this endpoint, we can get respective
            playlist of respective user. We can also update and delete respective playlist associated with
            respective user with this endpoint.


## Architecture and Features
• There are 2 controllers
    **1. auth**: It is used for authorization purpose
    **2. view**: It is used for all other purpose like viewing ,creating and searching songs, playlists, albums .
• There are 2 folders
    **1. static**: It contains CSS file and images
    **2. templates**: It contains all HTML templates used in Project.
• **login & sign-up system**: Here user should fill in details for creating a new account and after that user will be able to
    do login.
• **User Home Page**: All songs, playlists & albums will be displayed in this page
• **User Profile Page**: Page to view user’s details and update some details
• **Creator - register page**: For registering as a creator.
• **Song Page**: To read lyrics, play and rate a song
• **Search**: To search songs, playlists, albums based on names, created by and genres.
• **Admin’s Dashboard**: Contains statistics of the App, song/playlist/album management, creator management.
• **APIs**: Three APIs User, Song, Playlist with CRUD functionalities

# Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r requirements.txt
```

# Local Development Run

- Simply run `python main.py` , it will initiate the flask app in development.

# Replit run

- Click on `main.py` and click button run
- The web app will be available

# Folder Structure

- `instance` has the `msapp.db` DB.
- `static` has the css file and Images.
- `templates` has all the html template files.

```

├───── main.py
├───── instance
|        ├───msapp.db
├───── readme.md
├───── web
|        ├───apis
|        |      ├───SongAPI.py
|        |      ├───user_api.py
|        |      └── validation.py
│        ├───static
|        |     ├─ album_coverphoto
|        |     ├─ decors
|        |     ├─ playlist_coverphoto
|        |     ├─ profile_photos
|        |     ├─ song_coverphoto
|        |     ├─ songs
|        |     └── style.css
|        ├───templates
|        |       ├─ adminhome.html
|        |       ├─ adminlogin.html
|        │       ├─ adminmanage1.html
|        │       ├─ adminmanage2.html
|        │       ├─ albumdisplay.html
|        │       ├─ createalbum.html
|        │       ├─ createplaylist.html
|        |       ├─ createsong.html
|        |       ├─ creatorhome.html
|        │       ├─ admindashboard.html
|        |       ├─ creatorRegistor.html
|        |       ├─ editsong.html
|        │       ├─ editalbum.html
|        |       ├─ editplaylist.html
|        |       ├─ playlistdisplay.html
|        │       ├─ register.html
|        |       ├─  search.html
|        |       ├─ song.html
|        |       ├─ userhome.html
|        |       ├─ userlogin.html
|        |       ├─ userprofile.html
|        |       └── user_view.html
│        ├─ __init__.py
|        ├─ auth.py
|        ├─ models.py
│        └─ diff_views.py
├───── report.pdf
└───── requirements.txt
```
