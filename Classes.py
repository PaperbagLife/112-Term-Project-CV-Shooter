import pygame
import os
import random
import math
 
class Player(pygame.sprite.Sprite):
    #player ship, has a powerLevel for the bullets, which is leveled up through
    #gaining exp
    def __init__(self,x,y,health=20,powerLevel=1,exp=0):
        pygame.sprite.Sprite.__init__(self)
        self.health = health
        self.powerLevel = powerLevel
        self.exp = exp
        self.normalImage = pygame.image.load(os.path.join('Assets',
                                        'Player','playerNew.png')).convert()
        self.hurtImage = pygame.image.load(os.path.join('Assets',
                                        'Player','playerHurt.png')).convert()
        self.normalImage.set_colorkey((102,204,255))
        self.hurtImage.set_colorkey((205,67,112))
        self.image = self.normalImage
        self.rect = self.image.get_rect()
        self.invincibleTimer = 0
        self.invincible = False
        self.rect.centerx = x
        self.rect.centery = y
        self.velocity = 10
        ## Get a measure of the user's performance based on health lost in last 20 seconds.
        #Change enemy shootTimer to higher based on the performance.
        #Performance highest is 0, lowest is 50
        self.performance = 0
        self.prevHealth = self.health
        self.performanceTimer = 300 #Around 16 seconds
        self.deltHealth = 0
    def update(self,enemyBulletGroup):
        if self.exp >= 100 and self.powerLevel < 3:
            self.powerLevel += 1
            self.exp = 0
        if self.invincibleTimer > 0:
            self.invincibleTimer -= 1
            if self.invincibleTimer %5 >= 2:
                self.image = self.hurtImage
            else:
                self.image = self.normalImage
        if self.invincibleTimer <= 0 and self.invincible:
            self.invincible = False
            self.image = self.normalImage
        self.performanceTimer -= 1
        if self.performanceTimer <= 0:
            self.deltHealth = self.prevHealth - self.health
            #Determining performance by number of bullets on screen and health lost
            bulletOnScreen = len(enemyBulletGroup)
            if bulletOnScreen!=0:
                self.performance = 50*(self.deltHealth/(bulletOnScreen+10))
            self.performanceTimer = 300
            print("Performance: ",self.performance)
    def shoot(self,playerBulletGroup):
        if self.powerLevel == 1:
            bullet = PlayerBullet(self.rect.midtop[0],
                                            self.rect.midtop[1],1)
            playerBulletGroup.add(bullet)
        elif self.powerLevel == 2:
            bullet1 = PlayerBullet(self.rect.midtop[0]-10,
                                            self.rect.midtop[1],1)
            bullet2 = PlayerBullet(self.rect.midtop[0]+10,
                                            self.rect.midtop[1],1)
            playerBulletGroup.add(bullet1,bullet2)
        elif self.powerLevel == 3:
            bulletMid = PlayerBullet(self.rect.midtop[0],
                                            self.rect.midtop[1],1)
            bulletLeft = PlayerBullet(self.rect.midtop[0]-20,
                                            self.rect.midtop[1]-20,1)
            bulletRight = PlayerBullet(self.rect.midtop[0]+20,
                                            self.rect.midtop[1]-20,1)
            playerBulletGroup.add(bulletMid,bulletLeft,bulletRight)
class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self,x,y,power):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('Assets','Bullets',
                            'powerLevel'+str(power)+".png")).convert()
        self.image.set_colorkey((0,0,0))
        self.power = power
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.velocity = 30
    def move(self):
        self.rect.centery -= self.velocity
