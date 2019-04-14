import pygame
import os
import sys
import random

windowWidth = 600
windowHeight = 800
window = pygame.display.set_mode((windowWidth,windowHeight))
clock = pygame.time.Clock()
gameSpeed = 30


class Player(pygame.sprite.Sprite):
    #player ship, has a powerLevel for the bullets, which is leveled up through
    #gaining exp
    def __init__(self,x,y,health=50,powerLevel=1,exp=0):
        pygame.sprite.Sprite.__init__(self)
        self.health = health
        self.powerLevel = powerLevel
        self.exp = exp
        self.image = pygame.image.load(os.path.join('Assets','Player','player.png')).convert()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.velocity = 10
    def update(self):
        if self.exp >= 100 and self.powerLevel < 3:
            self.powerLevel += 1
            self.exp = 0
    def shoot(self):
        pass
class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self,x,y,filePath):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('Assets','Bullets',filePath)).convert()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.velocity = 30
        self.direction = direction
    def move(self):
        self.rect.centery -= self.velocity
def CVShooter():
    score = 0
    gameOver = False
    
    
    #Sprite Group for drawing player only
    playerSpriteGroup = pygame.sprite.Group() 
    player = Player(windowWidth//2,windowHeight - 80)
    playerSpriteGroup.add(player)
    
    
    while not gameOver:
        
        window.fill((0,0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and player.rect.left > 0:
            player.rect.centerx -= player.velocity
        if keys[pygame.K_RIGHT] and player.rect.right < windowWidth:
            player.rect.centerx += player.velocity
    
    
    
    
    
    
        playerSpriteGroup.draw(window)
        pygame.display.update()
        clock.tick(gameSpeed)

CVShooter()