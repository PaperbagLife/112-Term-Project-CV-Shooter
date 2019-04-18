import random
from Classes import *


def levelConstructor():
    #Level1
    # EnemyList,spawnAmount,level (Arguments)
    #Example enemy = Enemy(3,10,20,"Enemy1.png")
    # Argument = health,exp,shootTimer,filePath,velocity,x = None
    levels = []
    enemy1 = ("Normal",3,10,50,"Enemy1.png",1.5)
    enemy2 = ("Normal",7,15,40,"Enemy2.png",1)
    enemy3 = ("Moving",7,15,50,"Enemy3.png",1.5)
    miniBoss1 = ("MiniBoss", 500, 100, 30,"miniBoss.png",3)
    lv1EnemyList = [enemy1,enemy3,enemy2,enemy3,enemy1,enemy2,enemy2]
    lv1SpawnWait = [100,100,100,100,200,200,600]
    lv1SpawnAmount = [1,2,3,1,1,1,1] 
    assert(len(lv1SpawnWait) == len(lv1EnemyList) == len(lv1SpawnAmount))
    level1 = Level(lv1EnemyList,lv1SpawnAmount,lv1SpawnWait,1)
    levels.append(level1)
    ##Level 2
    lv2EnemyList = [miniBoss1]
    lv2SpawnWait = [10]
    lv2SpawnAmount = [1]
    level2 = Level(lv2EnemyList,lv2SpawnAmount,lv2SpawnWait,2)
    levels.append(level2)
    
    return levels