#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 David Llewellyn-Jones

# DTAG example orchestrator
# Periodically contacts the World, Visualise and Player servers
# Sends stored states, requests and receives new states and stores them

import sys
import json
import time
from urllib.request import (urlopen, Request)

from src.library import (
    HostBase,
    StateBase,
    StatesBase,
)

class Config():
    """ Parse and store configuration values"""
    world = None
    visualise = None
    players = {}
    timestep = 1.0

    def __init__(self, filename):
        with open(filename) as file:
            config = json.load(file)
            self.timestep = config.get("timestep", 1.0)
            self.world = config.get("world", {})
            self.visualise = config.get("visualise", {})
            self.players = config.get("players", {})

class World(HostBase):
    pass

class Visualise(HostBase):
    pass

class Action(StateBase):
    pass

class Team(StateBase):
    pass

class Player(HostBase):
    player_id = 0
    team_id = 0

    def __init__(self, player_id, team_id, host, path):
        super().__init__(host, path)
        self.player_id = player_id
        self.team_id = team_id

class Actions(StatesBase):
    def __init__(self, identifiers):
        super().__init__(Action, identifiers)

class Teams2(StatesBase):
    def __init__(self, identifiers):
        super().__init__(Team, identifiers)

class Teams(StatesBase):
    def __init__(self, identifiers):
        super().__init__(Team, identifiers)

class Players(StatesBase):
    def __init__(self, state):
        super().__init__(Player, [])
        player_id_max = 0

        for player in state:
            # Ensure we get a unique player id
            player_id = player.get("player_id", player_id_max)
            if player_id in self.items:
                player_id = player_id_max
            if player_id >= player_id_max:
                player_id_max = player_id + 1
            # Read the team id
            team_id = player.get("team_id", 0)
            # Add a new player
            self.items[player_id] = Player(
                player_id,
                team_id,
                player.get("host", ""),
                player.get("path", ""),
            )

class Orchestrator():
    time = 0
    timestep = 1.0
    world = None
    visualise = None
    players = None
    teams = None
    actions = None

    def __init__(self, config):
        time = 0
        self.timestep = config.timestep
        data = config.world
        self.world = World(data.get("host", ""), data.get("path", ""))
        data = config.visualise
        self.visualise = Visualise(data.get("host", ""), data.get("path", ""))
        data = config.players
        self.players = Players(data)
        self.actions = Actions(self.players.items.keys())
        self.teams = Teams([player.team_id for player in self.players.items.values()])

    def sendToWorld(self):
        url = "{}{}".format(self.world.host, self.world.path)
        data = {
            "time": self.time,
            "world": self.world.json(),
            "actions": self.actions.json(),
        }
        reply = json.dumps(data, separators=(",",":")).encode("utf-8")
        print("World tx: {}".format(len(reply)))
        request = Request(url, headers={}, data=reply)
        with urlopen(request) as response:
            binary = response.read()
            data = json.loads(binary.decode("utf-8"))
            print("World rx {}".format(len(binary)))
            if "world" in data:
                self.world.set_state(data.get("world"))

    def sendToVisualise(self):
        url = "{}{}".format(self.visualise.host, self.visualise.path)
        data = {
            "time": self.time,
            "world": self.world.json(),
            "teams": self.teams.json(),
            "players": self.players.json(),
        }
        reply = json.dumps(data, separators=(",",":")).encode("utf-8")
        print("Visualise tx: {}".format(len(reply)))
        request = Request(url, headers={}, data=reply)
        with urlopen(request) as response:
            binary = response.read()
            data = json.loads(binary.decode("utf-8"))
            print("Visualise rx {}".format(len(binary)))

    def sendToPlayers(self):
        for player_id in self.players.items.keys():
            player = self.players.items[player_id]
            team_id = player.team_id
            action = self.actions.items[player_id]
            team = self.teams.items[team_id]
            url = "{}{}".format(player.host, player.path)
            data = {
                "time": self.time,
                "world": self.world.json(),
                "team": team.json(),
                "player": player.json(),
            }
            reply = json.dumps(data, separators=(",",":")).encode("utf-8")
            print("Player tx {}: {}".format(player_id, len(reply)))
            request = Request(url, headers={}, data=reply)
            with urlopen(request) as response:
                binary = response.read()
                data = json.loads(binary.decode("utf-8"))
                print("Player rx {}: {}".format(player_id, len(binary)))
                if "player" in data:
                    player.set_state(data.get("player"))
                    self.players.items[player_id] = player
                if "action" in data:
                    action.set_state(data.get("action"))
                    self.actions.items[player_id] = action
                if "team" in data:
                    team.set_state(data.get("team"))
                    self.actions.items[team_id] = action

    def poll(self):
        print("Poll: {}".format(self.time))
        self.sendToWorld()
        self.sendToVisualise()
        self.sendToPlayers()
        self.time += 1
        print()

def run_client():
    config_file = "orchestrator.json"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    config = Config(config_file)

    orchestrator = Orchestrator(config)
    print("DTAG Orchestrator running")

    while True:
        start_time = time.monotonic()
        orchestrator.poll();
        end_time = time.monotonic()
        remaining = orchestrator.timestep - (end_time - start_time)
        if remaining > 0.0:
            time.sleep(remaining)

    print("Game Over")

if __name__ == "__main__":
    run_client()