class Enemy(pygame.sprite.Sprite):
    def __init__(self,health,exp,shootTimer,filePath,velocity,x = None, size = (80,80)):
        pygame.sprite.Sprite.__init__(self)
        self.health = health
        self.exp = exp
        if size != None:
            self.image = pygame.transform.scale(pygame.image.load\
                    (os.path.join('Assets','Enemies',filePath)).convert(),size)
        else:
            self.image = pygame.image.load(os.path.join('Assets','Enemies',filePath)).convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey((0,0,0))
        if x != None:
            self.rect.centerx = x
        else:
            self.rect.centerx = random.randint(50,550)
        self.rect.centery = -20
        self.baseShootTimer = shootTimer
        self.shootTimer = shootTimer
        self.timer = shootTimer
        self.baseVelocity = velocity
        self.velocity = velocity
    def shoot(self,enemyBulletGroup,player):
        self.timer -= 1
        if self.timer <= 0:
            deltX = player.rect.centerx - self.rect.centerx
            deltY = player.rect.centery - self.rect.bottom
            mag = (deltX**2 + deltY**2)**0.5
            direction = (deltX/mag, deltY/mag)
            bullet = EnemyStraightBullet(self.rect.centerx,self.rect.bottom,direction)
            enemyBulletGroup.add(bullet)
            self.timer = self.shootTimer
    def move(self):
        self.rect.centery += self.velocity
    def update(self,playerPerformance):
        self.shootTimer = self.baseShootTimer + playerPerformance
        self.velocity = self.baseVelocity - 0.005*playerPerformance
        
    
class MoveEnemy(Enemy):
    def __init__(self,health,exp,shootTimer,filePath,velocity,x = None):
        super().__init__(health,exp,shootTimer,filePath,velocity,x = None)
        self.cosCounter = 0
    def move(self):
        self.rect.centery += self.velocity
        self.cosCounter = (self.cosCounter+1)%200
        ##20 is one cycle of cos
        self.rect.centerx += 2*self.velocity*math.cos(self.cosCounter/200*2*math.pi)
    
class MiniBoss1(Enemy):
    def __init__(self,health,exp,shootTimer,filePath,velocity,x = None):
        super().__init__(health,exp,shootTimer,filePath,velocity,x = 300, size = None)
        self.rect.bottom = 0
        self.moveRight = True
        self.type1Shots = 5
    def shoot(self,enemyBulletGroup,player):
        self.timer -= 1
        if self.timer <= 0:
            attackType = random.choice([1,2])
            if attackType == 1:
                direction = (0,-1)
                for i in range(self.type1Shots+1):
                    xVel = (-3**0.5)*math.cos(math.pi*2/3/(self.type1Shots)*i)-\
                                (-math.sin(math.pi*2/3/(self.type1Shots)*i))
                    yVel = (-3**0.5)*math.sin(math.pi*2/3/(self.type1Shots)*i)+\
                                (-math.cos(math.pi*2/3/(self.type1Shots)*i))
                    direction = (xVel,-yVel)
                    bullet = EnemyStraightBullet(self.rect.centerx,self.rect.bottom,direction)
                    enemyBulletGroup.add(bullet)
                self.timer = self.shootTimer
            elif attackType == 2:
                gunPos = [self.rect.bottomleft,self.rect.midbottom,self.rect.bottomright]
                for gunPosition in gunPos:
                    deltX = player.rect.centerx - gunPosition[0]
                    deltY = player.rect.centery - gunPosition[1]
                    mag = (deltX**2 + deltY**2)**0.5
                    direction = (deltX/mag, deltY/mag)
                    bullet = EnemyStraightBullet(gunPosition[0],gunPosition[1]-10,direction)
                    enemyBulletGroup.add(bullet)
                self.timer = self.shootTimer
    def move(self):
        if self.rect.top <= 0:
            self.rect.centery += self.velocity
        else:
            if self.rect.right >= 600 or self.rect.left <= 0:
                self.moveRight = not self.moveRight
            if self.moveRight:
                self.rect.centerx += self.velocity
            else:
                self.rect.centerx -= self.velocity
    def update(self,playerPerformance):
        self.shootTimer = self.baseShootTimer + playerPerformance
        
class EnemyStraightBullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('Assets','Bullets',
                            'enemyBullet2.png')).convert()
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.direction = direction
    def move(self):
        self.rect.centerx += 8*self.direction[0]
        self.rect.centery += 8*self.direction[1]
        
class Repair(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join('Assets','PowerUps',
                            'repair.png')).convert(),(50,50))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
    def move(self):
        self.rect.centery += 5
        
class Level(object):
    #This level class contains enemies in order, and the spawn wait time between them.
    def __init__(self, enemyList,spawnAmount,spawnWait,level):
        self.enemyList = enemyList
        self.spawnWait = spawnWait #The last element of this list should be the timer between levels.
        self.spawnAmount = spawnAmount
        self.level = level
    def __repr__(self):
        return str(self.level)
    
    
