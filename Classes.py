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
    def update(self):
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
        return self.powerLevel
    def shoot(self,playerBulletGroup):
        if self.powerLevel == 1:
            bullet = PlayerBullet(self.rect.midtop[0],
                                            self.rect.midtop[1],self.powerLevel)
            playerBulletGroup.add(bullet)
        elif self.powerLevel == 2:
            bullet1 = PlayerBullet(self.rect.midtop[0]-10,
                                            self.rect.midtop[1],self.powerLevel)
            bullet2 = PlayerBullet(self.rect.midtop[0]+10,
                                            self.rect.midtop[1],self.powerLevel)
            playerBulletGroup.add(bullet1,bullet2)
        elif self.powerLevel == 3:
            bulletMid = PlayerBullet(self.rect.midtop[0],
                                            self.rect.midtop[1],self.powerLevel-1)
            bulletLeft = PlayerBullet(self.rect.midtop[0]-20,
                                            self.rect.midtop[1]-20,self.powerLevel-1)
            bulletRight = PlayerBullet(self.rect.midtop[0]+20,
                                            self.rect.midtop[1]-20,self.powerLevel-1)
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
    def __init__(self,health,exp,shootTimer,filePath,velocity,x = None):
        pygame.sprite.Sprite.__init__(self)
        self.health = health
        self.exp = exp
        self.image = pygame.image.load(os.path.join('Assets','Enemies',filePath)).convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey((0,0,0))
        if x != None:
            self.rect.centerx = x
        else:
            self.rect.centerx = random.randint(50,550)
        self.rect.centery = -20
        self.shootTimer = shootTimer
        self.timer = shootTimer
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
        super().__init__(health,exp,shootTimer,filePath,velocity,x = 300)
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
                    xVel = (-3**0.5)*math.cos(math.pi*2/3/(self.type1Shots)*i)-(-math.sin(math.pi*2/3/(self.type1Shots)*i))
                    yVel = (-3**0.5)*math.sin(math.pi*2/3/(self.type1Shots)*i)+(-math.cos(math.pi*2/3/(self.type1Shots)*i))
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
        
class Level(object):
    #This level class contains enemies in order, and the spawn wait time between them.
    def __init__(self, enemyList,spawnAmount,spawnWait,level):
        self.enemyList = enemyList
        self.spawnWait = spawnWait #The last element of this list should be the timer between levels.
        self.spawnAmount = spawnAmount
        self.level = level
    def __repr__(self):
        return str(self.level)
    