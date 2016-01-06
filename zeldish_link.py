#!/usr/bin/env python
#
# Filename: zeldish_link.py
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
####    Link Class                                              ####
####        This is the player object.                          ####
####################################################################
####################################################################

class LinkClass(pygame.sprite.Sprite):
    rect = hitRect = hA = hD = vA = vD = 0

    ############################################################
    ####   LinkClass: Init                                  ####
    ############################################################
    def __init__(self, p_link_sprites, p_screen):
        self.link_screen = p_screen
        self.link_sprites = p_link_sprites
        self.hitRectChange = (-8,-36)
        self.hitRectOffset = (0,18)

        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image = self.link_sprites[0][0]
        self.rect = self.image.get_rect()
        self.imageLoc = self.rect.topleft
        self.hitRect = self.rect.copy()
        self.hitRect.inflate_ip(self.hitRectChange[0],\
                                self.hitRectChange[1])
        self.hitRect.move_ip(self.hitRectOffset[0],\
                                self.hitRectOffset[1])
        
        self.staticMove([PIXELS_PER_ROOM[0]/2,PIXELS_PER_ROOM[1]/2])
 
        self.facing = 0
        self.frame = 0
        self.frameCount = 0

        self.hA = 0
        self.vA = 0
        self.hD = 0
        self.vD = 0
        self.moveSpeed = 5
        
        self.worldLoc = roomLocToWorldLoc([7,7],[5,5])
        self.roomLoc = [7,7]
        self.roomIndex = [7,7]
        self.roomView = [7,7]
        
    ############################################################
    ####    LinkClass: Events                               ####
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
    ####    LinkClass: Update                               ####
    ############################################################
    def staticMove(self, m):
        # This function moves link without changing his facing.
        # It moves both is sprite and his hit rectangle.
        self.rect.move_ip(int(m[0]),int(m[1]))
        self.hitRect.move_ip(int(m[0]),int(m[1]))

    def move(self, m):
        # This fucntion moves link, changes his facing, and
        # ticks the animation counter.
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

    def getTile(self, d, n):
        # This gets the tile ID of the tile that is n tiles
        # in front of link.
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
        self.image = self.link_sprites[frame[0]][frame[1]]
  
    def update(self):
        self.worldLoc = roomLocToWorldLoc(self.roomIndex,\
                pixelLocToRoomLoc(self.hitRect.center))     
        self.animationHandler((self.facing, self.frame))
        if self.frameCount >= 15:
            self.frameCount = 0
            self.frame += 1
            if self.frame == 2: self.frame = 0
        if self.hD != 0 or self.vD != 0:
            self.move([int(self.hD), int(self.vD)])
        
    ############################################################
    ####    LinkClass: Draw                                 ####
    ############################################################
    def draw(self):
        self.link_screen.blit(self.image, self.rect)

        # The next line can be used to see the hit rectangles.
        # It's useful for looking at collision detection
        #pygame.draw.rect(self.link_screen,(20,20,20),self.hitRect)
