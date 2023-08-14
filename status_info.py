from termcolor import colored
from chessInterface import chessInterface
from statusInterface import statusInterface
from copy import deepcopy
# from chess_info import *

statusDictExample= {
'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
'blood_draining':None, 'sand_poisoned': None,
'armor_change':None, 'attack_change':None, 'attack_interval_change':None}

##################################################
#### 棋子状态
##################################################


# TODO
class moving(statusInterface):
    def __init__(self,
                 currentTime: int,
                 statusOwner: chessInterface,
                 newPosition:list[int],
                 ) -> None:
        super().__init__(statusName = "移动",
                         currentTime = currentTime,
                         statusDuration=0.3,
                         statusType="moving")
        self.statusOwner = statusOwner
        self.activate(currentTime)
        print(f"{currentTime/100}   {self.statusOwner}开始从{self.statusOwner.position}移动到{newPosition} ")

    def activate(self, currentTime):
        ''' 如果这个效果持续时间结束 就把这个状态从状态栏珊处移除 否则按照状态对棋子的数值积累 造成影响'''
        if currentTime > self.statusEnd:
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束")
            self.statusOwner.statusDict['moving'] = None
            return False
        else:
            # 移动，跳过 本次攻击/移动判定
            self.statusOwner.attack_counter = 0
            return True
# 变羊
class hexed(statusInterface):
    def __init__(self, currentTime: int,
                 statusOwner: chessInterface) -> None:
        super().__init__(statusName = "变羊",
                         currentTime = currentTime,
                         statusDuration=2.0, statusType="disable")
        self.statusOwner = statusOwner
        print(f"{currentTime/100}   {self.statusOwner}被【{self}】了！")

    def activate(self, currentTime):
        ''' 如果这个效果持续时间结束 就把这个状态从状态栏珊处移除 否则按照状态对棋子的数值积累 造成影响'''
        if currentTime > self.statusEnd:
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束")
            self.statusOwner.statusDict['hexed'] = None
            return False
        else:
            # 仍然被羊，跳过 本次攻击/移动判定
            self.statusOwner.attack_counter = 0
            return True

# 眩晕
class stunned(statusInterface):
    def __init__(self, currentTime: int,
                 statusDuration: float,
                 statusOwner: chessInterface) -> None:
        super().__init__(statusName = "眩晕",
                         currentTime = currentTime,
                         statusDuration = statusDuration,
                         statusType="disable")
        self.statusOwner = statusOwner
        print(f"{currentTime/100}   {self.statusOwner}被【{self}】了！")

    def activate(self, currentTime: float) -> bool:
        if currentTime > self.statusEnd:
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束")
            self.statusOwner.statusDict['stunned'] = None
            return False
        else:
            # 仍然被眩晕，跳过 本次攻击/移动判定
            self.statusOwner.attack_counter = 0
            return True

# 缴械
class disarmed(statusInterface):
    def __init__(self, currentTime: int,
                 statusDuration: float,
                 statusOwner: chessInterface) -> None:
        super().__init__(statusName = "缴械",
                         currentTime = currentTime,
                         statusDuration=statusDuration,
                         statusType = "disable")
        self.statusOwner = statusOwner
    def activate(self, currentTime: float) -> bool:
        if currentTime > self.statusEnd:
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束")
            self.statusOwner.statusDict['disarmed'] = None
            return False
        else:
            # 仍然被缴械，跳过 本次攻击， 移动判定继续
            self.statusOwner.attack_counter = 0
            return True

# 嘲讽
class taunted(statusInterface):
    def __init__(self, currentTime: int,
                 statusDuration: float,
                 statusOwner: chessInterface) -> None:
        super().__init__(statusName = "沉默",
                         currentTime = currentTime,
                         statusDuration=statusDuration,
                         statusType = "disable")
        self.statusOwner = statusOwner
    def activate(self, currentTime: float) -> bool:
        if currentTime > self.statusEnd:
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束")
            self.statusOwner.statusDict['taunted'] = None
            return False
        else:
            # 仍然被嘲讽，跳过 移动 和 技能判定， 攻击判定继续
            self.statusOwner.cd_counter -= 5
            return True

