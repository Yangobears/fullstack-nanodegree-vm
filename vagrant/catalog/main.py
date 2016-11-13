from flask import (Flask, render_template, request, redirect, jsonify,
                   url_for, abort, flash)
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import random
import string
import httplib2
import json
import os
from oauth2client import client, crypt
from werkzeug.utils import secure_filename
import pdb

# Init app
app = Flask(__name__)

# File upload Config
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Limit file size
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

# Load Client ID
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Item Catalog"
APPS_DOMAIN_NAME = 'http://localhost:8181'


engine = create_engine('sqlite:///itemcatalogusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Helper Functions


def createUser(login_session):
    # Create new user with info stored in login_session
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    # Get user info by user id
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    # Get user id by email
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Helper function for checking allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Delete all the session info when signing out
@app.route('/signout', methods=['POST'])
def signout():
    del login_session['user_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    return "Sign out"


# Store user info in login_session and create user after
# id verified  by  Google API Client Library
@app.route('/tokensignin', methods=['POST'])
def tokensignin():
    token = request.form['idtoken']
    try:
        idinfo = client.verify_id_token(token, CLIENT_ID)
        if idinfo['iss'] not in ['accounts.google.com',
                                 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
    except crypt.AppIdentityError:
        flash("App Identity Error")
        return redirect(request.url)
    # userid is the google user id
    userid = idinfo['sub']
    login_session['username'] = idinfo['name']
    login_session['picture'] = idinfo['picture']
    login_session['email'] = idinfo['email']
    # user_id is the id of user in the db.
    user_id = getUserID(login_session['email'])
    if not user_id:
        # Create new user in db
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    return userid


# Home page, show all categories and items.
@app.route('/')
def home():
    permission = 'username' in login_session
    categories = session.query(Category)
    items = session.query(Item).order_by(Item.last_modified.desc()).limit(10)
    return render_template('home.html', categories=categories,
                           items=items, permission=permission)


# Show item by category
@app.route('/catalog/<categoryname>/')
@app.route('/catalog/<categoryname>/items')
def showcategory(categoryname):
    permission = 'username' in login_session
    category = session.query(Category).filter_by(name=categoryname).one()
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(
        category_id=category.id).all()
    return render_template('categories.html',
                           items=items,
                           categories=categories,
                           category=category,
                           permission=permission)


# Show all item in JSON format
@app.route('/catalog/<categoryname>/item/JSON')
def CategoryitemJSON(categoryname):
    category = session.query(Category).filter_by(name=categoryname).one()
    items = session.query(Item).filter_by(
        category_id=category.id).all()
    return jsonify(items=[i.serialize for i in items])


# Show all catalog in JSON format
@app.route('/catalog/JSON')
def CategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show specific item
@app.route('/catalog/items/<itemname>/')
def showitem(itemname):
    item = session.query(Item).filter_by(name=itemname).one()
    creator = getUserInfo(item.user_id)
    permission = ('user_id' in login_session) and (login_session['user_id']
                                                   == creator.id)
    imgexists = item.imgsrc is not None
    item = session.query(Item).filter_by(name=itemname).one()
    return render_template('item.html',
                           item=item,
                           permission=permission,
                           imgexists=imgexists)


# Create new item
@app.route(
    '/catalog/new/', methods=['GET', 'POST'])
def newitem():
    categories = session.query(Category).all()
    if request.method == 'POST':
        if 'username' not in login_session:
            flash("Please log in first")
            return redirect(request.url)
        if request.form['name'] == '':
            flash('Please enter a name')
            return redirect(request.url)
        if request.form['description'] == '':
            flash('Please enter a description')
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            imgpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(imgpath)
            imgsrc = 'images/' + filename
        else:
            imgsrc = None

        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=request.form['category'],
                       user_id=login_session['user_id'],
                       imgsrc=imgsrc)
        session.add(newItem)
        session.commit()
        category = session.query(Category).filter_by(
            id=request.form['category']).one()
        return redirect(url_for('showcategory', categoryname=category.name))
    return render_template('newItem.html', categories=categories)


@app.route(
    '/catalog/<itemname>/edit', methods=['GET', 'POST'])
def edititem(itemname):
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(name=itemname).one()
    creator = getUserInfo(item.user_id)
    if login_session['user_id'] != creator.id:
        abort(403)
        return
    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.category_id = int(request.form['category'])
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            imgpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(imgpath)
            imgsrc = 'images/' + filename
            item.imgsrc = imgsrc

        session.add(item)
        session.commit()
        return redirect(url_for('showitem', itemname=item.name))
    else:
        return render_template('editItem.html',
                               item=item, categories=categories)
    return render_template('editItem.html', item=item, categories=categories)


# Delete item
@app.route(
    '/catalog/<itemname>/delete', methods=['GET', 'POST'])
def deleteitem(itemname):
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(name=itemname).one()
    category = session.query(Category).filter_by(id=item.category_id).one()
    creator = getUserInfo(item.user_id)
    if login_session['user_id'] != creator.id:
        abort(403)
        return
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('showcategory', categoryname=category.name))
    else:

        return render_template('deleteItem.html', item=item)

    return render_template('deleteItem.html', item=item)


@app.errorhandler(413)
def file_too_big(e):
    flash("File too big")
    return redirect(request.url), 413
#
# @app.errorhandler(403)
# def page_not_found(e):
#     return render_template('403.html'), 403

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8181)
