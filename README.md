Player API
==========

Background
----------

In this exercise, you will create a simple REST API. We think that it can all be completed in an evening, but we appreciate that you may have other commitments and time constraints. Please let us know (roughly) when we should expect your answers (e.g. "over the weekend"), and whether or not you need more time.

You have been supplied with the skeleton of a Python web application. The stack is as follows:

- Operating system: Debian 9 ("Stretch")
- Python release: 3.6
- Application framework: Flask
- Database: PostgreSQL 9.6
- Object-relational mapper: SQLAlchemy

The purpose of the API is to manage the players, guilds and items of some game.


### Players

Players are identified by a unique ID, and provide a nickname and an email address when they sign up. They have a specific number of skill points, and they may possess zero or more items.

### Guilds

A guild consists of a team of two or more players. All guilds have a unique ID and a name, and  optionally a country code.

### Items

Items are special bonuses which the player encounters as they progress through the game, which can increase the player's skill points by a certain amount. If the player is not in a guild when they pick up an item, it simply increases their skill points.

However, a special rule applies if a player is in a guild when they pick up an item: if anyone else in the guild has the same item, the skill points of the players with that item are decreased by the same amount first.


## Endpoints

The API needs endpoints with the following functionality:

1. create, update and delete a player
2. create, update and delete a guild
3. create, update and delete an item
4. add a player to a guild
5. remove a player from a guild
6. add an item to a player
7. calculate the total number of skill points in a guild

The endpoints should accept JSON objects as the request body. For example, a `POST` to the endpoint to add a player to a guild might look like

```
{
    "player_id": <UUID>,
    "guild_id": <UUID>
}
```

Note that in some cases it may be appropriate for a single endpoint to handle multiple REST verbs (e.g. both a `POST` and a `PUT`).

Your endpoints should handle errors and return HTTP status codes appropriately. If a request is successfully processed (i.e. results in a 2XX status), the server should respond with the following message:

```
{
    "success": "true"
}
```

If the request is not successful, the endpoint should return an appropriate HTTP status code and error message.

## Tasks

1. Create declarative SQLAlchemy model definitions which capture all of the information required for guilds, players and items, as well as the relationships between them.
2. Use the model definitions to set up the database schema for the player, guild and item tables, with associated primary keys, indexes and foreign key relationships.
3. Implement as many of the endpoints as you can.
4. Write tests for your application using `pytest`.

Write your code as if you were shipping it to production. It should be simple, idiomatic Python 3 which is easy to read. At Game Hive we don't allow code to be merged if it doesn't have tests covering it, so those are expected too.

Use comments to explain your code, and the design decisions you made. 

Getting started
---------------

The stack has been assembled as a set of Docker containers using `docker-compose`. The network is defined in `docker-compose.yml`, while the app server's image is defined in `Dockerfile`. 

To build the application and run it, install Docker and docker-compose on your computer, then run the following at a command prompt, in the current directory:

```
$ docker-compose up
```

This will take a few minutes as docker needs to download the images for Debian, PostgreSQL and so on that the containers are based on. Once all images are built the system will be available on localhost, port 5000 (which you can access through a web browser, postman etc.). Flask will automatically reload the server as you make changes to the code.

The entrypoint of the appserver image is also set up so that you can run arbitrary commands by supplying them on the command line. For example, to run an interactive Python shell, you would run

```
$ docker-compose run -p 5000:5000 appserver python
``` 

To get a shell inside the container, you would run


```
$ docker-compose run -p 5000:5000 appserver bash
```

### Libraries

You can install any additional libraries, packages, etc. that you see fit. To install system packages, add the appropriate `apt-get` command to the `Dockerfile` and rebuild. To install Python packages, append them to the `requirements.txt` file and rebuild.


You can rebuild by running 

```
$ docker-compose build
```

In some cases, you may need to supply the `--no-cache` flag to `docker-compose build` to force cached steps in the build to be regenerated.

### Configuration

The configuration for the application can be changed by editing the `Config` object in `app.py`.

### Database

The database is available inside the appserver container at the address `postgres:5432`. The username and password are `gamehive` and `gamehive`.

When you start the application for the first time, you will need to populate the database with the schema defined in your application. To do this, first find the name of the running app server container using `docker ps`:

```
$ docker ps
CONTAINER ID        IMAGE                COMMAND                  CREATED             STATUS              PORTS                    NAMES
0004849e6554        gamehive_appserver   "/docker-entrypoint...."   18 seconds ago      Up 22 seconds       0.0.0.0:5000->5000/tcp   gamehive_appserver_1
b1f97b5ad60f        postgres:9.6         "docker-entrypoint.s..."   19 seconds ago      Up 23 seconds       5432/tcp                 gamehive_postgres_1
```

We see here that the container is running as `gamehive_appserver_1`. We can now open a Python shell inside this container, and populate the schema as follows:
```
$ docker exec -ti gamehive_appserver_1 python
Python 3.6.4 (default, Dec 21 2017, 01:29:34)
[GCC 6.3.0 20170516] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from app import db
>>> db.create_all()
```

#### PostgresSQL shell

You can get a shell on the database server by running `psql` inside the postgres container, supplying the username and password on the command line:

```
$ docker exec -ti gamehive_postgres_1 psql gamehive gamehive
psql (9.6.6)
Type "help" for help.

gamehive=#
```