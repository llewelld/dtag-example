# Discrete Time Adversarial Game Server

## Overview

The system is split into an Orchestration server, a world server and multiple player servers. All interactions between servers are performed through a set of HTTP REST interfaces.

Players can be grouped into teams. All of the state is maintained by the orchestration server. The world server and player server are only concerned with behaviour, that is, how to update world and player states based on the data provided to them by the orchestration server.

The orchestration server maintains four types of state:

World state (one per game)
Team states (one per team)
Player states (one per player)
Action states (one per player)

The orchestration server doesn't concern itself with what these states are or mean, they can just be JSON blobs as far as it's concerned.

These stats are essentially "shared memory" with the following access restrictions:

World state: world server read/write; player server read.
Team state: players on a team read/write
Player state: player read/write
Action state: world read; player write

These access restrictions aren't for protecting against cheating, they're given here for delineating roles and to help direct the API design.

At each game step the orchestration server goes through the following steps:

1. Cycle through each of the player states. Call the player server for each state. Overwrite the player state and action state with the data returned.
2. Call the world sever with the world state and actions. Overwrite the world state with the data returned.

When the player server update function is called, it receives the states, runs its behaviour code on this and returns the result. It doesn't need to store anything.

When the world server update function is called, it receives the states, runs its behaviour code on this and returns the result. It doesn't need to store anything.

There may also be a need to visualise the result. To avoid the orchestration server having to understand the contents of the states, we might also want a "Visualisation Server" that's given the states and returns back an image to be displayed.

## Orchestration server

The orchestration server consumes the interfaces of the player servers and the world server, it doesn't need to have an API of its own. Nevertheless query methods like these could be included for debugging, etc.

The orchestration server manages all of the state. The world server and player servers can be stateless (e.g. cloud-based Lambda functions).

```
GET /api/v1/orchestrator/player/state
```

Query parameters:
3. player_id (number)

Response:
```json
{
    "player_id": (int),
    "team_id": (int),
    "state": (json)
}
```

The JSON player state is game-specific, but here's an example:

```json
{
    "color": "red",
    "state": 5,
    "resting": 7,
    "direction": 2,
    "has_food": true
}
```

```
GET /api/v1/orchestrator/action/state
```

Query parameters:
3. player_id (number)

Response:
```json
{
    "player_id": (int),
    "state": (json)
}
```

```
GET /api/v1/orchestrator/team/state
```

Query parameters:
1. team_id (number)

Response:
```json
{
    "team_id": (int),
    "state": (json)
}
```

The JSON team state is game-specific, but here's an example:

```json
{
    "alive": 5
}
```

```
GET /api/v1/orchestrator/world/state
```

Query parameters:
None

Response:
```json
{
    "state": (json)
}
```

The JSON world state is game-specific, but here's an example:

```json
{
    "x": 10,
    "y": 10,
    "cells": [
        "##########",
        "#99....33#",
        "#9#.-----#",
        "#.#------#",
        "#..5-----#",
        "#+++++5..#",
        "#++++++#.#",
        "#+++++.#9#",
        "#33....99#",
        "##########"
    ]
}
```

## World server

The world server doesn't hold any state. It updates the world state based on the actions of the players.

At each step the world server is queried, given the world state and player actions, and returns an updated world state.

```
POST /api/v1/world/update
```

Request data
```json
{
    "time": (int),
    "world": (json)
    "actions": {
        1: (json),
        2: (json),
        ...
    }
}
```

Response:
```json
{
    "world": (json)
}
```

Example POST:
```
curl --request POST --data \
'{"time":1,"world":{"x":10,"y":10,"cells":["..........","..........",'\
'"..........","..........","..........","..........","..........",'\
'"..........","..........",".........."]},"actions":{"0":{"x":5,"y":5,'\
'"action":"move"},"1":{"x":1,"y":2,"action":"move"},"2":{"x":2,"y":7,'\
'"action":"eat"}}}' \
'http://localhost:8001/api/v1/world/update'
```

## Player server

The player server doesn't hold any state apart from the behavioural code for a player. It receives the world state, team state and player state from the server, runs its behaviour code and returns with an updated player state, team state and an action.

The world state isn't updated, instead the action is passed to the world server so that it can update the world state.

```
POST /api/v1/player/update
```

Request parameters:
```json
{
    "time": (int),
    "world": (json)
    "team_id": (int),
    "player_id": (int),
    "team": (json)
    "player": (json)
}
```

Response:
```json
{
    "team_id": (int),
    "player_id": (int),
    "team": (json)
    "player": (json)
    "action": (json)
}
```

Example POST:
```
curl --request POST --data \
'{"time":1,"player_id":1,"team_id":1,"world":{"x":10,"y":10,"cells":'\
'["..........","..........","..........","..........","..........",'\
'"..........","..........","..........","..........",".........."]},'\
'"team":{},"player":{"x":5,"y":5}}' \
'http://localhost:8002/api/v1/player/update'
```

## Visualise server

The visualise server is used only to visualise the game. It's sent the status of the world and players but doesn't return anything. It can choose how to render the results (e.g. it might provide another path to view the results using a browser).

```
POST /api/v1/visualise/render
```

Query parameters
```json
{
    "time": (int),
    "world": (json)
    "teams": {
        1: (json)
        2: (json)
        ...
    }
    "players": {
        1: (json)
        2: (json)
        ...
    }
}
```

Response:
```json
{
}
```

Example POST:
```
curl --request POST --data \
'{"time":1,"world":{"x":10,"y":10,"cells":["..........","..........",'\
'"..........","..........","..........","..........","..........",'\
'"..........","..........",".........."]},"players":{"0":{"x":5,"y":5},'\
'"1":{"x":1,"y":2},"2":{"x":2,"y":7}},"teams":{}}' \
'http://localhost:8000/api/v1/visualise/render'
```


