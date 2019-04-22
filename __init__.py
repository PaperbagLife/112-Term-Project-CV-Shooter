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



def spawn(enemyGroup,levels,curLevelProgress,teamEnemyGroup):
    level = curLevelProgress[0]
    curLevel = levels[level-1]
    levelProgress = curLevelProgress[1]
    #Level is the level object, progress is an interger for indexing into list
    
        #Spawn for the last time and return level += 1, set progress to 0
    numSpawn = curLevel.spawnAmount[levelProgress]
    for i in range(numSpawn):

        enemySpec = curLevel.enemyList[levelProgress]
        enemyType = enemySpec[0]
        if enemyType == "Normal":
            curEnemy = Enemy(enemySpec[1],enemySpec[2],enemySpec[3],enemySpec[4],enemySpec[5],
                                    random.randint(i*windowWidth/numSpawn,(i+1)*windowWidth/numSpawn))
            enemyGroup.add(curEnemy)
        elif enemyType == "Moving":
            curEnemy = MoveEnemy(enemySpec[1],enemySpec[2],enemySpec[3],enemySpec[4],enemySpec[5],
                                random.randint(i*(windowWidth-100)/numSpawn+50,
                                                    (i+1)*(windowWidth-100)/numSpawn)-50)
            enemyGroup.add(curEnemy)
        elif enemyType == "MiniBoss":
            curEnemy = MiniBoss1(enemySpec[1],enemySpec[2],enemySpec[3],enemySpec[4],enemySpec[5])
            enemyGroup.add(curEnemy)
        elif enemyType == "Team":
            curEnemy = TeamEnemy(enemySpec[1])
            teamEnemyGroup.add(curEnemy)
            #TODO: curEnemy = Team.... etc 
    if levelProgress == len(curLevel.enemyList)-1:
        return (curLevel.spawnWait[levelProgress],(level+1,0))
    else:
        return (curLevel.spawnWait[levelProgress],(level,levelProgress+1))
        
def spawnPowerUp(player,powerUpGroup,enemyPos):
    powerUpType = random.choice(["repair"])
    if powerUpType == "repair":
        repair = Repair(enemyPos[0],enemyPos[1])
        powerUpGroup.add(repair)
    
def explode(x,y,scale,explosionGroup):
    curExplosion = Explosion(x,y,scale)
    explosionGroup.add(curExplosion)