# 沉默
class silenced(statusInterface):
    def __init__(self, currentTime: int,
                 statusDuration: float,
                 statusOwner: chessInterface) -> None:
        super().__init__(statusName = "沉默",
                         currentTime = currentTime,
                         statusDuration=statusDuration,
                         statusType = "disable")
        self.statusOwner = statusOwner
    def activate(self, currentTime: float) -> bool:
        if currentTime > self.statusEnd:
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束")
            self.statusOwner.statusDict['silenced'] = None
            return False
        else:
            # 仍然被沉默，跳过 技能判定，攻击判定继续
            self.statusOwner.cd_counter -= 5
            return True

# 破坏 （被动无效化）
class broken(statusInterface):
    def __init__(self, currentTime: int,
                 statusDuration: float,
                 statusOwner: chessInterface) -> None:
        super().__init__(statusName = "破坏",
                         currentTime = currentTime,
                         statusDuration=statusDuration,
                         statusType = "disable")
        self.statusOwner = statusOwner
    def activate(self, currentTime: float) -> bool:
        if currentTime > self.statusEnd:
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束")
            self.statusOwner.statusDict['broken'] = None
            return False
        else:
            # 仍然被缴械，如果有被动技能，跳过被动技能判定
            if self.statusOwner.skill.type == 'passive':
                self.statusOwner.cd_counter -= 5
            return True

class attack_interval_change(statusInterface):
    def __init__(self, currentTime: int,
                 statusDuration: float,
                 statusOwner: chessInterface,
                 changeRatio: float) -> None:
        super().__init__(statusName = "攻击间隔变化",
                         currentTime = currentTime,
                         statusDuration=statusDuration,
                         statusType = "buff/debuff")
        self.statusOwner = statusOwner
        self.originalAttackInterval = deepcopy(self.statusOwner.attack_interval)
        currentAttackInterval =1/(1/self.statusOwner.attack_interval * (1+changeRatio))
        print(f"    {statusOwner} 攻击速度提升{changeRatio*100}%, 原攻击间隔{self.statusOwner.attack_interval/100}, 现攻击间隔{currentAttackInterval/100}")
        self.statusOwner.attack_interval = currentAttackInterval
        

    def activate(self, currentTime: float) -> bool:
        if currentTime > self.statusEnd:
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束, 攻击间隔回复初始值{self.originalAttackInterval}")
            self.statusOwner.attack_interval = self.originalAttackInterval
            self.statusOwner.statusDict['attack_interval_change'] = None
            return False
        else:
            # 减小/加大攻击间隔 攻击间隔=1/攻速
            return True

class summoned(statusInterface):
    def __init__(self,
                 currentTime: int,
                 statusDuration: float,
                 statusOwner: chessInterface) -> None:
        super().__init__(statusName = "被召唤",
                         currentTime = currentTime,
                         statusDuration = statusDuration,
                         statusType = "buff/debuff")
        self.statusOwner = statusOwner

    def activate(self, currentTime: float):
        if currentTime > self.statusEnd:
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束, {self.statusOwner}死掉")
            self.statusOwner.health = -1
            self.statusOwner.check_death()

# 反伤
class dispersion_status(statusInterface):
    def __init__(self,
                 currentTime: int,
                 statusOwner: chessInterface) -> None:
        super().__init__(statusName= "反伤",
                 statusDuration = 2.5,
                 statusType = "special",
                 currentTime=currentTime
                 )
        self.statusOwner = statusOwner
        print(f"{currentTime/100}   {self.statusOwner}对自己施加【{self}】状态")

    def activate(self, currentTime: int,
                 target: chessInterface = None,
                 damage:float = 0) -> bool:
        ''' 在棋子收到伤害时触发, 如果时间到了 return True 并且关掉状态'''
        if currentTime > self.statusEnd:
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束")
            self.statusOwner.statusDict['dispersion_status'] = None
            return False
        else:
            if target is not None and damage > 0:
                damage = damage * self.statusOwner.skill.returnRate
                # 当海胆收到伤害时 反弹伤害*1.5
                print(f'{currentTime/100}  {self.statusOwner} 触发了{self},')
                self.statusOwner.deal_damage_to(opponent=target,
                                    damage=damage,
                                    currentTime=currentTime)
                print(f"     <{self.statusOwner}> *{self}*了<{target}>, 造成了{colored(damage,'cyan')}点伤害，<{target}>生命值还剩:{colored(target.health,'green')} / {target.maxHP}") 
            return True

