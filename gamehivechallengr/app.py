import os
import sys

from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, validates


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://gamehive:gamehive@postgres:5432/test_db'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True


app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig
}


# Initialize a SQLAlchemy instance
config_name = 'development'
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(app_config[config_name])
db = SQLAlchemy(app)


class Guild(db.Model):
    __tablename__ = 'guild'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    country_code = db.Column(db.String, nullable=True)
    members = relationship('Player', back_populates='guild', lazy=True)

    def __init__(self, name, members, country_code=None):
        self.name = name
        assert len(
            members) >= 2, "Your guild would be too lonely with just you, try to get more members!"
        for m in members:
            self.members.append(m)
        self.country_code = country_code

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Guild.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    skill_points = db.Column(db.Integer)

    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"))
    guild = relationship("Guild", back_populates="members")

    # Map many items to single player
    inventory = relationship(
        "Item", back_populates='player', cascade='all, delete, delete-orphan')

    def __init__(self, nickname, email, skill_points=0):
        self.nickname = nickname
        self.email = email
        self.skill_points = skill_points

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Player.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address, "Email is not valid!"
        return address.lower()

    def __repr__(self):
        return "<Player: {}>".format(self.nickname)


class Item(db.Model):
    __tablename__ = 'game_item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    skill_points = db.Column(db.Integer)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player = relationship("Player", back_populates="inventory")

    def __init__(self, name, skill_points):
        self.name = name
        self.skill_points = skill_points

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


@app.route('/')
def root():
    return 'Game Hive Player API'


@app.route('/players', methods=['POST', 'GET'])
def players():
    if request.method == 'POST':
        # Create a new player
        name = str(request.get_json().get('nickname', 'Untitled Player'))
        email = str(request.get_json().get('email', ''))
        skill_points = int(request.get_json().get('skill_points', 0))

        try:
            player = Player(name, email, skill_points)
            player.save()

            response = jsonify({
                "success": "true",
                "player": {
                    "id": player.id,
                    "nickname": player.nickname
                }
            })
            response.status_code = 201

            return response
        except AssertionError as AE:
            abort(500, AE)
    else:
        # GET
        players = Player.get_all()
        results = []
        for player in players:
            print(player)
            results.append({
                'id': player.id,
                'nickname': player.nickname,
                'email': player.email,
                'skill_points': player.skill_points,
                'inventory': player.inventory,
                'guild': player.guild.name if player.guild is not None else player.guild,
            })
        response = jsonify(results)
        response.status_code = 200

        return response


@app.route('/players/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def player_manipulation(id, **kwargs):
    # retrieve a player using it's ID
    player = Player.query.filter_by(id=id).first()
    if not player:
        # Raise an HTTPException with a 404 not found status code
        response = jsonify({
            'message': 'Player not found'
        })
        response.status_code = 404
        return response

    if request.method == 'DELETE':
        player.delete()
        response = jsonify({
            "message": "player {} deleted successfully".format(player.id)
        })
        response.status_code = 200
        return response

    elif request.method == 'PUT':
        data = dict(request.get_json())

        # Get input data, filter and set
        if data.get('nickname') is not None:
            player.nickname = data['nickname']
        if data.get('email') is not None:
            player.email = data['email']

        player.save()

        response = jsonify({
            'message': 'success',
            'player': {
                'id': player.id,
                'nickname': player.nickname
                }
        })
        response.status_code = 200
        return response

    else:
        # GET
        response = jsonify({
            'id': player.id,
            'nickname': player.nickname,
            'email': player.email,
            'skill_points': player.skill_points,
            'inventory': player.inventory,
            'guild': player.guild,
        })
        response.status_code = 200
        return response


@app.route('/guilds', methods=['POST', 'GET'])
def guilds():
    if request.method == 'POST':
        # Create a new guild
        req_data = request.get_json()
        name = str(req_data.get('name', 'Untitled Guild'))
        country_code = str(req_data.get('country_code', None))
        # Filter members who don't belong to a guild right now
        members = list(filter(lambda p: p.guild is None, [Player.query.filter_by(
            id=p['id']).first() for p in req_data.get('members')]))
        try:
            guild = Guild(name, members, country_code)
            guild.save()
            response = jsonify({
                "success": "true",
                "guild": {
                    "id": guild.id,
                    "name": guild.name
                }
            })
            response.status_code = 201

            return response
        except Exception as e:
            response = jsonify({"message": str(e)})
            response.status_code = 500
            return response

    else:
        # GET
        guilds = Guild.get_all()

        results = []

        for guild in guilds:
            results.append({
                'id': guild.id,
                'name': guild.name,
                'members': [m.nickname for m in guild.members]
            })
        response = jsonify(results)
        response.status_code = 200

        return response


@app.route('/guilds/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def guild_manipulation(id, **kwargs):
    # retrieve a guild using it's ID
    guild = Guild.query.filter_by(id=id).first()
    if not guild:
        # Raise an HTTPException with a 404 not found status code
        abort(404, 'Guild not found')

    if request.method == 'DELETE':
        data = request.get_json()
        guild.delete()
        response = jsonify({
            "message": "Guild {} deleted successfully".format(guild.id)
        })
        response.status_code = 200
        return response

    elif request.method == 'PUT':
        data = dict(request.get_json())

        # Get input data, filter and set
        if data.get('name', None) is not None:
            guild.name = data['name']
        if data.get('email', None) is not None:
            guild.email = data['email']
        guild.save()

        response = jsonify({
            'id': guild.id,
            'name': guild.name,
        })
        response.status_code = 200
        return response

    else:
        # GET
        response = jsonify({
            'id': guild.id,
            'name': guild.name
        })
        response.status_code = 200
        return response


@app.route('/items', methods=['POST', 'GET'])
def item():
    if request.method == 'POST':
        # Create a new item
        req_data = request.get_json()
        name = str(req_data.get('name', 'Untitled Item'))
        skill_points = str(req_data.get('skill_points', None))
        try:
            item = Item(name, skill_points)
            item.save()
            response = jsonify({
                "success": "true",
                "item": {
                    "id": item.id,
                    "name": item.name
                }
            })
            response.status_code = 201

            return response
        except Exception as e:
            response = jsonify({"message": str(e)})
            response.status_code = 500
            return response

    else:
        # GET
        items = Item.get_all()

        results = []

        for item in items:
            results.append({
                'id': item.id,
                'name': item.name,
                'skill_points': item.skill_points
            })
        response = jsonify(results)
        response.status_code = 200

        return response


@app.route('/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def item_manipulation(id, **kwargs):
    # retrieve a item using it's ID
    item = Item.query.filter_by(id=id).first()
    if not item:
        # Raise an HTTPException with a 404 not found status code
        abort(404, 'Item not found')

    if request.method == 'DELETE':
        item.delete()
        response = jsonify({
            "message": "Item {} deleted successfully".format(item.id)
        })
        response.status_code = 200
        return response

    elif request.method == 'PUT':
        data = dict(request.get_json())

        # Get input data, filter and set
        if data.get('name', None) is not None:
            item.name = data['name']
        if data.get('email', None) is not None:
            item.email = data['email']
        item.save()

        response = jsonify({
            'id': item.id,
            'name': item.name,
        })
        response.status_code = 200
        return response

    else:
        # GET
        response = jsonify({
            'id': item.id,
            'name': item.name
        })
        response.status_code = 200
        return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
