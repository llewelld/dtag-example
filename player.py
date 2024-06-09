#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 David Llewellyn-Jones

# DTAG example player
# Receives world, team and player state
# Returns updated player and team states

from json import dumps
from random import randrange

from src.library import (
    ClientConfig,
    WorldBase,
    PlayerBase,
    ActionBase,
    ServerBase,
    run_server,
)

class Config(ClientConfig):
    """ Parse and store configuration values"""
    name = ""
    team = ""

    def setup(self, config):
        self.name = config.get("name", "anonymous")
        self.team = config.get("team", "individual")

class Reply():
    """Storing and serialise replies"""
    player = None
    action = None

    def __init__(self, player, action):
        self.player = player
        self.action = action

    def json(self):
        return {
            "player": self.player.json(),
            "action": self.action.json()
        }

class World(WorldBase):
    """Store the world state"""
    pass

class Player(PlayerBase):
    """Store and upated the player state"""
    def moveRandom(self, world):
        # 0 = up; 1 = right; 2 = down; 3 = left
        direction = randrange(4)
        if direction == 0:
            self.y = (self.y + 1 ) % world.height
        elif direction == 1:
            self.x = (self.x + 1 ) % world.width
        elif direction == 2:
            self.y = (self.y - 1 ) % world.height
        elif direction == 3:
            self.x = (self.x - 1 ) % world.width

class Team():
    """Store and update the team state"""
    def __init__(self, data):
        pass

class Action(ActionBase):
    """Store the update the player action state"""
    def __init__(self, x, y, action):
        super().__init__({"x": x, "y": y, "action": action})

class Server(ServerBase):
    """"Specialised server code for responding to player updates """
    name = "A"

    def pre_init(self):
        self.title = "Player"
        self.update_path = "/api/v1/player/update"

    def update(self, player, world):
        player.moveRandom(world)
        cell = world.get_cell(player.x, player.y)
        act = "move"
        if cell == "*":
            act = "eat"
        action = Action(player.x, player.y, act)
        return Reply(player, action)

    def receive(self, data):
        time = int(data.get("time", "0"))
        world = World(data.get("world", "{}"))
        #team = json.loads(data.get("team", "{}"))
        player = Player(data.get("player", "{}"))

        update = self.update(player, world)
        reply = dumps(update.json(), separators=(",",":"))

        world.display(player.x, player.y, self.name)

        return reply

if __name__ == "__main__":
    run_server("player.json", Config, Server)

