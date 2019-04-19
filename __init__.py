import pygame
import os
import sys
import random
import cv2
import time
import numpy as np
import imutils
import copy
from Classes import *
from Levels import levelConstructor

windowWidth = 600
windowHeight = 800
window = pygame.display.set_mode((windowWidth,windowHeight))
clock = pygame.time.Clock()
gameSpeed = 30


pygame.font.init()
hpFont = pygame.font.SysFont('Comic Sans MS', 30)

def spawn(enemyGroup,levels,curLevelProgress):
    level = curLevelProgress[0]
    curLevel = levels[level-1]
    levelProgress = curLevelProgress[1]
    #Level is the level object, progress is an interger for indexing into list
    if levelProgress == len(curLevel.enemyList)-1:
        #Spawn for the last time and return level += 1, set progress to 0
        numSpawn = curLevel.spawnAmount[levelProgress]
        for i in range(numSpawn):
            enemySpec = curLevel.enemyList[levelProgress]
            enemyType = enemySpec[0]
            if enemyType == "Normal":
                curEnemy = Enemy(enemySpec[1],enemySpec[2],enemySpec[3],enemySpec[4],enemySpec[5],
                                        random.randint(i*windowWidth/numSpawn,(i+1)*windowWidth/numSpawn))
            elif enemyType == "Moving":
                curEnemy = MoveEnemy(enemySpec[1],enemySpec[2],enemySpec[3],enemySpec[4],enemySpec[5],
                                    random.randint(i*(windowWidth-100)/numSpawn+50,
                                                        (i+1)*(windowWidth-100)/numSpawn)-50)
            elif enemyType == "MiniBoss":
                curEnemy = MiniBoss1(enemySpec[1],enemySpec[2],enemySpec[3],enemySpec[4],enemySpec[5])
            enemyGroup.add(curEnemy)
        print("end of level")
        return (curLevel.spawnWait[levelProgress],(level+1,0))
    else:
        #Spawn and increment progress by 1
        numSpawn = curLevel.spawnAmount[levelProgress]
        for i in range(numSpawn):
            enemySpec = curLevel.enemyList[levelProgress]
            enemyType = enemySpec[0]
            if enemyType == "Normal":
                curEnemy = Enemy(enemySpec[1],enemySpec[2],enemySpec[3],enemySpec[4],enemySpec[5],
                                        random.randint(i*windowWidth/numSpawn,(i+1)*windowWidth/numSpawn))
            elif enemyType == "Moving":
                curEnemy = MoveEnemy(enemySpec[1],enemySpec[2],enemySpec[3],enemySpec[4],enemySpec[5],
                                    random.randint(i*(windowWidth-100)/numSpawn+50,
                                                                (i+1)*(windowWidth-100)/numSpawn)-50)
            elif enemyType == "MiniBoss":
                curEnemy = MiniBoss1(enemySpec[1],enemySpec[2],enemySpec[3],enemySpec[4],enemySpec[5])
            enemyGroup.add(curEnemy)
        return (curLevel.spawnWait[levelProgress],(level,levelProgress+1))
        
def spawnPowerUp(player,powerUpGroup,enemyPos):
    powerUpType = random.choice(["repair"])
    if powerUpType == "repair":
        repair = Repair(enemyPos[0],enemyPos[1])
        powerUpGroup.add(repair)
    
    
    
