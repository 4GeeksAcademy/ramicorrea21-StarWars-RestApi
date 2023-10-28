from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class People(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(50), nullable=False, unique=True)
   eye_color = db.Column(db.String(20), nullable=False, unique=False)
   is_alive = db.Column(db.Boolean(), nullable=False, unique=False)
   favorites = db.relationship('Favorites', uselist=True, backref='People')

   def serialize(self):
      return{
         "id": self.id,
         "name": self.name,
         "eye_color": self.eye_color,
         "is_alive": self.is_alive
      }
   
class Planets(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(50), nullable=False, unique=True)
   population = db.Column(db.Integer, nullable=False, unique=False)
   climate = db.Column(db.String(20), nullable=False, unique=False)
   favorites = db.relationship('Favorites', uselist=True, backref='Planets')

   def serialize(self):
      return{
        "id": self.id,
        "name": self.name,
        "population" : self.population,
        "climate": self.climate
      }
   
class Users(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(50), nullable=False, unique=True)
   email = db.Column(db.String(20), nullable=False, unique=True)
   favorites = db.relationship('Favorites', uselist=True, backref='Users')
   def serialize(self):
      return{
         "id": self.id,
         "name": self.name,
         "email": self.email
      }

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    planets_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=True)

    def serialize(self):
       return{
          "id": self.id,
          "user_id": self.user_id,
          "people_id": self.people_id,
          "planets_id": self.planets_id
       }