import pygame
import os
import random
import math
 
class Player(pygame.sprite.Sprite):
    #player ship, has a powerLevel for the bullets, which is leveled up through
    #gaining exp
    def __init__(self,x,y,powerLevel=1,exp=0):
        pygame.sprite.Sprite.__init__(self)
        self.health = 15
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
        self.performanceTimer = 250 #Around 10 seconds
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
            self.performanceTimer = 250
            print("Performance: ",self.performance)
    def shoot(self,playerBulletGroup,mode = None):
        if mode == None:
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
        elif mode == "Challenge":
            bullet = PlayerChallengeBullet(self.rect.midtop[0],
                                                self.rect.midtop[1],1)
            playerBulletGroup.add(bullet)
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

class PlayerChallengeBullet(PlayerBullet):
    def __init__(self,x,y,power):
        pygame.sprite.Sprite.__init__(self)
        super().__init__(x,y,power)
        self.velocity = 10
class SmartBoss(pygame.sprite.Sprite):
    #Should be able to dodge some bullets and attack player based on most frequent dodge directions
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.health = 50
        self.image = pygame.image.load(os.path.join('Assets','Enemies','Challenge.png')).convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey((0,0,0))
        self.rect.centerx = 300
        self.rect.top = 0
        self.velocity = 9
        self.threats = []
        #PlayerAnalysis contains offset X locations of the player
        #Since the player can only move left/right
        #Each time shoot out an extra bullet towards the predicted player location
        #based on how the player tend to dodge each time.
        self.playerAnalysis = []
        self.directShootTimer = 20
        self.homingShootTimer = 100
        self.score = 0
        
    def update(self,playerBulletGroup,enemyBulletGroup):
        #Update self.threats with player.
        for bullet in playerBulletGroup:
            #Do math here
            #Distance should just be taken by y value, distance is only talking about priority of checking,
            #not necessarily be dodging for the cloest bullet. ie a missed bullet entirely
            distance = bullet.rect.top - self.rect.top
            if distance <= 0 or distance >= 2*self.rect.width + 2*bullet.rect.height:
                continue
            position = (bullet.rect.centerx,bullet.rect.centery)
            #Direction is just going to be (0,-1) since straight bullets by default
            self.threats.append(Threat(distance,position,bullet.rect.width))
        self.threats.sort()
    def move(self):
        #move based on threats
        #Default dodge direction = left
        leftCount = 0
        rightCount = 0
        for threat in self.threats:
            width = threat.width
            projectionX = threat.position[0]
            self.score += 1
            if projectionX -5 < self.rect.width and self.rect.left < self.rect.width + 10:
                rightCount += 100 / threat.position[1]
            elif projectionX + 5 > 600 - self.rect.width and self.rect.right > 600 - self.rect.width - 10:
                leftCount += 100 / threat.position[1]
            #middle case, can both dodge left or right
            elif self.rect.right + width > projectionX > self.rect.centerx - width:
                leftCount += 100 / threat.position[1]
            elif self.rect.left - width < projectionX < self.rect.centerx + width:
                rightCount += 100 / threat.position[1]
            else:
                self.score -= 1
        if leftCount > rightCount and self.rect.left > 0:
            #move left
            self.rect.centerx -= self.velocity
        elif rightCount > leftCount and self.rect.right < 600:
            #move right
            self.rect.centerx += self.velocity
        self.threats = []
    def shoot(self, player, enemyBulletGroup):
        self.homingShootTimer -= 1
        self.directShootTimer -= 1
        if self.directShootTimer <= 0:
            deltX = player.rect.centerx - self.rect.centerx + 10
            deltY = player.rect.centery - self.rect.bottom
            mag = (deltX**2 + deltY**2)**0.5
            mag = 20
            direction = (deltX/mag, deltY/mag)
            bullet = ChallengeStraightBullet(self.rect.centerx,self.rect.bottom,direction)
            enemyBulletGroup.add(bullet)
            self.directShootTimer = 20
        if self.homingShootTimer <= 0:
            homingBullet = HomingBullet(self.rect.centerx,self.rect.bottom,(0,0))
            enemyBulletGroup.add(homingBullet)
            self.homingShootTimer = 200
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
        self.rect.centerx += 10*self.direction[0]
        self.rect.centery += 10*self.direction[1]
        
