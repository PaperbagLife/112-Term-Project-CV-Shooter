class Player(object):
    #player ship, has a powerLevel for the bullets, which is leveled up through
    #gaining exp
    def __init__(self,x,y,health=50,powerLevel=1,exp=0):
        self.x = x
        self.y = y
        self.health = health
        self.powerLevel = powerLevel
        self.exp = 