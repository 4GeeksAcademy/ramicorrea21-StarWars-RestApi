"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, People, Planets, Users, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#Get a list of all the people in the database
@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    return jsonify(list(map(lambda p: p.serialize(), people))), 200


#Get a one single people information
@app.route('/people/<int:id>', methods=['GET'])
def get_single_people(id):
    single_people = People.query.get(id)
    if single_people is None:
        return jsonify({"message": "person not found"}), 404
    return(single_people.serialize())

# Get a list of all the planets in the database
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    return jsonify(list(map(lambda p: p.serialize(), planets))), 200

# Get one single planet information
@app.route('/planets/<int:id>', methods=['GET'])
def get_single_planets(id):
    single_planet = Planets.query.get(id)
    if single_planet is None:
        return jsonify({"message": "planet not found"}), 404
    return jsonify(single_planet.serialize()), 200

#Get a list of all the blog post users
@app.route('/users', methods=['GET'])
def get_all_users():
    users = Users.query.all()
    return jsonify(list(map(lambda usr: usr.serialize(), users)))

#Get all the favorites that belong to the current user.
@app.route('/users<int:id>/favorites', methods=['GET'])
def get_favorites(id):
    user = Users.query.get(id)
    if user is None:
        return jsonify({"message": f"user{id} not found"}), 404
    if user.favorites == []:
        return jsonify({"message": f"user{id} has no favorites"}), 400
    result = []
    for favorite in user.favorites:
        result.append(favorite.serialize())
    return jsonify(result), 200

#Add a new favorite planet to the current user with the planet id 
@app.route('/user<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
def post_planet_favorite(user_id, planet_id):
    user = Users.query.get(user_id)
    planet = Planets.query.get(planet_id)
    if user is None:
        return jsonify({"message": f"user{user_id} not found"}), 404
    if planet is None:
        return jsonify({"message": "planet not found"}), 404
    favorite = Favorites(user_id=user.id, planets_id=planet.id)
    db.session.add(favorite)
    try:
        db.session.commit()
        return jsonify({"msg": "Planet added to favorites"}), 200
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500

#Add new favorite people to the current user with the people id = people_id.
@app.route('/user<int:user_id>/favorite/people/<int:people_id>', methods=['POST'])
def post_people_favorites(user_id, people_id):
    user = Users.query.get(user_id)
    people = People.query.get(people_id)

    if user is None:
        return jsonify({"message": f"user{user_id} not found"}), 404
    if people is None:
        return jsonify({"message": "people not found"}), 404
    
    favorite = Favorites(user_id=user.id, people_id=people.id)
    db.session.add(favorite)

    try:
        db.session.commit()
        return jsonify({"msg": "People added to favorites"}), 200
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500

#Delete favorite planet with the id = planet_id.
@app.route('/user<int:user_id>/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_fav(user_id, planet_id):
    user = Users.query.get(user_id)
    planet = Planets.query.get(planet_id)

    if user is None:
        return jsonify({"message": f"user{user_id} not found"}), 404
    if planet is None:
        return jsonify({"message": "planet not found"}), 404
    
    favorite = Favorites.query.filter_by(user_id=user.id, planets_id=planet.id).first()
    
    if favorite is None:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(favorite)
    try:
        db.session.commit()
        return jsonify({"msg": "Planet deleted from favorites"}), 200
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500

# Delete favorite people with the id = people_id.
@app.route('/user<int:user_id>/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_fav(user_id, people_id):
    user = Users.query.get(user_id)
    people = People.query.get(people_id)

    if user is None:
        return jsonify({"message": f"user{user_id} not found"}), 404
    if people is None:
        return jsonify({"message": "people not found"}), 404
    
    favorite = Favorites.query.filter_by(user_id=user.id, people_id=people.id).first()

    db.session.delete(favorite)
    try:
        db.session.commit()
        return jsonify({"msg": "People deleted from favorites"}), 200
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
