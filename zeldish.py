#!/usr/bin/env python
#
# Filename: zelish.py
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
import json
import sys
import pygame

import zeldish_link
import zeldish_world
import zeldish_enemy
from zeldish_tools import *

#####################################################################
####   zeldish settings                                         #####
#####################################################################

zeldish_settings = {"scale":2, "max_monsters": 200}
fname = "zeldish_settings.json"
try:
    f = open(str(fname),"r")
    zeldish_settings = json.loads(f.read())
    f.close
except IOError:
    f = open(str(fname),"w")
    f.write(json.dumps(zeldish_settings))
    f.close()   

#####################################################################
####   pygame setup                                             #####
#####################################################################

GAME_SCALE = zeldish_settings["scale"]
GAME_SCREEN_SIZE = (512,352)
UI_SIZE = [512,50]
SCREEN_OFFSET = [10,10]

SMALL_SCREEN_SIZE = \
            [GAME_SCREEN_SIZE[0]+2*SCREEN_OFFSET[0],\
            GAME_SCREEN_SIZE[1]+UI_SIZE[1]+2*SCREEN_OFFSET[1]]
SCREEN_SIZE = [SMALL_SCREEN_SIZE[0]*GAME_SCALE,\
                            SMALL_SCREEN_SIZE[1]*GAME_SCALE]
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
gameScreen = pygame.Surface(GAME_SCREEN_SIZE)
smallScreen = pygame.Surface(SMALL_SCREEN_SIZE)
uiScreen = pygame.Surface(UI_SIZE)
pygame.display.set_caption("Zeldish")



####################################################################
####    pygame joystick setup                                   ####
####################################################################
pygame_joystick = False
if pygame.joystick.get_count() >= 1:
    controller = pygame.joystick.Joystick(0)
    controller.init()
    pygame_joystick = True
    
####################################################################
####   pygame functons                                          ####
####################################################################
def processSpritesheet(p_sheetName, p_spriteSize, p_border):
    # slices up a spritesheet, returns a 2d array of sprites.
    # p_sheetName = the sprite sheet to slice up
    # p_spriteSize = the size sprites to cut the sheet into
    # p_boarder = the size of the boarder around each tile
    # note: sizes are in the form (x_size, y_size)
    returnList = []
    offset = (1,1)
    sSize = (p_spriteSize[0]+p_border[0],p_spriteSize[1]+p_border[1])
    for y in range(int(p_sheetName.get_size()[1]/sSize[1])):
        temp = []
        for x in range(int(p_sheetName.get_size()[0]/sSize[0])):
            temp.append(p_sheetName.subsurface(\
                        pygame.Rect(x*sSize[0]+p_border[0],\
                                    y*sSize[1]+p_border[1],\
                                    sSize[0]-p_border[0],\
                                    sSize[1]-p_border[1])))
        returnList.append(temp)
    return returnList

####################################################################
####    sprite setup                                            ####
####################################################################

### set up link sprites ############################################
link_spritesheet = pygame.image.load("link_spritesheet.bmp").convert()
link_spritesheet.set_colorkey(link_spritesheet\
                                        .get_at((0,0)), pygame.RLEACCEL)        
link_sprites = processSpritesheet(link_spritesheet,SPRITE_SIZE,(0,0))

### set up enemy sprites ############################################
enemy_spritesheet = pygame.image.load("enemy_spritesheet.bmp").convert()
enemy_spritesheet.set_colorkey(enemy_spritesheet\
                                        .get_at((0,0)), pygame.RLEACCEL)        
enemy_sprites = processSpritesheet(enemy_spritesheet,SPRITE_SIZE,(0,0))

### set up enemy1 sprites ############################################
enemy1_spritesheet = pygame.image.load("enemy1_spritesheet.bmp").convert()
enemy1_spritesheet.set_colorkey(enemy1_spritesheet\
                                        .get_at((0,0)), pygame.RLEACCEL)        
enemy1_sprites = processSpritesheet(enemy1_spritesheet,[30,47],(0,0))

### set up world sprites ###########################################
world_spritesheet = pygame.image.load("overworldtiles.bmp").convert()
world_sprites = processSpritesheet(world_spritesheet,PIXELS_PER_TILE,(2,2))

### sets the font to be used in the game ###########################
# the font selected must be in the directory
font = pygame.font.Font("FreeSerif.ttf", 75)
font2 = pygame.font.Font("FreeSerif.ttf", 35)

