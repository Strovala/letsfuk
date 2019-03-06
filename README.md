# letsfuk

## Install postgre
Install PostgreSQL in Linux using the command,

    sudo apt-get install postgresql postgresql-contrib
Now create a superuser for PostgreSQL

    sudo -u postgres createuser --superuser name_of_user
And create a database using created user account

    sudo -u name_of_user createdb name_of_database
You can access created database with created user by,

    psql -U name_of_user -d name_of_database

_Note that if you created the name_of_user and name_of_database as your user name on your machine, you can access that database with that user with psql command_
## Staritng code
    from flask import Flask, request
    
    app = Flask(__name__)
    
    @app.route("/")
    def hello():
        return "Hello World!"
    
    @app.route("/name/<name>")
    def get_book_name(name):
        return "name : {}".format(name)
    
    @app.route("/details")
    def get_book_details():
        author=request.args.get('author')
        published=request.args.get('published')
        return "Author : {}, Published: {}".format(author,published)
    
    if __name__ == '__main__':
        app.run()

## Create database
First create the database we need here for our application named books_store

    sudo -u name_of_user createdb <database_name>
Now you can check the created database with,

    psql -U name_of_user -d <database_name>

## Create configurations
config.py

    import os
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    class Config(object):
        DEBUG = False
        TESTING = False
        CSRF_ENABLED = True
        SECRET_KEY = 'this-really-needs-to-be-changed'
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    
    
    class ProductionConfig(Config):
        DEBUG = False
    
    
    class StagingConfig(Config):
        DEVELOPMENT = True
        DEBUG = True
    
    
    class DevelopmentConfig(Config):
        DEVELOPMENT = True
        DEBUG = True
    
    
    class TestingConfig(Config):
        TESTING = True
    view raw
    
According to created configurations set “APP_SETTINGS” environment variable by running this in the terminal

export APP_SETTINGS="config.DevelopmentConfig"
Also add “DATABASE_URL” to environment variables. In this case our database URL is based on the created database. So, export the environment variable by this command in the terminal,

export DATABASE_URL="postgresql://localhost/books_store"
It should be returned when you execute echo $DATABASE_URL in terminal.
So, now our python application can get database URL for the application from the environment variable which is “DATABASE_URL”

also put these 2 environment variables into a file called .env

.env

    export APP_SETTINGS="config.DevelopmentConfig"
    export DATABASE_URL="postgresql://localhost/<database_name>"

## Database migration
app.py

    from flask import Flask, request
    from flask_sqlalchemy import SQLAlchemy
    
    app = Flask(__name__)
    
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    
    from models import Book
    
    @app.route("/")
    def hello():
        return "Hello World!"

    from app import db

models.py

    class Book(db.Model):
        __tablename__ = 'books'
    
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String())
        author = db.Column(db.String())
        published = db.Column(db.String())
    
        def __init__(self, name, author, published):
            self.name = name
            self.author = author
            self.published = published
    
        def __repr__(self):
            return '<id {}>'.format(self.id)
        
        def serialize(self):
            return {
                'id': self.id, 
                'name': self.name,
                'author': self.author,
                'published':self.published
            }
manage.py

    from flask_script import Manager
    from flask_migrate import Migrate, MigrateCommand
    
    from app import app, db
    
    migrate = Migrate(app, db)
    manager = Manager(app)
    
    manager.add_command('db', MigrateCommand)
    
    
    if __name__ == '__main__':
        manager.run()
        
Now we can start migrating database. First run,

    python manage.py db init
This will create a folder named migrations in our project folder. To migrate using these created files, run

    python manage.py db migrate


Now apply the migrations to the database using

    python manage.py db upgrade
This will create the table books in books_store database. you can check it in PostgreSQL command line inside books_store database by \dt command.


In a case of migration fails to be success try droping auto generated alembic_version table by drop table alembic_version;
You can check the columns of the books table by \d books command.

## Finishing

app.py
    
    import os
    from flask import Flask, request, jsonify
    from flask_sqlalchemy import SQLAlchemy
    
    app = Flask(__name__)
    
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    
    from models import Book
    
    @app.route("/")
    def hello():
        return "Hello World!"
    
    @app.route("/add")
    def add_book():
        name=request.args.get('name')
        author=request.args.get('author')
        published=request.args.get('published')
        try:
            book=Book(
                name=name,
                author=author,
                published=published
            )
            db.session.add(book)
            db.session.commit()
            return "Book added. book id={}".format(book.id)
        except Exception as e:
    	    return(str(e))
    
    @app.route("/getall")
    def get_all():
        try:
            books=Book.query.all()
            return  jsonify([e.serialize() for e in books])
        except Exception as e:
    	    return(str(e))
    
    @app.route("/get/<id_>")
    def get_by_id(id_):
        try:
            book=Book.query.filter_by(id=id_).first()
            return jsonify(book.serialize())
        except Exception as e:
    	    return(str(e))
    
    if __name__ == '__main__':
        app.run()
        
Start it by running

    python manage.py runserver
