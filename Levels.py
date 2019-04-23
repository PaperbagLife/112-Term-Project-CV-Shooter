import random
from Classes import *


def levelConstructor():
    #Level1
    # EnemyList,spawnAmount,level (Arguments)
    #Example enemy = Enemy(3,10,20,"Enemy1.png")
    # Argument = health,exp,shootTimer,filePath,velocity,x = None
    levels = []
    enemy1 = ("Normal",3,10,50,"Enemy1.png",1.5)
    enemy2 = ("Normal",5,15,40,"Enemy2.png",2)
    enemy3 = ("Moving",7,15,50,"Enemy3.png",1.5)
    miniBoss1 = ("MiniBoss", 20, 100, 30,"miniBoss.png",3)
    teamEnemy1 = ("Team",None)
    teamEnemy2 = ("Team",None)
    teamEnemy3 = ("Team",None)
    teamEnemy4 = ("Team",None)
    boss = ("Boss",3)
    lv1EnemyList = [enemy1,enemy3,enemy2,enemy3,enemy1,enemy2,enemy2]
    lv1SpawnWait = [100,100,100,100,200,200,400]
    lv1SpawnAmount = [1,2,3,1,1,1,1] 
    assert(len(lv1SpawnWait) == len(lv1EnemyList) == len(lv1SpawnAmount))
    level1 = Level(lv1EnemyList,lv1SpawnAmount,lv1SpawnWait,1)
    levels.append(level1)
    ##Level 2 Miniboss
    lv2EnemyList = [miniBoss1]
    lv2SpawnWait = [200]
    lv2SpawnAmount = [1]
    level2 = Level(lv2EnemyList,lv2SpawnAmount,lv2SpawnWait,2)
    levels.append(level2)
    ##Level 3 Team enemies
    
    lv3EnemyList = [teamEnemy1,teamEnemy2,teamEnemy3,teamEnemy4]
    lv3SpawnWait = [60,60,60,200]
    lv3SpawnAmount = [1,1,1,1]
    level3 = Level(lv3EnemyList,lv3SpawnAmount,lv3SpawnWait,3)
    levels.append(level3)
    ## Level 4: Final Boss
    lv4EnemyList = [boss]
    lv4SpawnWait = [100]
    lv4SpawnAmount = [1]
    level4 = Level(lv4EnemyList,lv4SpawnAmount,lv4SpawnWait,4)
    levels.append(level4)
    return levels