class HomingBullet(EnemyStraightBullet):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        super().__init__(x,y,direction)
        self.timer = 150
    def move(self,player):
        deltX = player.rect.centerx - self.rect.centerx
        deltY = player.rect.centery - self.rect.bottom
        mag = (deltX**2 + deltY**2)**0.5
        direction = (deltX/mag, deltY/mag)
        self.rect.centerx += direction[0]*6
        self.rect.centery += direction[1]*6
        self.timer -= 1
        return self.timer <= 0
class Threat(object):
    #Threat class for player bullets. easier to manipulate/visualize
    def __init__(self,distance,position,width,velocity = 10):
        self.distance = distance
        self.position = position
        self.velocity = velocity
        self.width = width
    def __lt__(self, other):
         return isinstance(other,Threat) and self.distance < other.distance
         
# class ChallengeEnemyBullet()
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
        

class ChallengeStraightBullet(EnemyStraightBullet):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        super().__init__(x,y,direction)
    def move(self):
        self.rect.centerx += 0.4*self.direction[0]
        self.rect.centery += 0.4*self.direction[1]
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
        self.image = pygame.image.load(os.path.join('Assets','Enemies',
                        "GroupEnemytrial.png")).convert()
        self.rect = self.image.get_rect()
        self.exp = 10
        self.health = 50
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
class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        pygame.sprite.Sprite.__init__(self)
        ex1 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Enemies','Explosions','1.png')).convert(),scale)
        ex1.set_colorkey((0,0,0))
        ex2 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Enemies','Explosions','2.png')).convert(),scale)
        ex2.set_colorkey((0,0,0))
        ex3 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Enemies','Explosions','3.png')).convert(),scale)
        ex3.set_colorkey((0,0,0))
        ex4 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Enemies','Explosions','4.png')).convert(),scale)
        ex4.set_colorkey((0,0,0))
        ex5 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Enemies','Explosions','5.png')).convert(),scale)
        ex5.set_colorkey((0,0,0))
        ex6 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Enemies','Explosions','6.png')).convert(),scale)
        ex6.set_colorkey((0,0,0))
        ex7 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Enemies','Explosions','7.png')).convert(),scale)
        ex7.set_colorkey((0,0,0))
        ex8 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Enemies','Explosions','8.png')).convert(),scale)
        ex8.set_colorkey((0,0,0))
        self.image = ex1
        self.images = [ex1,ex2,ex3,ex4,ex5,ex6,ex7,ex8]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.count = 0
        self.timeInt = 3
    def update(self):
        self.timeInt -= 1
        if self.timeInt <= 0:
            self.count += 1
            self.timeInt = 3
        if self.count < len(self.images):
            self.image = self.images[self.count]
        #Return True if it needs to be destroyed, ie reached the end of explosion
        return self.count == len(self.images)