### sets the background color for when the screen is wiped #########
background_color = (0, 0, 0)

####################################################################
####################################################################
####################################################################
####    Game Class                                              ####
####################################################################
####################################################################
####################################################################

class GameClass():
    link = zeldish_link.LinkClass(link_sprites, gameScreen)
    world = zeldish_world.WorldClass(world_sprites, gameScreen)
    enemies = []
    heldItem = ""
    displayText = "Zeldish:"
    displayText2 = "Find All the Orbs"
    displayTextTimer = 250
    numberOfOrbs = 0
    numberOfHearts = 5
    spawnRate = 2 # out of 100000
    iTimer = 0
    maxMonsters = 200
    magicList = [] # [wLoc, color, frame] & frame == -1 ==> setup
    gameRunning = True
    swapTools = [False, [], False]
    
    spawnPoints = [[71,67],[103,67],[116,78],[82,78],\
                [243,67],[116,37],[68,45],[11,79],[119,37],\
                [39,26],[183,4],[76,1]]
    
    ############################################################
    ####   GameClass: Init                                  ####
    ############################################################
    def __init__(self):
        self.maxMonsters = zeldish_settings["max_monsters"]
        pygame.event.set_allowed([pygame.KEYDOWN,pygame.KEYUP,\
                        pygame.JOYAXISMOTION, pygame.JOYHATMOTION,\
                        pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN,\
                        pygame.MOUSEBUTTONDOWN])
        self.link = zeldish_link.LinkClass(link_sprites, gameScreen)
        self.world = zeldish_world.WorldClass(world_sprites, gameScreen)     
        self.enemies = []   
        
        ### sets up spawnPoints
        self.spawnPoints = []
        for y in range(len(self.world.worldData)):
            for x in range(len(self.world.worldData[y])):
                if self.world.worldData[y][x] == "12":
                    self.spawnPoints.append([x,y])
        
        self.spawnEnemy(0,roomLocToWorldLoc([7,2],[5,5]),"")
        self.heldItem = "68"
        self.numberOfOrbs = 0
        self.numberOfHearts = 5
        
        self.spawnRate = 5
        self.iTimer = 0
        magicList = [] # [wLoc, color, frame] & frame == -1 ==> setup
        self.gameRunning = True
        swapTools = [False, [], False]

    ############################################################
    ####    GameClass: Events                               ####
    ############################################################
    def game_event(self):
        # Gets the status of the keys at this instant
        # as oppzosed to getting it from the event que.
        # This alhttp://t.co/QiaXhwsF9Clows us to see if two keys are being
        # pressed at the same time.
        kRight = pygame.key.get_pressed()[pygame.K_RIGHT]
        kLeft = pygame.key.get_pressed()[pygame.K_LEFT]
        kUp = pygame.key.get_pressed()[pygame.K_UP]
        kDown = pygame.key.get_pressed()[pygame.K_DOWN]

        # Gets joystick inputs only if there is a joystick.
        if pygame_joystick == True:
            jAxis = (controller.get_axis(0),controller.get_axis(1))
            ### Joystick events ############################
            if jAxis[0] > 0.5:
                kRight = True
                kLeft = False
            if jAxis[0] < -0.5:
                kLeft = True
                kRight = False
            if jAxis[1] > 0.5:
                kUp = False
                kDown = True
            if jAxis[1] < -0.5:
                kUp = True
                kDown = False

        ### Keyboard Events ####################################

        # This uses the status of the keys that we got at
        # the start of the game_event() funtion.
        if kRight == True and kLeft == False:
            self.link.walkRight()
        if kRight == False and kLeft == True:
            self.link.walkLeft()
        if kRight == False and kLeft == False:
            self.link.hStop()
        if kRight == True and kLeft == True:
            self.link.hStop()
        if kUp == True and kDown == False:
            self.link.walkUp()
        if kUp == False and kDown == True:
            self.link.walkDown()
        if kUp == False and kDown == False:
            self.link.vStop()
        if kUp == True and kDown == True:
            self.link.vStop()

        # This uses the event que.
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                #debugging
                #if event.key == pygame.K_e:
                #    for x in range(len(self.enemies)):
                #        if self.enemies[x].eType == "girl":
                #            print x, self.enemies[x].worldLoc
                #        print len(self.enemies)
                #
                #if event.key == pygame.K_w:
                #    self.maxMonsters += 50
                #    print "Max Monsters:", self.maxMonsters
                #if event.key == pygame.K_q:
                #    self.maxMonsters = max(50, self.maxMonsters - 50)
                #    print "Max Monsters:", self.maxMonsters
                #if event.key == pygame.K_a:
                #    print self.link.worldLoc, self.link.roomIndex
                
                #real commands
                if event.key == pygame.K_z:
                    self.swapItem(2)
                if event.key == pygame.K_x:
                    self.swapItem(1)
                    
            # This section we put any key-up we want to catch.
            if event.type == pygame.KEYUP:
            #    if event.key == pygame.K_x:
                pass
                
            # This catches someone clicking on the close window box.
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit(0)

            # This catches the joystick button-down
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    self.swapItem(1)
                if event.button == 1:
                    self.swapItem(2)
            # This catches the joystick button-up
            if event.type == pygame.JOYBUTTONUP:
            #    if event.button == 0:
            #       self.link.animationHandler((0,0))
                pass
            # This catches mouse button-down
            if event.type == pygame.MOUSEBUTTONDOWN:
                #temp = pygame.mouse.get_pos()
                #setTemp = [(temp[0]-SCREEN_OFFSET[0]-\
                #               SPRITE_SIZE[0]/2)/GAME_SCALE,\
                #           (temp[1] - SCREEN_OFFSET[1] -\
                #                SPRITE_SIZE[1]/2)/GAME_SCALE] 
                #self.enemies[0].autoList.append([temp[0], temp[1]])
                pass
            

    ############################################################
    ####    GameClass: Collision                            ####
    ############################################################
    def game_collision(self, p_name):
        ### vertical check #################################
        hitRect = p_name.hitRect.inflate(-14,0)
        # Checks moving to the right.
        if p_name.vD > 0:
            if (self.world.getTileTypeByPixel(hitRect.bottomleft)\
                        not in walkList) or\
                        (self.world.getTileTypeByPixel(hitRect.bottomright)\
                        not in walkList):
                p_name.vStop()
                p_name.staticMove([0, -(hitRect.bottom%\
                                                PIXELS_PER_TILE[1])])
        # Checks moving to the left.
        if p_name.vD < 0:
            if (self.world.getTileTypeByPixel(hitRect.topleft)\
                            not in walkList)\
                            or (self.world.getTileTypeByPixel(hitRect.topright)\
                            not in walkList):
                p_name.vStop()
                p_name.staticMove([0, PIXELS_PER_TILE[1] - \
                                    (hitRect.top%PIXELS_PER_TILE[1])])

        ### horizontal check ###############################
        hitRect = p_name.hitRect.inflate(0,-14)
        # Checks moving down.
        if p_name.hD > 0:
            if (self.world.getTileTypeByPixel(hitRect.topright) \
                            not in walkList) or \
                            (self.world.getTileTypeByPixel(hitRect.bottomright)\
                            not in walkList):
                p_name.hStop()
                p_name.staticMove([-(hitRect.right%\
                                              PIXELS_PER_TILE[0]),0])
        # Checks moving up.
        if p_name.hD < 0:
            if (self.world.getTileTypeByPixel(hitRect.topleft) \
                            not in walkList) or \
                            (self.world.getTileTypeByPixel(hitRect.bottomleft) \
                            not in walkList):
                p_name.hStop()
                p_name.staticMove([PIXELS_PER_TILE[0] - \
                                   (hitRect.left%PIXELS_PER_TILE[0]),0])
                                   
    def swapItem(self, n):
        loc = copy.copy(self.link.getTile("",1))
        self.swapTools[1] = self.link.worldLoc[:]
        if n == 1:
            self.magicList.append([loc, (59,166,189,1), -1])
            temp = self.world.getTileType(loc)
            self.world.changeTerrain(loc, self.heldItem)
            self.heldItem = temp
        if n == 0:
            self.magicList.append([loc, (59,166,189,1), -1])
            self.world.changeTerrain(loc, self.heldItem)
        if n == 2:
            loc2 = copy.copy(self.link.getTile("",-1))
            self.magicList.append([loc, (59,166,189,1), -2])
            self.magicList.append([loc2, (59,166,189,1), -2])
            t = self.world.getTileType(loc)
            t2 = self.world.getTileType(loc2)
            self.world.changeTerrain(loc, t2)
            self.world.changeTerrain(loc2, t)
        
    def spawnEnemy(self,eType, location, spot):
        if spot == "":
            if eType == 0:
                self.enemies.append(zeldish_enemy.EnemyClass\
                                (enemy_sprites, gameScreen,\
                                eType, location,\
                                self.world.roomView))
            if eType == 1:
                self.enemies.append(zeldish_enemy.EnemyClass\
                                (enemy1_sprites, gameScreen,\
                                eType, location,\
                                self.world.roomView))
        else:
            if eType == 0:
                self.enemies[spot] = zeldish_enemy.EnemyClass\
                                (enemy_sprites, gameScreen,\
                                eType, location,\
                                self.world.roomView)
            if eType == 1:
                self.enemies[spot] = zeldish_enemy.EnemyClass\
                                (enemy1_sprites, gameScreen,\
                                eType, location,\
                                self.world.roomView)
        
    ############################################################
    ####    GameClass: Update                               ####
    ############################################################
    def roomSwitchTest(self):
        # Checks to see if link has moved into the next room,
        # and loads the new room if he has.

        #### START BUG FIX #################################
        if self.link.roomIndex[0] < 0:
            self.link.roomIndex[0] = ROOMS_PER_WORLD[0]-1
            self.world.roomView[0] = ROOMS_PER_WORLD[0]-1
            self.link.update()
        if self.link.roomIndex[0] >= ROOMS_PER_WORLD[0]:
            self.link.roomIndex[0] = 0
            self.world.roomView[0] = 0
            self.link.update()
        if self.link.roomIndex[1] < 0:
            self.link.roomIndex[1] = ROOMS_PER_WORLD[1]-1
            self.world.roomView[1] = ROOMS_PER_WORLD[1]-1
            self.link.update()
        if self.link.roomIndex[1] >= ROOMS_PER_WORLD[1]:
            self.link.roomIndex[1] = 0
            self.world.roomView[1] = 0
            self.link.update()
            
        if self.enemies[0].eType != "girl":
            self.enemies[0].enemy_sprites = enemy_sprites
            self.enemies[0].eType = "girl"
        #### END BUG FIX ####################################

        linkRoomIndex = worldLocToRoomIndex(self.link.worldLoc)
        worldRoomView = self.world.roomView
        if linkRoomIndex != worldRoomView:
            self.world.changeRoom(linkRoomIndex)
            self.link.roomIndex = linkRoomIndex
        
        if linkRoomIndex[0] > worldRoomView[0]:
            self.link.staticMove([-PIXELS_PER_ROOM[0],0])
        if linkRoomIndex[0] < worldRoomView[0]:
            self.link.staticMove([PIXELS_PER_ROOM[0],0])
        if linkRoomIndex[1] > worldRoomView[1]:
            self.link.staticMove([0,-PIXELS_PER_ROOM[1]])
        if linkRoomIndex[1] < worldRoomView[1]:
            self.link.staticMove([0,PIXELS_PER_ROOM[1]])
            
    def game_update(self):
        ### checks for orbs
        t = self.link.worldLoc
        isOrb = False
        if [t[0],t[1]] in self.world.orbPoints:
            isOrb = True
            orbTemp = t
        if [t[0]-1,t[1]] in self.world.orbPoints:
            isOrb = True
            orbTemp = [t[0]-1,t[1]]
        if [t[0],t[1]-1] in self.world.orbPoints:
            isOrb = True
            orbTemp = [t[0],t[1]-1]
        if [t[0]-1,t[1]-1] in self.world.orbPoints:
            isOrb = True
            orbTemp = [t[0]-1,t[1]-1]
        if isOrb == True:
            self.world.orbPoints.remove(orbTemp)
            self.numberOfOrbs += 1
            self.world.changeTerrain([orbTemp[0],orbTemp[1]], "02")
            self.world.changeTerrain([orbTemp[0]+1,orbTemp[1]], "02")
            self.world.changeTerrain([orbTemp[0],orbTemp[1]+1], "02")
            self.world.changeTerrain([orbTemp[0]+1,orbTemp[1]+1], "02")
            self.numberOfHearts = min(self.numberOfHearts + 1, 5)
                    
        ### gets a list of tiles with enemies in them
        occupiedTiles = []
        for x in range(len(self.enemies)):
            occupiedTiles.append(self.enemies[x].worldLoc)

        ### spawns bad guys
        for x in self.spawnPoints:
            if random.randint(0,1000) < self.spawnRate: #
                if x not in occupiedTiles:
                    if len(self.enemies) < self.maxMonsters:
                        self.spawnEnemy(1,x,"")
                    if len(self.enemies) >= self.maxMonsters:
                        self.spawnEnemy(1,x,random.randrange(len(self.enemies)))
        if len(self.enemies) > self.maxMonsters:
            self.enemies = self.enemies[:self.maxMonsters]
        
        ### Red Witch changes one tile
        if self.enemies[0].cooldown < 0:
            self.enemies[0].cooldown = self.enemies[0].startingCooldown
            xT0 = self.enemies[0].worldLoc[0]-1+random.randint(0,1)*2
            yT0 = self.enemies[0].worldLoc[1]-1+random.randint(0,1)*2
            self.world.changeTerrain([xT0,yT0], "68")
            self.magicList.append([[xT0,yT0], (59,166,189,1), -1])        
        
        ### gets enemy hits
        if self.iTimer > 0: 
            self.iTimer -= 1
        else:
            if self.link.worldLoc in occupiedTiles:
                self.magicList.append([self.link.worldLoc, (230,0,0,30), -3])
                self.numberOfHearts = max(self.numberOfHearts - 1,-1)
                self.iTimer = 150
        
        def getMovement(oT, n):     # oT = occupiedTiles
            returnList = []
            t0 = self.enemies[n].worldLoc
            # up
            t = [t0[0],t0[1]-1]
            if self.world.getTileType(t) in walkList:
                if t not in oT:
                    returnList.append([0,-1])
            # right
            t = [t0[0]+1,t0[1]]
            if self.world.getTileType(t) in walkList:
                if t not in oT:
                    returnList.append([1,0])
            # down
            t = [t0[0],t0[1]+1]
            if self.world.getTileType(t) in walkList:
                if t not in oT:
                    returnList.append([0,1])
            # left
            t = [t0[0]-1,t0[1]]
            if self.world.getTileType(t) in walkList:
                if t not in oT:
                    returnList.append([-1,0])
            return returnList
            
        #self.world.update()    # world.update does nothing
        self.roomSwitchTest()
        t = self.link.worldLoc[:]
        self.link.update()
        if t != self.link.worldLoc[:] and self.swapTools[0] == True:
            self.swapItem(2)
        
        for x in range(len(self.enemies)):
            self.enemies[x].update(self.world.roomView,\
                            self.link.worldLoc,\
                            getMovement(occupiedTiles, x))

        self.game_collision(self.link)
        #for x in range(len(self.enemies)):
        #   self.game_collision(self.enemies[x])
        
        # processes displayText
        if self.displayTextTimer >= 0:
            self.displayTextTimer -= 1
        if self.displayTextTimer < 0:
            self.displayText = ""
            self.displayText2 = ""
         
    ############################################################
    ####    GameClass: Draw                                 ####
    ####        Takes care of scaling the gameScreen,       ####
    ####        drawing it to the screen object, then       ####
    ####        drawing the screen object to the actual     ####
    ####        computer screen.                            ####
    ############################################################
    def drawUI(self):
        #sets up the held item
        xSize = 20
        uiScreen.fill(background_color)
        temp = int("0x" + self.heldItem,16)
        yVal = temp/xSize
        xVal = temp - yVal*xSize
        bs = 5 # bs is boarderSize
        pygame.draw.rect(uiScreen,(200,200,200),\
                    [(UI_SIZE[0]-PIXELS_PER_TILE[0])/2-bs,\
                    (UI_SIZE[1]-PIXELS_PER_TILE[1])/2-bs,\
                    PIXELS_PER_TILE[0]+2*bs,\
                    PIXELS_PER_TILE[1]+2*bs])
        uiScreen.blit(world_sprites[yVal][xVal],\
                    [(UI_SIZE[0]-PIXELS_PER_TILE[0])/2,\
                    (UI_SIZE[1]-PIXELS_PER_TILE[1])/2,\
                    PIXELS_PER_TILE[0],\
                    PIXELS_PER_TILE[1]])
        for x in range(self.numberOfOrbs):
            uiScreen.blit(world_sprites[8][3],\
                    [32*x, 10,\
                    PIXELS_PER_TILE[0], PIXELS_PER_TILE[1]])
        for x in range(self.numberOfHearts):
            uiScreen.blit(world_sprites[8][0],\
                    [40*x+300, 10,\
                    PIXELS_PER_TILE[0], PIXELS_PER_TILE[1]])

    def game_draw(self):
        ### blanks the screen
        screen.fill(background_color)
        
        ### objects draw to the gameScreen
        self.world.draw()
        if self.iTimer == 0:
            self.link.draw()
        elif self.iTimer/5%2 == 0:
            self.link.draw()
        for x in range(len(self.enemies)):
            self.enemies[x].draw()
        
        ###draws magic
        tempList = []
        x = 0
        magicFrames = 5
        while x < len(self.magicList):
            if self.magicList[x][2] < 0: 
                wTemp = self.magicList[x][0]
                vTemp = self.world.roomView
                rTemp = [wTemp[0]-vTemp[0]*TILES_PER_ROOM[0],\
                            wTemp[1]-vTemp[1]*TILES_PER_ROOM[1]]
                pTemp = [rTemp[0]*PIXELS_PER_TILE[0],\
                            rTemp[1]*PIXELS_PER_TILE[1]]
                self.magicList[x] = [pTemp,\
                                self.magicList[x][1],\
                                magicFrames]
                if rTemp[0] < 0 or rTemp[1] < 0:
                    self.magicList[x][2] = 0
                if rTemp[0] >= TILES_PER_ROOM[0]:
                    self.magicList[x][2] = 0
                if rTemp[1] >= TILES_PER_ROOM[1]:
                    self.magicList[x][2] = 0
            elif self.magicList[x][2] == 0:
                self.magicList.pop(x)
                x -= 1
            elif self.magicList[x][2] > 0:
                pygame.draw.rect(gameScreen, self.magicList[x][1],\
                            [self.magicList[x][0],\
                            [PIXELS_PER_TILE[0]/magicFrames*\
                                                self.magicList[x][2],\
                            PIXELS_PER_TILE[1]]],0)
                self.magicList[x][2] -= 1
            x += 1
        
        ### draws gameScreen & uiScreen to smallScreen
        smallScreen.blit(gameScreen,\
                                [[SCREEN_OFFSET[0],\
                                SCREEN_OFFSET[1]+UI_SIZE[1]],\
                                [GAME_SCREEN_SIZE[0],\
                                GAME_SCREEN_SIZE[1]]])
        self.drawUI()
        smallScreen.blit(uiScreen,\
                                [[SCREEN_OFFSET[0],\
                                SCREEN_OFFSET[1]],\
                                [UI_SIZE[0],\
                                UI_SIZE[1]]])

        ### draws displayText
        if self.displayText != "" or self.displayText2 != "":
            sizeTemp = font.size(self.displayText)
            sizeTemp2 = font2.size(self.displayText2)
            locationTemp = [GAME_SCREEN_SIZE[0]/2+SCREEN_OFFSET[0]-sizeTemp[0]/2,\
                            GAME_SCREEN_SIZE[1]/2+SCREEN_OFFSET[0]-sizeTemp[1]/2]
            locationTemp2 = [GAME_SCREEN_SIZE[0]/2+SCREEN_OFFSET[0]-sizeTemp2[0]/2,\
                            GAME_SCREEN_SIZE[1]/2+SCREEN_OFFSET[0]+sizeTemp[1]/2]
            text = font.render(str(self.displayText), 1, background_color)
            text2 = font2.render(str(self.displayText2), 1, background_color)
            smallScreen.blit(text, locationTemp)
            smallScreen.blit(text2, locationTemp2)

        ### scales smallScreen and draws it to screen
        screen.blit(pygame.transform.scale(smallScreen,\
                                (SMALL_SCREEN_SIZE[0]*GAME_SCALE,\
                                SMALL_SCREEN_SIZE[1]*GAME_SCALE)),\
                                [0,0])

        # updates the screen
        pygame.display.update()

####################################################################
####################################################################
####    main()                                                  ####
####################################################################
####################################################################
def main():
    gameClock = pygame.time.Clock() # Starts the game clock to set
                                    # up the frames per second.

    while True:
        game = GameClass()              # creates the game
        
        ### starts the event-update-draw loop ######################      
        while game.gameRunning == True:
            gameClock.tick(50)          # runs at 50 frames per second
            game.game_event()      
            game.game_update()
            if game.numberOfHearts <= 0: 
                game.gameRunning = False
                game.displayText = "You have died."
                game.displayText2 = "So many hearts, gone."
                game.game_draw()
                pygame.time.wait(8000)
            if game.numberOfOrbs >= 7:
                game.displayText = "You have won."
                game.displayTextTimer = 10000
            game.game_draw()
            
        ############################################################
        del game

main()  # Starts the main function
