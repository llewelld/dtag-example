#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 David Llewellyn-Jones

# DTAG example library files
# Base classes used by multiple of the example executables

import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class ClientConfig():
    """ Client base class for parsing and storing configuration values"""
    host = "localhost"
    port = 8080

    def __init__(self, filename):
        with open(filename) as file:
            config = json.load(file)
            self.host = config.get("host", "localhost")
            self.port = config.get("port", 8000)
            self.setup(config)

    def setup(self, config):
        pass

class WorldBase():
    """Base class for storing the World status"""
    height = 0
    width = 0
    cells = []

    def __init__(self, state):
        self.height = state.get("y", 0)
        self.width = state.get("x", 0)
        self.cells = state.get("cells", [])

    def get_cell(self, xpos, ypos):
        xpos = xpos % self.width
        ypos = ypos % self.height
        cell = self.cells[ypos][xpos]
        return cell

    def set_cell(self, xpos, ypos, value):
        row = self.cells[ypos]
        row = row[:xpos] + value + row[xpos + 1:]
        self.cells[ypos] = row

    def display(self, xpos, ypos, name):
        for y in range(self.height):
            row = self.cells[y]
            if y == ypos:
                row = row[:xpos] + name + row[xpos + 1:]
            print(row)

    def json(self):
        return {
            "x": self.width,
            "y": self.height,
            "cells": [row for row in self.cells]
        }

class PlayerBase():
    """Base class for storing the Player status"""
    x = 0
    y = 0

    def __init__(self, state):
        self.x = state.get("x", 0)
        self.y = state.get("y", 0)

    def json(self):
        return {
            "x": self.x,
            "y": self.y
        }

class ActionBase():
    """Base class for storing the Action status"""
    x = 0
    y = 0
    action = "none"

    def __init__(self, state):
        self.x = state.get("x", 0)
        self.y = state.get("y", 0)
        self.action = state.get("action", "none")

    def json(self):
        return {
            "x": self.x,
            "y": self.y,
            "action": self.action
        }

class TeamBase():
    """Base class for storing the Team status"""
    def __init__(self, state):
        pass

    def json(self):
        return {
        }

class Multiple():
    """Base class for storing dictionaries of status objects indexed by id"""
    items = {}

    def __init__(self, Type, state):
        self.items.clear()
        for item_id, item in state.items():
            self.items[item_id] = Type(item)

    def json(self):
        data = {}
        for item_id, item in self.items.items():
            data[item_id] = item.json()
        return data

class HostBase():
    """Base class for storing details about a hosted service"""
    host = ""
    path = ""
    state = {}

    def __init__(self, host, path):
        self.host = host
        self.path = path

    def set_state(self, state):
        self.state = state

    def json(self):
        return self.state

class StateBase():
    """Base class for storing states"""
    state = {}

    def __init__(self):
        pass

    def set_state(self, state):
        self.state = state

    def json(self):
        return self.state

class StatesBase():
    """Base class for storing multiple states indexed by id"""
    items = {}

    def __init__(self, Type, identifiers):
        self.items = {}
        for identifier in identifiers:
            self.items[identifier] = Type()

    def json(self):
        data = {}
        for state_id, state in self.items.items():
            data[state_id] = state.json()
        return data

class ServerBase(BaseHTTPRequestHandler):
    """Base class for responding to HTTP requests"""
    title = "Server"
    update_path = "/api/v1/server/update"

    def __init__(self, request, client_address, server):
        self.pre_init()
        super().__init__(request, client_address, server)

    def pre_init(self):
        pass

    def receive(self, data):
        return ""

    def do_POST(self):
        print(self.update_path)
        if self.path == self.update_path:
            length = int(self.headers.get('content-length'))
            data = json.loads(self.rfile.read(length).decode('utf8'))

            reply = self.receive(data)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(bytes(reply, "utf-8"))

    def do_GET(self):
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html>\n", "utf-8"))
        self.wfile.write(bytes("  <head>\n", "utf-8"))
        self.wfile.write(bytes("    <title>{}</title>\n".format(self.title), "utf-8"))
        self.wfile.write(bytes("  </head>\n", "utf-8"))
        self.wfile.write(bytes("  <body>\n", "utf-8"))
        self.wfile.write(bytes("    <p>404: Not found</p>\n", "utf-8"))
        self.wfile.write(bytes("    <p>Try POSTing to <a href=\"{}\">/api/v1/player/update</a>\n".format(self.update_path), "utf-8"))
        self.wfile.write(bytes("  </body>\n", "utf-8"))
        self.wfile.write(bytes("</html>\n", "utf-8"))

def run_server(default_config, Config, Server):
    """Method for running the server, used for starting a listening server"""
    config_file = default_config
    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    config = Config(config_file)

    server = HTTPServer((config.host, config.port), Server)
    print("DTAG Server: http://%s:%s" % (config.host, config.port))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    print("Game Over")