class Boss(pygame.sprite.Sprite):
    def __init__(self,velocity):
        pygame.sprite.Sprite.__init__(self)
        self.health = 150
        self.exp = 999
        self.image = pygame.image.load(os.path.join('Assets','Enemies',
                            'Boss.png')).convert()
        self.rect = self.image.get_rect()
        self.rect.centerx = 300
        self.rect.bottom = 0
        self.velocity = velocity
        self.moveRight = True
        #Self.stationary is used for laser attacks. Lazer 
        self.stationary = False
        self.lasers = []
        self.laserStopInterval = 150
        self.laserStopIntervalTimer = self.laserStopInterval
        self.laserPreludeDuration = 30
        self.laserPreludeTimer = self.laserStopInterval - self.laserPreludeDuration
        
        self.straightDownTimer = 220
        self.straightDownDuration = 100
        self.straightDownInterval = 20
        self.fanBulletTimer = 300
        self.fanBulletInterval = 20
        self.fanBulletDuration = 200
        self.fanShots = 6
    def move(self):
        if self.rect.top <= 0:
            self.rect.centery += self.velocity
        elif not self.stationary:
            if self.rect.right >= 600 or self.rect.left <= 0:
                self.moveRight = not self.moveRight
            if self.moveRight:
                self.rect.centerx += self.velocity
            else:
                self.rect.centerx -= self.velocity
    def shoot(self,enemyBulletGroup,player,preludeGroup):
        if self.laserStopIntervalTimer <= 0:
            laser1 = Laser(self.rect.centerx,self.rect.bottom-10,-30)
            laser2 = Laser(self.rect.centerx,self.rect.bottom-10, 30)
            enemyBulletGroup.add(laser1,laser2)
            self.laserStopIntervalTimer = self.laserStopInterval
            self.laserPreludeTimer = self.laserStopInterval - self.laserPreludeDuration
        self.laserStopIntervalTimer -= 1
        if self.laserPreludeTimer <= 0:
            prelude1 = Prelude(self.rect.centerx,self.rect.bottom-10,-30)
            prelude2 = Prelude(self.rect.centerx,self.rect.bottom-10, 30)
            preludeGroup.add(prelude1,prelude2)
        self.laserPreludeTimer -= 1
        if self.straightDownTimer <= 0:
            #Shoot straight down
            if self.straightDownDuration >= 0:
                if self.straightDownInterval <= 0:
                    bullet2 = EnemyStraightBullet(self.rect.centerx+80,self.rect.bottom,(0,1))
                    bullet3 = EnemyStraightBullet(self.rect.centerx-80,self.rect.bottom,(0,1))
                    enemyBulletGroup.add(bullet2,bullet3)
                    self.straightDownInterval = 10
                self.straightDownDuration -= 1
                self.straightDownInterval -= 1
            else:
                self.straightDownDuration = 100
                self.straightDownTimer = 300
        self.straightDownTimer -= 1
        if self.fanBulletTimer <= 0:
            #Shoot straight down
            if self.fanBulletDuration >= 0:
                if self.fanBulletInterval <= 0:
                    for i in range(self.fanShots+1):
                        xVel = (-3**0.5)*math.cos(math.pi*2/3/(self.fanShots)*i)-\
                                    (-math.sin(math.pi*2/3/(self.fanShots)*i))
                        yVel = (-3**0.5)*math.sin(math.pi*2/3/(self.fanShots)*i)+\
                                    (-math.cos(math.pi*2/3/(self.fanShots)*i))
                        mag = (xVel**2 + yVel**2)**0.5
                        direction = (xVel/mag,-yVel/mag)
                        bullet = EnemyStraightBullet(self.rect.centerx,
                                                    self.rect.bottom,direction)
                        enemyBulletGroup.add(bullet)
                    self.fanBulletInterval = 20
                self.fanBulletDuration -= 1
                self.fanBulletInterval -= 1
            else:
                self.fanBulletDuration = 100
                self.fanBulletTimer = 220
        self.fanBulletTimer -= 1
    def update(self,playerPerformance):
        pass
class Laser(pygame.sprite.Sprite):
    def __init__(self,x,shotY,offSet):
        pygame.sprite.Sprite.__init__(self)
        self.offSet = offSet
        scale = (60,800)
        laser1 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Bullets','lasers','1.png')).convert(),scale)
        laser1.set_colorkey((0,0,0))
        laser2 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Bullets','lasers','2.png')).convert(),scale)
        laser2.set_colorkey((0,0,0))
        laser3 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Bullets','lasers','3.png')).convert(),scale)
        laser3.set_colorkey((0,0,0))
        laser4 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Bullets','lasers','4.png')).convert(),scale)
        laser4.set_colorkey((0,0,0))
        laser5 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Bullets','lasers','5.png')).convert(),scale)
        laser5.set_colorkey((0,0,0))
        laser6 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Bullets','lasers','6.png')).convert(),scale)
        laser6.set_colorkey((0,0,0))
        laser7 = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Bullets','lasers','7.png')).convert(),scale)
        laser7.set_colorkey((0,0,0))
        self.images  = [laser1,laser2,laser3,laser4,laser5,laser6,laser7]
        self.image = laser1
        self.rect = self.image.get_rect()
        self.rect.centerx = x + self.offSet
        self.rect.top = shotY
        self.timeInt = 3
        self.count = 0
    def update(self,x):
        self.rect.centerx = x + self.offSet
        self.timeInt -= 1
        if self.timeInt <= 0:
            self.count += 1
            self.timeInt = 3
        self.image = self.images[self.count%len(self.images)]
        #Return True if it needs to be destroyed
        return self.count >= 15

class Prelude(pygame.sprite.Sprite):
    def __init__(self,x,shotY,offSet):
        pygame.sprite.Sprite.__init__(self)
        self.offSet = offSet
        scale = (30,800)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                        'Bullets','lasers','prelude.png')).convert(),scale)
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x+self.offSet
        self.rect.top = shotY
        self.timer = 4
        
    def update(self,x):
        self.rect.centerx = x + self.offSet
        self.timer -= 1
        return self.timer <= 0