###Main game
def titleScreen():
    bgGroup = pygame.sprite.Group()
    bgGroup.add(Background("TitleScreen.png"))
    buttonGroup = pygame.sprite.Group()
    buttonGroup.add(Button(windowWidth//2, windowHeight//2,
                "StartGame.png","StartGame2.png",CVShooter))
    buttonGroup.add(Button(windowWidth//2,windowHeight//2 + 100,"Tutorial.png","Tutorial2.png",tutorial))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        for button in buttonGroup:
            button.update(mouse,click)
        window.fill((0,0,0))
        bgGroup.draw(window)
        buttonGroup.draw(window)
        pygame.display.update()
def winScreen():
    bgGroup = pygame.sprite.Group()
    bgGroup.add(Background("WinScreen.png"))
    buttonGroup = pygame.sprite.Group()
    buttonGroup.add(Button(windowWidth//2, windowHeight//2 + 100,
                "Restart.png","Restart2.png",CVShooter))
    buttonGroup.add(Button(windowWidth//2,windowHeight//2 + 200,"ReturnToTitle.png","ReturnToTitle2.png",titleScreen))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        for button in buttonGroup:
            button.update(mouse,click)
        window.fill((0,0,0))
        bgGroup.draw(window)
        buttonGroup.draw(window)
        pygame.display.update()
def loseScreen():
    bgGroup = pygame.sprite.Group()
    bgGroup.add(Background("LoseScreen.png"))
    buttonGroup = pygame.sprite.Group()
    buttonGroup.add(Button(windowWidth//2, windowHeight//2 + 100,
                "Restart.png","Restart2.png",CVShooter))
    buttonGroup.add(Button(windowWidth//2,windowHeight//2 + 200,"ReturnToTitle.png","ReturnToTitle2.png",titleScreen))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        for button in buttonGroup:
            button.update(mouse,click)
        window.fill((0,0,0))
        bgGroup.draw(window)
        buttonGroup.draw(window)
        pygame.display.update()
def tutorial():
    print("start tutorial")
    video = cv2.VideoCapture(0)
    teaching = True
    
    playerSpriteGroup = pygame.sprite.Group() 
    player = Player(windowWidth//2,windowHeight - 80)
    playerSpriteGroup.add(player)
    backgroundGroup = pygame.sprite.Group()
    background = Background("TutorialBG.png")
    backgroundGroup.add(background)
    while teaching:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                video.release()
                cv2.destroyAllWindows()
                return
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
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, 'Left', (50,225), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, 'Left-Up', (25,100), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, 'Right', (500,225), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, 'Right-Up', (400,100), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, 'Right-Down', (400,350), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, 'Left-Up', (25,350), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, 'Up', (275,100), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, 'Down', (265,400), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.imshow("Webcame",frame)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            teaching = False
        window.fill((0,0,0))
        backgroundGroup.draw(window)
        playerSpriteGroup.draw(window)
        
        
        pygame.display.update()
    video.release()
    cv2.destroyAllWindows()
    return

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
    explosionGroup = pygame.sprite.Group()
    powerUpGroup = pygame.sprite.Group()
    backgroundGroup = pygame.sprite.Group()
    teamEnemyGroup = pygame.sprite.Group()
    teamEnemyModeOfAction = ["Straight","Right","Left"]
    
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
    
    endTimer = 50
    testCounter = 500
    testTimer = time.time()
    levelEnd = False
### Main Game
    while endTimer >= 0:
        background.move()
        spawnInterval -= 1
        
        ##handles spawning here
        if (spawnInterval <= 0) and curLevelProgress[0] <= len(levels) and not levelEnd:
            levelBefore = curLevelProgress[0]
            spawnInterval,curLevelProgress = spawn(enemyGroup,levels,curLevelProgress,teamEnemyGroup)
            
            if curLevelProgress[0] > levelBefore:
                levelEnd = True
        elif curLevelProgress[0] > len(levels) and len(enemyGroup) == 0 and len(teamEnemyGroup) == 0:
            print("Currently ended")
            video.release()
            cv2.destroyAllWindows()
            winScreen()
            return
        if (len(enemyGroup) + len(teamEnemyGroup)) == 0:
            levelEnd = False
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
        if keys[pygame.K_UP]:
            player.rect.centery -= player.velocity
        if keys[pygame.K_DOWN]:
            player.rect.centery += player.velocity
        ### Debug features
        if keys[pygame.K_t]:
            player.exp+=10
            print(player.powerLevel)
        if keys[pygame.K_e]:
            enemyGroup.add(Enemy(3,10,20,"Enemy1.png",5))
        if keys[pygame.K_d]:
            player.health -= 1
        if keys[pygame.K_2]:
            curLevelProgress = (3,0)
        if keys[pygame.K_h]:
            player.health += 1
        ### Debug feature end
        player.update(enemyBulletGroup)
        shootInterval = 15 - player.powerLevel
        if timeUntilShoot <= 0 and not gameOver:
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
                        explode(enemy.rect.centerx,enemy.rect.centery,enemy.rect.size,explosionGroup)
                        enemyGroup.remove(enemy)
            if enemy.rect.colliderect(player.rect):
                if player.invincible == False:
                    player.health-=1
                    player.invincible = True
                    player.invincibleTimer = 50
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
                    player.health += int(3 + player.performance//15)
                powerUpGroup.remove(powerUp)
        teamCounter = 0
        #teamEnemyModeOfAction = ["Straight","Right","Left"]
        for teamEnemy in teamEnemyGroup:
            memberLeft = len(teamEnemyGroup)
            if memberLeft <= 2:
                teamEnemy.shootInterval = 10
            teamEnemy.move()
            teamEnemy.shoot(enemyBulletGroup,teamEnemyModeOfAction[teamCounter%3],player)
            teamCounter += 1
            for bullet in playerBulletGroup:
                if teamEnemy.rect.colliderect(bullet.rect):
                    playerBulletGroup.remove(bullet)
                    teamEnemy.health -= bullet.power
                    if teamEnemy.health <= 0:
                        player.exp += teamEnemy.exp
                        if (random.randint(int(player.performance),100) >= 80):
                            spawnPowerUp(player,powerUpGroup,teamEnemy.rect.center)
                        explode(teamEnemy.rect.centerx,teamEnemy.rect.centery,teamEnemy.rect.size,explosionGroup)
                        teamEnemyGroup.remove(teamEnemy)
        for explosion in explosionGroup:
            if explosion.update():
                explosionGroup.remove(explosion)
        if player.health <= 0:
            #Explosion effect and gameOver screen
            if not gameOver:
                explode(player.rect.centerx,player.rect.centery,player.rect.size,explosionGroup)
            gameOver = True
            playerSpriteGroup.remove(player)
            endTimer -= 1
        ##Drawing and updating for sprite group
        backgroundGroup.draw(window)
        playerSpriteGroup.draw(window)
        playerBulletGroup.draw(window)
        enemyGroup.draw(window)
        teamEnemyGroup.draw(window)
        enemyBulletGroup.draw(window)
        powerUpGroup.draw(window)
        explosionGroup.draw(window)
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
    loseScreen()
    return

titleScreen()