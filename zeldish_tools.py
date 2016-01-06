#!/usr/bin/env python
#
# Filename: zeldish_tools.py
# Used by: zeldish.py
# Copyrigth 2015 Olympia Code
# Author: Joe Mortillaro
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

__metaclass__ = type

# This part imports standard python libraries.
import random
import copy
import time
import sys
import pygame

####################################################################
####    global variavles                                        ####
####        These variables are used by many functions          ####
####        and it is just easier to make them global           ####
####        variables then it is to pass the values into        ####
####        the functions.                                      ####
####################################################################
PIXELS_PER_TILE = (32, 32)
TILES_PER_ROOM = (16, 11)
PIXELS_PER_ROOM = (512, 352)
ROOMS_PER_WORLD = (16, 8)
SPRITE_SIZE = (28,50)
TILES_PER_WORLD = (256, 88)
PIXELS_PER_WORLD = (256*32, 88*32)


# the strings in the walklist are the types of tiles
# that it will let a sprite walk on.
walkList = ["02","06","0c","0e","14","18","1a","20","24",\
            "40","4c","53","54","55","59","5a","5b","5f",\
            "60","61","67","68","69","6d","6e","6f","73",\
            "74","75","7b","7c","7d","81","82","83","87",\
            "88","89","8c","8d","8e","8f","91","92","93",\
            "94","95","97","98","99","9a","9b","9d",\
            "a1","a2","a4","a5"]

orbList = ["a1","a2","a4","a5"]

# Notes:
# world > rooms > tiles > pixels
# world is 16 x 8 rooms, 256 x 88 tiles, 4096 x 1408 pixels
# rooms are 16 x 11 tiles, 256 x 176 pixels
# (but only the top half of the bottom row of tiles is shown on screen)
# tiles are 16 x 16 pixels
# World map colors:
# ['(32, 56, 236, 255)',   # blue
#  '(252, 252, 252, 255)',   # white
#  '(200, 76, 12, 255)',   # brown
#  '(0, 168, 0, 255)',      # green
#  '(116, 116, 116,116 255)',   # gray
#  '(252, 216, 168, 255)',   # tan
#  '(0, 0, 0, 255)']    # black
                                                                
def pixelLocToRoomLoc(pLoc):
    return [pLoc[0]/PIXELS_PER_TILE[0],\
            pLoc[1]/PIXELS_PER_TILE[1]]

def roomLocToPixelLoc(rLoc):
    return [rLoc[0]*PIXELS_PER_TILE[0],\
            rLoc[1]*PIXELS_PER_TILE[1]]

def roomLocToWorldLoc(rView, rLoc):
    return [rView[0]*TILES_PER_ROOM[0]+rLoc[0],\
            rView[1]*TILES_PER_ROOM[1]+rLoc[1]]

def worldLocToRoomLoc(wLoc):
    return [wLoc[0]%TILES_PER_ROOM[0],\
            wLoc[1]%TILES_PER_ROOM[1]]

def worldLocToRoomIndex(wLoc):
    return [wLoc[0]/TILES_PER_ROOM[0],\
            wLoc[1]/TILES_PER_ROOM[1]]
