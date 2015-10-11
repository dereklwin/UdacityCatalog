Travel Catalog
==============================================
This website is a travel catalog of cities in a country and the various destinations that can be visited. The main page is a landing page with a list of all cities. Clicking on the name or image of the city will route to a page with all the destinations in the city. Each city and destination can only be modified by the original creator of the city. 

The catalog uses Flask framework to generate the webpages. 
Sqlalchemly along with postgresql to manage the content of the webpage. 
Bootstrap was used to style the pages and make it more dynamic. 
Secure signin is created by using Google's and Facebook's OAuth APIs

Setup database
----------------------------------------------
On the first run, user should create a database called cities using the following commands
psql
CREATE DATABASE cities;

Next configure the database using database_setup.py. Followed by filling the database with usable data using filldb.py

To Run
----------------------------------------------
After following the Setup database guide, run the project.py file to start the server. The catalog can then be accessed at http://localhost:5000.

If the database is ever messed up, run the filldb.py script to reset the database to default.

Included files
----------------------------------------------
project.py             : main file that contains handles all routing, login information, and database modifications.
database_setup.py      : code to setup database and map to sqlalchemy
filldb.py              : fills the cities database with usable entries
client_secret.json     : json file containing the client secret key for google authorization
fb_client_secret.json  : json file containing the client secret key for facebook authorization
templates              : folder containing all HTML files used by Catalog
static                 : folder containing all CSS files used by Catalog
