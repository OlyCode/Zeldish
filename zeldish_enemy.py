#!/usr/bin/env python
#
# Filename: zeldish_enemy.py
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
####    Enemy Class                                             ####
####################################################################
####################################################################

class EnemyClass(pygame.sprite.Sprite):
    rect = hitRect = hA = hD = vA = vD = 0
    autoList = []
    worldLoc = []
    roomLoc = []
    roomIndex = []
    roomView = []
    isVisible = False
    delMe = False
    startingCooldown = 50
    cooldown = 50
    eType = ""
    
    ############################################################
    ####   EnemyClass: Init                                 ####
    ############################################################
    def __init__(self, p_enemy_sprites, p_screen, p_type, \
                                    p_worldLoc, l_worldLoc):
        self.enemy_screen = p_screen
        self.enemy_sprites = p_enemy_sprites
        self.hitRectChange = (-8,-36)
        self.hitRectOffset = (0,18)

        pygame.sprite.Sprite.__init__(self)
        self.image = self.enemy_sprites[0][0]
        self.rect = self.image.get_rect()
        self.imageLoc = self.rect.topleft
        self.hitRect = self.rect.copy()
        self.hitRect.inflate_ip(self.hitRectChange[0],\
                                self.hitRectChange[1])
        self.hitRect.move_ip(self.hitRectOffset[0],\
                                self.hitRectOffset[1])
        
        self.facing = 0
        self.frame = 0
        self.frameCount = 0
        self.moveCount = 0
        self.hA = 0
        self.vA = 0
        self.hD = 0
        self.vD = 0
        self.autoList = []
        if p_type == 0:
            self.moveSpeed = 3
            self.eType = "girl"
        if p_type == 1:
            self.moveSpeed = 3
            self.eType = "skeleton"
        self.isVisible = False
        self.worldLoc = list(p_worldLoc)
        self.roomLoc = list(worldLocToRoomLoc(p_worldLoc))
        self.roomView = list(worldLocToRoomLoc(l_worldLoc))
        
        self.moveToWorldLoc(self.worldLoc)
        self.testVisible()
        self.linkWorldLoc = [0,0]
        self.pathCount = 0
        self.pathDirection = ""
        self.collision = False
        self.possibleMoves = []
        self.delMe = False
        startingCooldown = 50
        self.cooldown = 50
    
    ############################################################
    ####    EnemyClass: Events                              ####
    ############################################################
    def hStop(self):
        self.hA = 0
        self.hD = 0
    def vStop(self):
        self.vA = 0
        self.vD = 0
    def walkLeft(self):
        self.hA = self.moveSpeed
        self.hD = -self.hA
    def walkRight(self):
        self.hA = self.moveSpeed
        self.hD = self.hA
    def walkUp(self):
        self.vA = self.moveSpeed
        self.vD = -self.vA
    def walkDown(self):
        self.vA = self.moveSpeed
        self.vD = self.vA   

    ############################################################
    ####    enemyClass: Update                              ####
    ############################################################
    def staticMove(self, m):
        # This function moves enemy without changing his facing.
        # It moves both is sprite and his hit rectangle.
        # Moves relative to current position.
        # Works on rooms.
        self.rect.move_ip(int(m[0]),int(m[1]))
        self.hitRect.move_ip(int(m[0]),int(m[1]))

    def move(self, m):
        # This fucntion moves enemy, changes his facing, and
        # ticks the animation counter.
        # Moves relative to current position.
        # Works on rooms.
        if self.vD > 0 and self.hD == 0:
            self.facing = 2
        if self.vD < 0 and self.hD == 0:
            self.facing = 0
        if self.hD < 0 and self.vD == 0:
            self.facing = 3
        if self.hD > 0 and self.vD == 0:
            self.facing = 1
        self.frameCount += 1
        self.staticMove(m)

    def staticMoveToPixel(self, pLoc):
        # Moves to pixel location of the room.
        self.staticMove([pLoc[0]-self.hitRect.center[0],\
                                pLoc[1]-self.hitRect.center[1]])

    def moveToWorldLoc(self, wLoc):
        rIndex = worldLocToRoomIndex(wLoc)
        rLoc = worldLocToRoomLoc(wLoc)
        if self.isVisible == False:
            self.worldLoc = list(wLoc)
            self.roomLoc = list(rLoc)
            self.roomIndex = list(rIndex)
        if self.isVisible == True:
            self.autoList = []
            self.staticMove([rLoc[0]-self.hitRect.center[0]\
                                            +PIXELS_PER_TILE[0]/2,\
                            rLoc[1]-self.hitRect.center[1]\
                                            +PIXELS_PER_TILE[0]/2])
    
    def autoMove(self):                 #moves to a location
        epsilon = 5
        stopped = [False,False]
        if self.isVisible == False:
            return 0
        # horiontal movement
        if self.autoList == []:
            self.hStop()
            self.vStop()
            return 1
        x = self.autoList[0][0]
        y = self.autoList[0][1]
        if self.hitRect.center[0] > (x+epsilon):
            self.walkLeft()
        elif self.hitRect.center[0] < (x-epsilon):
            self.walkRight()
        else:
            self.hStop() 
            stopped[0] = True
        # vertical movement
        if self.hitRect.center[1] > (y+epsilon):
            self.walkUp()
        elif self.hitRect.center[1] < (y-epsilon):
            self.walkDown()
        else:
            self.vStop()
            stopped[1] = True
        if stopped[0] == stopped [1] == True:
            self.autoList.pop(0)
        return 0

    def simpleMove(self, m):        
        #this function has been nerfed: -1 <= x, y <= 1
        x = y = 0
        if m[0] >= 1: x = 1
        if m[0] <= -1: x = -1
        if m[1] >= 1: y = 1
        if m[1] <= -1: y = -1
        self.worldLoc = [(self.worldLoc[0]+x)%TILES_PER_WORLD[0],\
                        (self.worldLoc[1]+y)%TILES_PER_WORLD[1]]
        rLoc = worldLocToRoomLoc(self.worldLoc)
        if self.isVisible == False:
            return 0
        if self.isVisible == True:
            self.autoList.append([\
                    (rLoc[0])*PIXELS_PER_TILE[0]\
                                        + PIXELS_PER_TILE[0]/2,\
                    (rLoc[1])*PIXELS_PER_TILE[1]\
                                        + PIXELS_PER_TILE[1]/2])
        return

    def getTile(self, d, n):
        # This gets the tile ID of the tile that is n tiles
        # in front of the enemy.
        t = list(self.worldLoc)
        if d == 0: t[1] -= n
        if d == 1: t[0] += n
        if d == 2: t[1] += n
        if d == 3: t[0] -= n    
        else:
            if self.facing == 0: t[1] -= n
            if self.facing == 1: t[0] += n
            if self.facing == 2: t[1] += n
            if self.facing == 3: t[0] -= n
        return t

    def animationHandler(self, frame):
        # This function turns the animation to frame [x,y].
        self.image = self.enemy_sprites[frame[0]][frame[1]]
  
    def testVisible(self):
        isVisibleTemp = self.isVisible
        
        if self.roomIndex == self.roomView:
            if isVisibleTemp == False:
                self.isVisible = True
                t0 = worldLocToRoomLoc(self.worldLoc)
                t1 = roomLocToPixelLoc(t0)
                
                self.staticMove([t1[0]-self.hitRect.center[0]\
                                        +PIXELS_PER_TILE[0]/2,\
                                t1[1]-self.hitRect.center[1]\
                                        +PIXELS_PER_TILE[1]/2])
            return 0
        
        if self.roomIndex != self.roomView:
            if isVisibleTemp == True:
                self.isVisible = False
                if self.autoList != []:
                    self.worldLoc = list(roomLocToWorldLoc(\
                                self.roomIndex,\
                                pixelLocToRoomLoc(self.autoList[-1])))
                self.autoList = []
            return 0
                        
    def pathfinder(self):
        tMoves = []
        if self.worldLoc[0] > self.linkWorldLoc[0]:
            if [-1,0] in self.possibleMoves:
                tMoves.append([-1,0])
        if self.worldLoc[0] < self.linkWorldLoc[0]:
            if [1,0] in self.possibleMoves:
                tMoves.append([1,0])
        if self.worldLoc[1] > self.linkWorldLoc[1]:
            if [0,-1] in self.possibleMoves:
                tMoves.append([0,-1])
        if self.worldLoc[1] < self.linkWorldLoc[1]:
            if [0,1] in self.possibleMoves:
                tMoves.append([0,1])
        if tMoves == []:
            if self.possibleMoves != []:
                self.simpleMove(self.possibleMoves[\
                            random.randrange(len(self.possibleMoves))])
            return 0
        self.simpleMove(tMoves[random.randrange(len(tMoves))])
        return 0

    def update(self, p_roomView, p_linkLocation, p_possibleMoves):
        self.moveCount += 1
        self.roomIndex = list(worldLocToRoomIndex(self.worldLoc))
        self.roomView = list(p_roomView)
        self.linkWorldLoc = list(p_linkLocation)
        self.possibleMoves = list(p_possibleMoves)
        self.testVisible()
        if self.roomIndex == self.roomView: 
            self.isVisible = True
            if self.autoList == []: self.pathfinder()
            self.autoMove()
            self.animationHandler((self.facing, self.frame))
            if self.frameCount >= 15:
                self.frameCount = 0
                self.frame = (self.frame+1)%2
        else: 
            self.isVisible = False
            self.moveCount += 1
            if self.moveCount > 50: # this delays off screen movemnt
                self.pathfinder()
                self.autoMove()
                self.moveCount = 0
        
        if self.hD != 0 or self.vD != 0:
            self.move([int(self.hD), int(self.vD)])
        self.cooldown -= 1
        
    ############################################################
    ####    enemyClass: Draw                                ####
    ############################################################
    def draw(self):
        if self.isVisible == True:
            self.enemy_screen.blit(self.image, self.rect)
