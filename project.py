from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response

# Imports for database
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Cities, Destinations, User

# Imports for Http server
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# renaming session because sqlalchemy already uses session function for DB session
from flask import session as login_session
import random, string

# Required for google oauth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

# Declare client ID by getting the information from client secret's json file from google console
CLIENT_ID =json.loads(open('client_secret.json', 'r').read())['web']['client_id']

app = Flask(__name__)

# Create postgresql session and connect to database
engine = create_engine('postgresql+psycopg2:///cities')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a login page that uses google and facebook authentication 
@app.route('/login')
def showLogin():
    # Create a state token using random uppercase and numbers to prevent CSRF.
    state=''.join(random.choice(string.ascii_uppercase+string.digits) for x in xrange(32))
    # store state in login session object under the name state
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Verify that state tokens match
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store one time code if the state tokens match
    code  = request.data
    try:
        # Create oauth flow object and add clients secret key
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        # specify this is a one time auth code using postmessage
        oauth_flow.redirect_uri = 'postmessage'
        # Trade one time auth code into a credentials object
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        # if a flow exchange error occurs, return a failed response
        response = make_response(json.dumps('Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see that the access token is valid
    access_token = credentials.access_token
    # Append the received access token to a google api url to verify that it is a valid token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, return an error message
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token and is used for the intended user id and client id.
    gplus_id = credentials.id_token['sub']
    # If the user id returned by google api server does not match our google plus id token
    if result['user_id'] != gplus_id:
        # Send failure because we get a user id that does not match our access token
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # if the google api server did not issue the access token to our client id
    if result['issued_to'] != CLIENT_ID:
        # Send failure because our token client id does not match our client id
        response = make_response(json.dumps("Token's client ID doesn't match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        # If the user is already logged in, we do not need to reset all the login session variables
        response = make_response(json.dumps('Current user is already connected', 200))
        response.headers['Content-Type'] = 'application/json'
        return response


    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id']= gplus_id

    # Get additional user info from google and store in a data object
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json' }
    answer = requests.get(userinfo_url, params = params)
    data = answer.json()

    # Store user data into login session
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]
    login_session['provider'] = 'google'

    # check if user exists in user DB, if it doesn't make a new entry
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Display a welcome screen and flash 
    output = ''
    output += '<h1> Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " stype = "width:300px; height: 300px; border-radius:150px; -webkit-border-radius:150px; -moz-border-radius:150px;">'
    flash("you are now logged in as %s" %login_session['username'])
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session.
@app.route("/gdisconnect")
def gdisconnect():
    # Check if there is a user to disconnect
    credentials = login_session.get('credentials')

    # If the credential field is empty, there is no user to disconnect
    if credentials is None:
        response = make_response(json.dumps('Current user is not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Use google's api to revoke credentials of the stored access token 
    # credentials only stores the access token
    access_token = credentials
    url = ('https://www.googleapis.com/o/oauth2/revoke?token=%s' %access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # If the resulting response is successful(200) delete all user login information
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # If google api server did not sucessfully revoke token credentials
    else: 
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Use state token to preven CSRF
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data
  
    # Exchange client token for long-lived server-side token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
  
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token since it is not needed to make api calls
    token = result.split("&")[0]
  
    # 
    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
  
    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token
  
    # Need to use a seperate API call to get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
  
    login_session['picture'] = data["data"]["url"]
  
    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
      user_id = createUser(login_session)
    login_session['user_id'] = user_id
  
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
  
    flash("Now logged in as %s" % login_session['username'])
    return output

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# JSON endpoints
@app.route('/city/<int:city_id>/destinations/JSON')
def allDestinationsAtCityJSON(city_id):
    allDestinations = session.query(Destinations).filter_by(
        city_id=city_id).all()
    return jsonify(destinations=[destination.serialize for destination in allDestinations])

@app.route('/city/<int:city_id>/destinations/<int:destination_id>/JSON')
def singleDestinationJSON(city_id, destination_id):
    singleDestination = session.query(Destinations).filter_by(destination_id=destination_id).one()
    return jsonify(destination=singleDestination.serialize)

@app.route('/city/JSON')
def citiesJSON():
    cities = session.query(Cities).all()
    return jsonify(cities=[city.serialize for city in cities])

# Home page
@app.route('/')
@app.route('/city/')
def showCities():
    # Print all entries in Cities
    cities = session.query(Cities).all()
    if 'username' not in login_session:
        return render_template('publicCity.html', cities=cities)
    else:
        return render_template('city.html', cities=cities)

# Create a new city
@app.route('/city/new/', methods=['GET', 'POST'])
def newCity():
    # Secure the creating of Cities by redirected to a login page if a user is not loggined in
    if 'username' not in login_session:
        return redirect('/login')
    # Get name from form and create a new city entry 
    if request.method == 'POST':
        cityObject = Cities(name=request.form['name'], user_id=login_session['user_id'], image=request.form['image'] )
        session.add(cityObject)
        session.commit()
        flash('New City %s Successfully Created' % cityObject.name)
        return redirect(url_for('showCities'))
    # Load form to create a new city
    else:
        return render_template('newCity.html')

# Edit an existing city
@app.route('/city/<int:city_id>/edit/', methods=['GET', 'POST'])
def editCity(city_id):
    # Secure the creating of Cities by redirected to a login page if a user is not loggined in
    if 'username' not in login_session:
        return redirect('/login')
    cityToEdit = session.query(Cities).filter_by(id=city_id).one()
    # Prevent unauthorized users from editing cities they do not own
    if cityToEdit.user_id != login_session['user_id']:
        flash('You are not authorized to edit this city.')
        return redirect(url_for('showCities'))
    if request.method == 'POST':
        if request.form['name']:
            cityToEdit.name = request.form['name']
        if request.form['image']:
            cityToEdit.image = request.form['image']
            flash('New City %s Successfully Edited' % cityToEdit.name)
            return redirect(url_for('showCities'))
    else:
        return render_template('editCity.html', city=cityToEdit)

# Delete an existing city
@app.route('/city/<int:city_id>/delete/', methods=['GET', 'POST'])
def deleteCity(city_id):
    # Secure the creating of Cities by redirected to a login page if a user is not loggined in
    if 'username' not in login_session:
        return redirect('/login')
    cityToDelete = session.query(Cities).filter_by(id=city_id).one()
    # Prevent unauthorized users from deleting cities they do not own
    if cityToDelete.user_id != login_session['user_id']:
        flash('You are not authorized to delete this city.')
        return redirect(url_for('showCities'))
    destinationsDelete = session.query(Destinations).filter_by(city_id=city_id)
    if request.method == 'POST':
        for destinationDelete in destinationsDelete:
            session.delete(destinationDelete)
            session.commit()
        session.delete(cityToDelete)
        session.commit()
        flash('New City %s Successfully Deteled' % cityToDelete.name)
        return redirect(url_for('showCities'))
    else:
        return render_template('deleteCity.html', city=cityToDelete)

######
# Destination
######
# Show the destinations at city
@app.route('/city/<int:city_id>/')
@app.route('/city/<int:city_id>/destinations/')
def showDestinations(city_id):
    # Get the first city entry that matches the given id
    city = session.query(Cities).filter_by(id=city_id).one()
    allDestinations = session.query(Destinations).filter_by(
        city_id=city_id).all()

    # Get the user id of the user that created the given city
    creator = getUserInfo(city.user_id)
    if 'username' not in login_session or not creator or creator.id != login_session['user_id']:
        return render_template('publicDestinations.html', destinations=allDestinations, city=city)
    else:
        return render_template('destinations.html', destinations=allDestinations, city=city)

@app.route('/city/<int:city_id>/destinations/new/', methods=['GET', 'POST'])
def newDestinations(city_id):
    # Secure the creating of Cities by redirected to a login page if a user is not loggined in
    if 'username' not in login_session:
        return redirect('/login')
    parentCity = session.query(Cities).filter_by(id=city_id).one()
    # Only the creator of the city can add new destinations
    if parentCity.user_id != login_session['user_id']:
        flash('You are not authorized to make a new destination in this city.')
        return redirect(url_for('showDestinations', city_id=city_id))
    if request.method == 'POST':
        # Set the user id of the destination to be the same user id as the city it is associated with
        newDestination = Destinations(name=request.form['name'], description=request.form
                            ['description'], price=request.form['price'], image=request.form['image'], 
                            city_id=city_id, user_id=parentCity.user_id)
        session.add(newDestination)
        session.commit()
        flash('New Destination %s Successfully Created' % newDestination.name)
        return redirect(url_for('showDestinations', city_id=city_id))
    else:
        return render_template('newDestinations.html', city_id=city_id)

@app.route('/city/<int:city_id>/destinations/<int:destination_id>/edit',
           methods=['GET', 'POST'])
def editDestinations(city_id, destination_id):
    # Secure the creating of Cities by redirected to a login page if a user is not loggined in
    if 'username' not in login_session:
        return redirect('/login')
    parentCity = session.query(Cities).filter_by(id=city_id).one()
    # Only the creator of the city can edit destinations
    if parentCity.user_id != login_session['user_id']:
        flash('You are not authorized to edit destinations in this city.')
        return redirect(url_for('showDestinations', city_id=city_id))
    editedDestination = session.query(Destinations).filter_by(id=destination_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedDestination.name = request.form['name']
        if request.form['description']:
            editedDestination.description = request.form['description']
        if request.form['price']:
            editedDestination.price = request.form['price']
        if request.form['image']:
            editedDestination.image = request.form['image']
        session.add(editedDestination)
        session.commit()
        return redirect(url_for('showDestinations', city_id=city_id))
    else:

        return render_template(
            'editDestinations.html', city_id=city_id, 
            destination_id=destination_id, destinations=editedDestination)

@app.route('/city/<int:city_id>/destinations/<int:destination_id>/delete',
           methods=['GET', 'POST'])
def deleteDestinations(city_id, destination_id):
    # Secure the creating of Cities by redirected to a login page if a user is not loggined in
    if 'username' not in login_session:
        return redirect('/login')
    parentCity = session.query(Cities).filter_by(id=city_id).one()
    # Only the creator of the city can delete destinations
    if parentCity.user_id != login_session['user_id']:
        flash('You are not authorized to delete destinations in this city.')
        return redirect(url_for('showDestinations', city_id=city_id))
    destinationsDelete = session.query(Destinations).filter_by(id=destination_id).one()
    if request.method == 'POST':
        session.delete(destinationsDelete)
        session.commit()
        return redirect(url_for('showDestinations', city_id=city_id))
    else:
        return render_template('deleteDestinations.html', city_id=city_id, destinations=destinationsDelete)

# Helper functions

# Disconnect based on provider and delete all entries in loginsession
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCities'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCities'))

# Get user id associated with input email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Get a user object associated to the input user id
def getUserInfo(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None

# Uses the login_session information from google or facebook and creates a new entry in the User DB
# Returns the user id generated by the DB when the user is created
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()

    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id
  
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)