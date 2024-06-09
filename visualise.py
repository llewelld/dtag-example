#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 David Llewellyn-Jones

# DTAG example visualise
# Receives world, team and player states
# Renders them for visualisation

from json import dumps

from src.library import (
    ClientConfig,
    PlayerBase,
    TeamBase,
    WorldBase,
    Multiple,
    ServerBase,
    run_server,
)

class Config(ClientConfig):
    """ Parse and store configuration values"""
    def setup(self, config):
        pass

class Reply():
    """Storing and serialise replies"""
    def __init__(self):
        pass

    def json(self):
        return {
        }

class World(WorldBase):
    """Store and display the world state"""
    def display(self, players):
        cells = self.cells[:]
        for player in players.items.values():
            row = cells[player.y]
            row = row[:player.x] + "A" + row[player.x + 1:]
            cells[player.y] = row

        for y in range(self.height):
            row = cells[y]
            print(row)

class Player(PlayerBase):
    """Store the player state"""
    pass

class Team(TeamBase):
    """Store the team state"""
    pass

class Server(ServerBase):
    """"Specialised server code for responding to render requests"""
    def pre_init(self):
        self.title = "Visualise"
        self.update_path = "/api/v1/visualise/render"

    def receive(self, data):
        time = int(data.get("time", "0"))
        world = World(data.get("world", "{}"))
        teams = Multiple(Team, data.get("teams", "[]"))
        players = Multiple(Player, data.get("players", "[]"))

        update = Reply()
        reply = dumps(update.json(), separators=(",",":"))

        world.display(players)

        return reply

if __name__ == "__main__":
    run_server("visualise.json", Config, Server)