# 沙漠剧毒
class sand_poisoned(statusInterface):
    def __init__(self,
                 currentTime: int,
                 statusOwner: chessInterface,
                 caster: chessInterface,
                 damageInterval: int = 100 # 秒 * 100， 以防用float 不能用% 来判定
                 ) -> None:
        super().__init__(statusName = "沙漠剧毒",
                         currentTime = currentTime,
                         statusDuration=5.0,
                         statusType="damage")
        self.caster = caster
        self.damageInterval = damageInterval
        self.statusOwner = statusOwner
        self.damage = self.caster.skill.damage
        self.damageInterval = 100
        print(f"{currentTime/100}   {self.statusOwner}被【{self}】了")

    def activate(self, currentTime):
        ''' 如果这个效果持续时间结束 就把这个状态从状态栏珊处移除 否则按照状态对棋子的数值积累 造成影响'''
        if currentTime > self.statusEnd:
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束")
            self.statusOwner.statusDict['sand_poisoned'] = None
            return False
        else:
            # 仍然被毒，目标掉血
            # 如果触发间隔到了就掉血
            # print(self.statusEnd, currentTime)
            if (self.statusEnd - currentTime)% self.damageInterval == 0: # 触发间隔 1 秒
                print(f"{currentTime/100}   {self.statusOwner}收到【{self}】的{colored(str(self.damage),'cyan')}点伤害，生命值还剩:{colored(self.statusOwner.health, 'green')} / {self.statusOwner.maxHP}")
                self.caster.deal_damage_to(self.statusOwner,
                                           damage = self.damage,
                                           currentTime=currentTime)
                return True
            return False

class vulnerable(statusInterface):
    def __init__(self, 
                 currentTime: int,
                 statusDuration: float,
                 amplification: float,
                 statusOwner: chessInterface) -> None:
        super().__init__(statusName = "伤害加深",
                         currentTime = currentTime,
                         statusDuration=statusDuration,
                         statusType = "debuff")
        self.statusOwner = statusOwner  
        self.amplification = amplification
        print(f"    {statusOwner} 伤害加深 {amplification}%")

    def activate(self, currentTime: float) -> bool:
        if currentTime > self.statusEnd:
            self.statusOwner.statusDict['vulnerable'] = None
            self.statusOwner.statusDict.pop('vulnerable', None)
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束")
            return False
        else:
            # print(self.statusEnd)
            return True

class frail(statusInterface):
    def __init__(self, 
                 currentTime: int,
                 statusDuration: float,
                 armorReduction: int,
                 statusOwner: chessInterface) -> None:
        super().__init__(statusName = "护甲降低",
                         currentTime = currentTime,
                         statusDuration=statusDuration,
                         statusType = "debuff")
        self.statusOwner = statusOwner  
        self.armorReduction = armorReduction
        print(f"    {statusOwner} 护甲降低{armorReduction}, 原护甲{self.statusOwner.armor}, 现护甲{statusOwner.armor-armorReduction}")
        self.statusOwner.armor -= armorReduction

    def activate(self, currentTime: float) -> bool:
        if currentTime > self.statusEnd:
            self.statusOwner.armor += self.armorReduction
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束, 护甲恢复{self.statusOwner.armor}")
            self.statusOwner.statusDict['frail'] = None
            return False
        else:
            # print(self.statusEnd)
            return True

class bleeding(statusInterface):
    def __init__(self, 
                 currentTime: int, 
                 statusDuration: float, 
                 statusOwner: chessInterface,
                 caster:chessInterface) -> None:
        super().__init__(statusName = "留学",
                         currentTime = currentTime,
                         statusDuration = statusDuration,
                         statusType = "debuff")
        self.statusOwner = statusOwner  
        self.caster = caster
        self.instanceDamage = 10.0
    def activate(self, currentTime: float) -> bool:
        if currentTime > self.statusEnd:
            self.statusOwner.statusDict['bleeding'] = None
            print(f"{currentTime/100}   {self.statusOwner}的状态【{self}】结束")
            return False
        else:
            self.caster.deal_damage_to(self.statusOwner, self.instanceDamage, currentTime)
            print(f"{currentTime/100}   {self.statusOwner}【{self}】神志不清, <{self.statusOwner}>生命值还剩:{colored(self.statusOwner.health,'green')} / {self.statusOwner.maxHP}")
            return True





