import pygame
import os
import random
 
class Player(pygame.sprite.Sprite):
    #player ship, has a powerLevel for the bullets, which is leveled up through
    #gaining exp
    def __init__(self,x,y,health=10,powerLevel=1,exp=0):
        pygame.sprite.Sprite.__init__(self)
        self.health = health
        self.powerLevel = powerLevel
        self.exp = exp
        self.image = pygame.image.load(os.path.join('Assets',
                                        'Player','player.png')).convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey((0,0,0))
        self.rect.centerx = x
        self.rect.centery = y
        self.velocity = 10
    def update(self):
        if self.exp >= 100 and self.powerLevel < 3:
            self.powerLevel += 1
            self.exp = 0
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
                                            self.rect.midtop[1],self.powerLevel)
            bulletLeft = PlayerBullet(self.rect.midtop[0]-20,
                                            self.rect.midtop[1]-20,self.powerLevel)
            bulletRight = PlayerBullet(self.rect.midtop[0]+20,
                                            self.rect.midtop[1]-20,self.powerLevel)
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
        self.image = pygame.transform.scale(pygame.image.load(os.path.join('Assets','Enemies',filePath)).convert(),(80,85))
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
    #This level class contains 3 parrallel lists, monsterList,spawnAmount
    #and spawnWait. The same index indicates the monster should be spawned that many times
    #And the spawnWait is the interval between spawns. If the interval is None,
    #It means it should spawn as soon as the next monster comes up.
    def __init__(self, enemyList,spawnAmount,spawnWait,level):
        self.enemyList = enemyList
        self.spawnAmount = spawnAmount
        self.spawnWait = spawnWait #The last element of this list should be the timer between levels.
        self.level = level
    def __repr__(self):
        return self.level
    
    