###Main game
def titleScreen():
    bgGroup = pygame.sprite.Group()
    bgGroup.add(Background("TitleScreen.png"))
    bgGroup.draw(window)
    buttonGroup = pygame.sprite.Group()
    buttonGroup.add(Button(windowWidth//2, windowHeight//2,"StartGame.png","StartGame2.png",CVShooter))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        for button in buttonGroup:
            button.update(mouse,click)
        buttonGroup.draw(window)
        pygame.display.update()
        
def tutorial():
    pass
        
        

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
    powerUpGroup = pygame.sprite.Group()
    backgroundGroup = pygame.sprite.Group()
    
    background = Background("Background.png")
    backgroundGroup.add(background)
    
    
    shootInterval = 10
    timeUntilShoot = shootInterval
    ## Wave control
    
    
    spawnInterval = 20
    # A list of Level Objects
    levels = levelConstructor()
    #This is a tuple of current level and the progress of the level.
    curLevelProgress = (1,0)
    
    
    #OpenCV setup
    video = cv2.VideoCapture(0)
    
    
    testCounter = 500
    testTimer = time.time()
    
### Main Game
    while not gameOver:
        background.move()
        spawnInterval -= 1
        ##handles spawning here
        if (spawnInterval <= 0) and (curLevelProgress[0] <= len(levels)):
            spawnInterval,curLevelProgress = spawn(enemyGroup,levels,curLevelProgress)
        elif curLevelProgress[0] > len(levels) and len(enemyGroup) == 0:
            print("Currently ended")
            video.release()
            cv2.destroyAllWindows()
            pygame.quit()
            return
        window.fill((0,0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                video.release()
                cv2.destroyAllWindows()
                return
        ##Open CV part Start
        ##Code adapted from https://docs.opencv.org/3.4/df/d9d/tutorial_py_colorspaces.html
        ##For changing color space and masking
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
        ## Finding contour, code adapted from https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
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
        ##Control player with opencv, original code
        if center != None:
            if center[0]>=350 and player.rect.right < windowWidth:
                player.rect.centerx += player.velocity
            elif center[0]<=250 and player.rect.left > 0:
                player.rect.centerx -= player.velocity
            if center[1] >= 250 and player.rect.bottom <= windowHeight:
                player.rect.centery += player.velocity
            elif center[1] <= 175 and player.rect.top >= 0:
                player.rect.centery -= player.velocity
        cv2.line(frame, (250,0), (250,600), (0,255,0),2)
        cv2.line(frame, (350,0), (350,600), (0,255,0),2)
        cv2.line(frame, (0,250), (600,250), (0,255,0),2)
        cv2.line(frame, (0,175), (600,175), (0,255,0),2)
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
            enemyGroup.add(Enemy(3,10,20,"Enemy1.png",5))
        
        ### Debug feature end
        player.update(enemyBulletGroup)
        shootInterval = 10 - 2*player.powerLevel
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
            enemy.update(player.performance)
            enemy.shoot(enemyBulletGroup,player)
            if enemy.rect.top >= windowHeight + 5:
                enemyGroup.remove(enemy)
            for bullet in playerBulletGroup:
                if enemy.rect.colliderect(bullet.rect):
                    playerBulletGroup.remove(bullet)
                    enemy.health -= bullet.power
                    if enemy.health <= 0:
                        player.exp += enemy.exp
                        if (random.randint(int(player.performance),100) >= 80):
                            spawnPowerUp(player,powerUpGroup,enemy.rect.center)
                        enemyGroup.remove(enemy)
            if enemy.rect.colliderect(player.rect):
                if player.invincible == False:
                    player.health-=1
                    player.invincible = True
                    player.invincibleTimer = 50

        #TODO: Can implement increased drop rate for struggling players here
            
        for bullet in enemyBulletGroup:
            bullet.move()
            if bullet.rect.colliderect(player.rect):
                if player.invincible == False:
                    player.health-=1
                    player.invincible = True
                    player.invincibleTimer = 50
                enemyBulletGroup.remove(bullet)
            if bullet.rect.centerx >= windowWidth+10 or bullet.rect.centerx <= -10:
                enemyBulletGroup.remove(bullet)
            if bullet.rect.centery >= windowHeight+10 or bullet.rect.centery <= -10:
                enemyBulletGroup.remove(bullet)
        for powerUp in powerUpGroup:
            powerUp.move()
            if powerUp.rect.colliderect(player.rect):
                if isinstance(powerUp,Repair):
                    player.health += int(3 + player.performance//10)
                powerUpGroup.remove(powerUp)
        if player.health <= 0:
            #Explosion effect and gameOver screen
            gameOver = True
        ##Drawing and updating for sprite group
        backgroundGroup.draw(window)
        playerSpriteGroup.draw(window)
        playerBulletGroup.draw(window)
        enemyGroup.draw(window)
        enemyBulletGroup.draw(window)
        powerUpGroup.draw(window)
        playerHP = hpFont.render("Health: "+ str(player.health),False, (255,255,255))
        window.blit(playerHP,(20,windowHeight-50))
        if player.powerLevel == 3:
            playerEXP = hpFont.render("Max EXP",False, (255,255,255))
        else:
            playerEXP = hpFont.render("EXP: "+ str(player.exp) + "/100",False, (255,255,255))
        window.blit(playerEXP,(420,windowHeight-50))
        pygame.display.update()
        clock.tick(gameSpeed)
    video.release()
    cv2.destroyAllWindows()
    pygame.quit()
    return

titleScreen()
