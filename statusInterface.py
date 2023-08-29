from termcolor import colored
class statusInterface:
    '''
    棋子状态接口, 
    需要重写activate 方法
    
    子状态有以下几种情况: 
    disable: silenced, disarmed, stunned, hexed
    damage: blood_draining, poisoned, taunted
    buff/debuff: armor_change, attack_change, attack_interval_change
    special status:
        瓢虫的飞
        独角仙的复活
        海胆的伤害反弹
    '''
    def __init__(self,
                 statusName: str,
                 currentTime:int,
                 statusDuration:float,
                 statusType:str) -> None:
        # currentTime is represented in hundreds of a second, so integer
        statusDuration = int (100* statusDuration)
        self.statusEnd = currentTime + statusDuration
        self.statusType = statusType
        self.statusName = statusName
        self.statusDuration = statusDuration # 不知道有没有用目前
    def __repr__(self) -> str:
        return f"{colored(self.statusName, 'cyan')}"

    def activate(self, currentTime: float) -> bool:
        ''' activate the status for the status owner'''
        print(f"{self.statusName} implement the activate method!!!!")
        pass
    def addBuff(self, currentTime:int, duration:float):
        print(f"{currentTime/100}    {self.statusOwner}又被{self.statusName}了")
        self.statusEnd += int(duration * 100)
