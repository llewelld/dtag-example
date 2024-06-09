#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 David Llewellyn-Jones

# DTAG example world
# Receives world state and actions
# Returns an updated world state

from json import dumps
from random import randrange

from src.library import (
    ClientConfig,
    WorldBase,
    ActionBase,
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
    world = None

    def __init__(self, world):
        self.world = world

    def json(self):
        return {
            "world": self.world.json(),
        }

class World(WorldBase):
    "Store and update the world state"
    def __init__(self, state):
        super().__init__(state)
        if self.width == 0 and self.height == 0:
            self.start()

    def start(self):
        self.height = 10
        self.width = 20
        for y in range(self.height):
            row = "." * self.width
            self.cells.append(row)

    def grow(self):
        prob = randrange(5)
        if prob == 0:
            x = randrange(self.width)
            y = randrange(self.height)
            self.set_cell(x, y, "*")

    def display(self, actions):
        cells = self.cells[:]
        for action in actions.items.values():
            row = cells[action.y]
            row = row[:action.x] + "A" + row[action.x + 1:]
            cells[action.y] = row

        for y in range(self.height):
            row = cells[y]
            print(row)

    def act(self, action):
        if action.action == "eat":
            self.set_cell(action.x, action.y, ".")

class Action(ActionBase):
    """Store player actoin states"""
    pass

class Server(ServerBase):
    """"Specialised server code for responding to world updates"""
    def pre_init(self):
        self.title = "World"
        self.update_path = "/api/v1/world/update"

    def update(self, world, actions):
        world.grow()
        for action in actions.items.values():
            world.act(action)
        return Reply(world)

    def receive(self, data):
        time = int(data.get("time", "0"))
        world = World(data.get("world", "{}"))
        actions = Multiple(Action, data.get("actions", "[]"))

        update = self.update(world, actions)
        reply = dumps(update.json(), separators=(",",":"))

        world.display(actions)

        return reply

if __name__ == "__main__":
    run_server("world.json", Config, Server)

