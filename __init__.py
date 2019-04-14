import pygame
import os
import sys
import random
import cv2
import time
import numpy as np
import imutils

windowWidth = 600
windowHeight = 800
window = pygame.display.set_mode((windowWidth,windowHeight))
clock = pygame.time.Clock()
gameSpeed = 30

pygame.font.init()
hpFont = pygame.font.SysFont('Comic Sans MS', 30)

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
        bullet = PlayerBullet(self.rect.midtop[0],
                                        self.rect.midtop[1],self.powerLevel)
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
class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,health,exp,shootTimer,filePath):
        pygame.sprite.Sprite.__init__(self)
        self.health = health
        self.exp = exp
        self.image = pygame.transform.scale(pygame.image.load(os.path.join('Assets','Enemies',filePath)).convert(),(80,85))
        self.rect = self.image.get_rect()
        self.image.set_colorkey((0,0,0))
        self.rect.centerx = x
        self.rect.centery = -20
        self.shootTimer = shootTimer
        self.timer = shootTimer
        self.velocity = 5
    def shoot(self,enemyBulletGroup,player):
        self.timer -= 1
        if self.timer <= 0:
            deltX = player.rect.centerx - self.rect.centerx
            deltY = player.rect.centery - self.rect.bottom
            mag = (deltX**2 + deltY**2)**0.5
            print(deltX,deltY,mag)
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
        
### Enemy types
###Main game
def CVShooter():
    score = 0
    gameOver = False
    
    
    #Sprite Group for drawing player only
    playerSpriteGroup = pygame.sprite.Group() 
    player = Player(windowWidth//2,windowHeight - 80)
    playerSpriteGroup.add(player)
    
    playerBulletGroup = pygame.sprite.Group()
    enemyGroup = pygame.sprite.Group()
    enemyBulletGroup = pygame.sprite.Group()
    
    shootInterval = 10
    timeUntilShoot = shootInterval
    
    #OpenCV setup
    video = cv2.VideoCapture(0)
    while not gameOver:
        
        window.fill((0,0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                video.release()
                cv2.destroyAllWindows()
                return
        ##Open CV part Start
        check, frame = video.read()
        frame = imutils.resize(frame, width=600)
        #Mirrors the frame
        frame = cv2.flip(frame,1)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        lowerRed = np.array([100,150,125])
        higherRed = np.array([120,255,200])
    
        
        csv = cv2.cvtColor(blurred,cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(csv,lowerRed,higherRed)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None
    
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                    (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
        ##Control player with opencv
        if center != None:
            if center[0]>=350 and player.rect.right < windowWidth:
                player.rect.centerx += player.velocity
            elif center[0]<=250 and player.rect.left > 0:

                player.rect.centerx -= player.velocity
        cv2.line(frame, (250,0), (250,600), (0,255,0),2)
        cv2.line(frame, (350,0), (350,600), (0,255,0),2)
        cv2.imshow("Webcame",frame)
        
        ##Open CV part end
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and player.rect.left > 0:
            player.rect.centerx -= player.velocity
        if keys[pygame.K_RIGHT] and player.rect.right < windowWidth:
            player.rect.centerx += player.velocity
        ### Debug features
        if keys[pygame.K_t]:
            player.exp+=10
            print(player.powerLevel)
        if keys[pygame.K_e] and len(enemyGroup) == 0:
            enemyGroup.add(Enemy(random.randint(20,580),2,10,20,"Enemy1.png"))
        
        ### Debug feature end
        shootInterval = 10 - 2*player.update()
        if timeUntilShoot <= 0:
            player.shoot(playerBulletGroup)
            timeUntilShoot = shootInterval
        else:
            timeUntilShoot -= 1
        
        for bullet in playerBulletGroup:
            bullet.move()
            if bullet.rect.bottom <= -10:
                playerBulletGroup.remove(bullet)
        for enemy in enemyGroup:
            enemy.move()
            enemy.shoot(enemyBulletGroup,player)
            if enemy.rect.top >= windowHeight + 5:
                enemyGroup.remove(enemy)
            for bullet in playerBulletGroup:
                if enemy.rect.colliderect(bullet.rect):
                    playerBulletGroup.remove(bullet)
                    enemy.health -= bullet.power
                    if enemy.health <= 0:
                        player.exp += enemy.exp
                        enemyGroup.remove(enemy)
        for bullet in enemyBulletGroup:
            bullet.move()
            if bullet.rect.colliderect(player.rect):
                player.health-=1
                enemyBulletGroup.remove(bullet)
            if bullet.rect.centerx >= windowWidth+10 or bullet.rect.centerx <= -10:
                enemyBulletGroup.remove(bullet)
            if bullet.rect.centery >= windowHeight+10 or bullet.rect.centery <= -10:
                enemyBulletGroup.remove(bullet)
        if player.health <= 0:
            #Explosion effect and gameOver screen
            gameOver = True
        ##Drawing and updating for sprite group
        playerSpriteGroup.draw(window)
        playerBulletGroup.draw(window)
        enemyGroup.draw(window)
        enemyBulletGroup.draw(window)
        playerHP = hpFont.render("Health: "+ str(player.health),False, (255,255,255))
        print(playerHP)
        window.blit(playerHP,(20,windowHeight-50))
        
        
        pygame.display.update()
        clock.tick(gameSpeed)
    video.release()
    cv2.destroyAllWindows()
    pygame.quit()

CVShooter()
