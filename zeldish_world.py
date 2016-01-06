#!/usr/bin/env python
#
# Filename: zeldish_world.py
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
import random
import copy
import time
import sys
import pygame
from zeldish_tools import *

####################################################################
####################################################################
####    WorldClass                                              ####
####################################################################
####################################################################

class WorldClass():
    worldData = []      # 2d array of strings
    roomData = []       # 2d array of strings
    roomView = [7,7]    # [x,y] value of current room
    
    orbPoints = []
        
    image = pygame.Surface(PIXELS_PER_ROOM)
    world_sprites = 0
    room = []

    ############################################################
    ####   GameClass: Init                                  ####
    ############################################################
    def __init__(self, p_world_sprites, p_screen):
        self.world_screen = p_screen
        
        #### Reads and Processes Map Data
        self.world_sprites = p_world_sprites
        worldTemp = ""
        try:
            f = open("zeldish_map.dat",'r')
        except IOError:
            print "ERROR -- zeldish_map.dat -- FILE DOES NOT EXIST"
            sys.exit(0)
        worldTemp = f.read()
        f.close()
        worldTemp = worldTemp.split('\n')
        for x in range(len(worldTemp)):
            worldTemp[x] = worldTemp[x].split(' ')
        x = 0
        while x < len(worldTemp):
            if len(worldTemp[x]) != TILES_PER_WORLD[0]:
                worldTemp.pop(x)
                x -= 1
            x += 1
        self.worldData = worldTemp
        
        orbPoints = []
        for x in range(7):
            self.orbPoints.append(\
                [random.randrange(ROOMS_PER_WORLD[0])*TILES_PER_ROOM[0]\
                                                   + TILES_PER_ROOM[0]/2,\
                random.randrange(ROOMS_PER_WORLD[1])*TILES_PER_ROOM[1]\
                                                   + TILES_PER_ROOM[1]/2 +2])
        
        for x in range(len(self.orbPoints)):
            t = self.orbPoints[x]
            self.changeTerrain([t[0],t[1]], "a1")
            self.changeTerrain([t[0]+1,t[1]], "a2")
            self.changeTerrain([t[0],t[1]+1], "a4")
            self.changeTerrain([t[0]+1,t[1]+1], "a5")
        
        self.render()
        
    def setRoomData(self):
        self.roomData = []
        t = [self.roomView[0]%ROOMS_PER_WORLD[0],\
                self.roomView[1]%ROOMS_PER_WORLD[1]]
        offset = [t[0]*TILES_PER_ROOM[0], t[1]*TILES_PER_ROOM[1]]
        for y in range(TILES_PER_ROOM[1]):
            self.roomData.append(self.worldData[offset[1]+y]\
                        [offset[0]:offset[0]+TILES_PER_ROOM[0]])
    
    #############################################################
    ####   WorldClass:  events   ################################
    #############################################################
    def getTileType(self, worldLoc):
        # This gets the tile ID of the location.
        # The location is [x,y]
        t = [worldLoc[0]%TILES_PER_WORLD[0],\
                worldLoc[1]%TILES_PER_WORLD[1]]
        return self.worldData[t[1]][t[0]]
    
    def getTileTypeByPixel(self, pixelLoc):
        # This gets the tile ID of the location.
        # The location is [x,y] pixel data
        t0 = pixelLocToRoomLoc(pixelLoc)
        t = roomLocToWorldLoc(self.roomView, t0)
        return self.getTileType(t)
                
    def getTileTypeByRoom(self, roomLoc):
        # This gets the tile ID of the location.
        # The location is [x,y]
        t = roomLoc
        return self.roomData[t[1]][t[0]]

    def render(self):
        xSize = 20
        
        self.setRoomData()
        for y in range(TILES_PER_ROOM[1]):
            for x in range(TILES_PER_ROOM[0]):
                temp = int("0x" + self.roomData[y][x],16)
                yVal = temp/xSize
                xVal = temp - yVal*xSize
                self.image.blit(self.world_sprites[yVal][xVal],\
                            (x*PIXELS_PER_TILE[0],\
                            y*PIXELS_PER_TILE[1]))

    def changeTerrain(self, wLoc, n):
        # loc = (x,y), n = tile id = "02" for example.
        # This function can be used to change tiles in a room.
        # It works as the game is running.
        t = [wLoc[0]%TILES_PER_WORLD[0],\
                wLoc[1]%TILES_PER_WORLD[1]]
        self.worldData[t[1]][t[0]] = n
        self.render()

    def changeRoom(self, loc):
        # This function changes the current screen.
        self.roomView = loc
        self.render()

    #############################################################
    ####   WordClass:  update   #################################
    #############################################################
    def animationHandler(self, frame):
        # Any animation we want to happen in the world goes here.
        pass
  
    def update(self):
        # Anything that needs to get updated once per frame goes here.
        #self.pathfinder(50)
        pass
        
    #############################################################
    ####   WorldClass:  draw   ##################################
    #############################################################
    def draw(self):
        self.world_screen.blit(self.image, (0,0))