class Background(pygame.sprite.Sprite):
    def __init__(self,filePath):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('Assets','Background',filePath)).convert()
        self.rect = self.image.get_rect()
        self.rect.left = 0
        self.rect.bottom = 800
    def move(self):
        self.rect.centery += 1
        if self.rect.top >= 0:
            self.rect.bottom = 800
        
class Button(pygame.sprite.Sprite):
    def __init__(self,x,y,filePath1,filePath2,action):
        pygame.sprite.Sprite.__init__(self)
        self.normalImage = pygame.image.load(os.path.join('Assets','Background',filePath1)).convert()
        self.hoverImage = pygame.image.load(os.path.join('Assets','Background',filePath2)).convert()
        self.image = pygame.image.load(os.path.join('Assets','Background',filePath1)).convert()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.action = action
    def update(self,mousePos,click):
        
        if self.rect.left <= mousePos[0] <= self.rect.right and\
                            self.rect.top <= mousePos[1] <= self.rect.bottom:
            self.image = self.hoverImage
            if click[0]:
                print("click")
                self.action()
        else:
            self.image = self.normalImage

class TeamEnemy(pygame.sprite.Sprite):
    def __init__(self,x = None):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('Assets','Enemies',"GroupEnemytrial.png")).convert()
        self.rect = self.image.get_rect()
        self.exp = 10
        self.health = 20
        self.rect.centerx = 300
        self.rect.bottom = 0
        self.image.set_colorkey((0,0,0))
        self.moveDir = [(-1,1),(1,1),(1,-1),(-1,-1)]
        self.moveInterval = 30
        self.shootInterval = self.moveInterval
        self.shootTimer = self.shootInterval
        self.moveDuration = 30
        self.moveDurationTimer = self.moveDuration
        self.moveIntervalTimer = self.moveInterval
        self.stop = True
        self.velocity = 3
        self.moveIndex = 0
    def move(self):
        if self.rect.centery <= 200: self.rect.centery += self.velocity
        else:
            if self.moveDurationTimer <= 0 and not self.stop:
                self.moveIndex = (self.moveIndex+1)%4
                self.stop = True
                self.moveDurationTimer = self.moveDuration
            elif self.moveDuration > 0 and not self.stop:
                self.rect.centerx += self.velocity*self.moveDir[self.moveIndex][0]
                self.rect.centery += self.velocity*self.moveDir[self.moveIndex][1]
                self.moveDurationTimer -= 1
            elif self.stop and self.moveIntervalTimer > 0:
                self.moveIntervalTimer -= 1
            elif self.moveIntervalTimer <= 0:
                self.stop = False
                self.moveIntervalTimer = self.moveInterval
    def shoot(self,enemyBulletGroup,mode,player):
        if not self.stop:
            return
        if self.stop and self.shootTimer > 0:
            self.shootTimer -= 1
            return
        if mode == "Straight":
            deltX = player.rect.centerx - self.rect.centerx
            deltY = player.rect.centery - self.rect.bottom
            mag = (deltX**2 + deltY**2)**0.5
            direction = (deltX/mag, deltY/mag)
            bullet = EnemyStraightBullet(self.rect.centerx,self.rect.bottom,direction)
            self.shootTimer = self.shootInterval
            enemyBulletGroup.add(bullet)
        elif mode == "Right":
            deltX = player.rect.centerx + 80 - self.rect.centerx
            deltY = player.rect.centery - self.rect.bottom
            mag = (deltX**2 + deltY**2)**0.5
            direction = (deltX/mag, deltY/mag)
            bullet = EnemyStraightBullet(self.rect.centerx,self.rect.bottom,direction)
            self.shootTimer = self.shootInterval
            enemyBulletGroup.add(bullet)
        elif mode == "Left":
            deltX = player.rect.centerx - 80 - self.rect.centerx
            deltY = player.rect.centery - self.rect.bottom
            mag = (deltX**2 + deltY**2)**0.5
            direction = (deltX/mag, deltY/mag)
            bullet = EnemyStraightBullet(self.rect.centerx,self.rect.bottom,direction)
            self.shootTimer = self.shootInterval
            enemyBulletGroup.add(bullet)