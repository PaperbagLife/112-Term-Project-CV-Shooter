import random
from Classes import *


def levelConstructor():
    #Level1
    # EnemyList,spawnAmount,spawnWait,level (Arguments)
    #Example enemy = Enemy(3,10,20,"Enemy1.png")
    # Argument = health,exp,shootTimer,filePath,velocity,x = None
    levels = []
    enemy1 = Enemy(3,10,30,"Enemy1.png",5)
    enemy2 = Enemy(7,15,30,"Enemy2.png",2)
    lv1EnemyList = [enemy1,enemy2]
    lv1SpawnAmount = [5,3]
    lv1SpawnWait = [20,20]
    level1 = Level(lv1EnemyList,lv1SpawnAmount,lv1SpawnWait,1)
    levels.append(level1)
    
    
    
    
    return levels