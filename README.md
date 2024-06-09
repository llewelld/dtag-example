# Discrete Time Adversarial Game

Provides an example of the Discrete Time Adversarial Game framework.

## Overview

Includes executables and configuration files for the following:
1. Orchestrator client.
2. Visualise Server.
3. World Server.
4. Player Server.

The Orchestrator periodically contacts the World and Player servers with the current state of the game.
These servers return with updates states.
The Visualise server is then contacted with the state to render a visualisation of the game.

The example game is played on a grid.
Food randomly appears on the grid.
Players move around the grid randomly.
If they walk into some feed they will eat it.

Example view:
```
....................
.........*........*.
.......A.*..........
........**.........*
............**......
....A...*...........
.............*......
.....*.*..**........
........*....*...*..
....................
```

Key:
1. `.` - Empty space.
2. `*` - Food.
3. `A` - Player.

## Setup

Create a virtual environment and install the dependencies.

```
python3 -m ven venv
. ./venv/bin/activate
pip install pip --upgrade
pip install -r requirements.txt
```

There are no dependencies except Python and the base librarie. Tested using 3.10.12.

## Running the game

To run the game you need to start up the World Server, Visualise Server and two instances of the Player server.
Once these are running the Orchestrator Client can be started to begin the game.
Watch the console output of the Visualise Server to see how the game progresses.

Ideally each server should be started in a different shell so that the output for each can be seen separately.
Each server can be provided with a single parameter: the filename of the configuration file to use.

Start the Visualise Server:
```
$ python3 visualise.py visualise.json
```

Start the World Server:
```
$ python3 world.py world.json
```

Start the first Player Server:
```
$ python3 player.py player01.json
```

Start the second Player server:
```
$ python3 player.py player02.json
```

Finally, start the Orchestrator client:
```
$ python3 orchestrator.py orchestrator.json
```

## Configuration files

The Visualise, World and Player Servers all accept a JSON configuration file in the following form:
```
{
    "host": "<hostname>",
    "port": <port>
}
```

Servers which inhabit the same device must be run with different ports.

The Orchestrator Client accepts a JSON configuration file in the following form:
```
{
    "timestep": 1.0,
    "world": {
        "host": "<host>:<port>",
        "path": "/api/v1/world/update"
    },
    "visualise": {
        "host": "<host>:<port>",
        "path": "/api/v1/visualise/render"
    },
    "players": [
        {
            "player_id": <id>,
            "team_id": <id>,
            "host": "<host>:<port>",
            "path": "/api/v1/player/update"
        },
        ...
    ]
}
```

The timestep dictates the time the Orchestrator Client will wait between turns of the game, measured in seconds.

The other configuration values provide contact URLs for the Visualise, World and Player Servers.
These should match the values in the configuration files provided to the servers.

## Specification

See the [tournament.md](tournament.md) file for details of the communication protocol used.


