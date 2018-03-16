import unittest
import os
import sys
import json

from gamehivechallengr.app import app, db, TestingConfig


class MyBaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """On inherited classes, run our `setUp` method"""
        # Inspired via http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class/17696807#17696807
        if cls is not MyBaseTestCase and cls.setUp is not MyBaseTestCase.setUp:
            orig_setUp = cls.setUp

            def setUpOverride(self, *args, **kwargs):
                MyBaseTestCase.setUp(self)
                return orig_setUp(self, *args, **kwargs)
            cls.setUp = setUpOverride

    def setUp(self):
        app.config.from_object(TestingConfig)
        self.app = app
        self.client = self.app.test_client()

        # Binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


class PlayerTestCase(MyBaseTestCase):

    def setUp(self):
        self.player = {'nickname': 'Jack', 'email': 'jack@example.com'}

    def test_simple(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

    def test_player_creation(self):
        """Test API can create a new player (POST request)"""
        res = self.client.post(
            '/players', data=json.dumps(self.player), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('success', str(res.data))

    def test_get_player_by_id(self):
        # first create a player
        res = self.client.post(
            '/players', data=json.dumps(self.player), content_type='application/json')
        self.assertEqual(res.status_code, 201)

        result_json = json.loads(res.data.decode('utf-8'))
        result = self.client.get(
            '/players/{}'.format(result_json['player']['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Jack', str(result.data))

    def test_update_player_info_by_id(self):
        # first create a player
        res = self.client.post(
            '/players', data=json.dumps(self.player), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        # update player
        rv = self.client.put('/players/1', data=json.dumps({
            'nickname': 'Albs',
            'email': 'albs@example.com'
        }), content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        results = self.client.get('/players/1')
        self.assertIn('Albs', str(results.data))

    def test_player_deletion(self):
        rv = self.client.post(
            '/players', data=json.dumps(self.player), content_type='application/json')
        self.assertEqual(rv.status_code, 201)
        self.assertIn('success', str(rv.data))
        res = self.client.delete('/players/1')
        self.assertEqual(res.status_code, 200)
        result = self.client.get('/players/1')
        self.assertEqual(result.status_code, 404)



class GuildTestCase(MyBaseTestCase):
    def setUp(self):
        players = [
            {'nickname': 'Jack', 'email': 'jack@example.com'}, 
            {'nickname': 'Mike', 'email': 'mike@example.com'}, 
            {'nickname': 'Alice', 'email': 'alice@example.com'}]
        self.players = players
        self.guild = {'name': 'Red', 'members': [{'id': 1}, {'id': 3}]}

    def test_guild_creation(self):
        # first create players
        responses = []
        for p in self.players:
            req = json.dumps(p)
            res = self.client.post('/players', data=req, content_type='application/json')
            responses.append(json.loads(res.data.decode('utf-8'))['player'])

        # create the guild
        req = json.dumps(self.guild)
        res = self.client.post('/guilds', data=req, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('Red', str(res.data))

    def test_guild_creation_single_member_failure(self):
        # first create players
        responses = []
        for p in self.players:
            req = json.dumps(p)
            res = self.client.post('/players', data=req, content_type='application/json')
            responses.append(json.loads(res.data.decode('utf-8'))['player'])

        # create the guild
        req = json.dumps({'name': 'Red', 'members': [{'id': 1}]})
        res = self.client.post('/guilds', data=req, content_type='application/json')
        self.assertEqual(res.status_code, 500)
        self.assertIn('lonely', str(res.data))

    def test_delete_player(self):
        # first create players
        responses = []
        for p in self.players:
            req = json.dumps(p)
            res = self.client.post('/players', data=req, content_type='application/json')
            responses.append(json.loads(res.data.decode('utf-8'))['player'])

        # create the guild
        req = json.dumps(self.guild)
        res = self.client.post('/guilds', data=req, content_type='application/json')

        res = self.client.delete('/guilds/1/members/3')


if __name__ == '__main__':
    unittest.main()
