from flask import Flask, render_template, request, redirect, jsonify, url_for, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import logging
from flask import session as login_session
import random
import string
import httplib2
import json
import os
from oauth2client import client, crypt
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Item Catalog"
APPS_DOMAIN_NAME = 'http://localhost:8181'


engine = create_engine('sqlite:///itemcatalogusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/tokensignin', methods=['POST'])
def tokensignin():
    token = request.form['idtoken']
    try:
        # import pdb
        # pdb.set_trace()
        idinfo = client.verify_id_token(token, CLIENT_ID)

        app.logger.info(idinfo)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")

    except crypt.AppIdentityError:
        return "Wrong"
        # Invalid token
    userid = idinfo['sub']
    login_session['username'] = idinfo['name']
    login_session['picture'] = idinfo['picture']
    login_session['email'] = idinfo['email']
    user_id = getUserID(login_session['email'])
    app.logger.info("=======================login_session")
    app.logger.info(login_session)
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return userid


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html')


@app.route('/')
def home():
    categories = session.query(Category)
    items = session.query(Item).order_by(Item.last_modified.desc()).limit(10)
    return render_template('home.html', categories=categories, items=items)


@app.route('/catalog/<categoryname>/item/JSON')
def CategoryitemJSON(categoryname):
    category = session.query(Category).filter_by(name=categoryname).one()
    items = session.query(Item).filter_by(
        category_id=category.id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/catalog/JSON')
def CategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show a category item
@app.route('/catalog/<categoryname>/')
@app.route('/catalog/<categoryname>/items')
def showcategory(categoryname):
    category = session.query(Category).filter_by(name=categoryname).one()
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(
        category_id=category.id).all()
    return render_template('categories.html',
                           items=items,
                           categories=categories,
                           category=category)


@app.route('/catalog/items/<itemname>/')
def showitem(itemname):
    item = session.query(Item).filter_by(name=itemname).one()
    app.logger.info('USER ID ==============' + str(item.user_id )  )
    creator = getUserInfo(item.user_id)
    permission = login_session['user_id'] == creator.id
    item = session.query(Item).filter_by(name=itemname).one()
    return render_template('item.html',
                           item=item, permission = permission)

@app.route(
    '/catalog/new/', methods=['GET', 'POST'])
def newitem():
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    if request.method == 'POST':
        app.logger.info("Posting")
        app.logger.info(request.form['name'])
        app.logger.info(request.form['category'])
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            imgpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(imgpath)
            imgsrc='images/'+filename
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=request.form['category'],
                       user_id=login_session['user_id'],
                       imgsrc=imgsrc)
        session.add(newItem)
        session.commit()
        category = session.query(Category).filter_by(id=request.form['category']).one()
        app.logger.info(request.form)

        return redirect(url_for('showcategory', categoryname=category.name))
    else:

        return render_template('newItem.html', categories=categories)

    return render_template('newItem.html', categories=categories)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Edit a item item
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
        session.add(item)
        session.commit()
        return redirect(url_for('showitem', itemname=item.name))
    else:

        return render_template('editItem.html', item=item, categories=categories)

    return render_template('editItem.html', item=item, categories=categories)


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

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404
#
# @app.errorhandler(403)
# def page_not_found(e):
#     return render_template('403.html'), 403

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8181)
