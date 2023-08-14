from __future__ import annotations
from termcolor import colored
from skillInterface import skillInterface
from statusInterface import statusInterface
from chessInterface import chessInterface
from copy import deepcopy
from numpy.random import random, randint
from math import dist, floor

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
            # 仍然被羊，跳过 本次攻击/移动判定
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
                 statusOwner: sea_hedgehog) -> None:
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
                 caster:scorpion,
                 damageInterval: int = 100 # 秒 * 100， 以防用float 不能用% 来判定
                 ) -> None:
        super().__init__(statusName = "沙漠剧毒",
                         currentTime = currentTime,
                         statusDuration=5.0,
                         statusType="damage")
        self.caster = caster
        self.damageInterval = damageInterval
        self.statusOwner = statusOwner
        self.damage = caster.skill.damage
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









##################################################
##### 棋子技能以及 单位信息
##################################################


# 卡
# 1星卡
############################################################################################################
# 兔子
class spit(skillInterface):
    # spit saliva 
    def __init__(self) -> None:
        super().__init__(skillName = "吐口水",
                         cd = 0.1,
                         type = "active",
                         description= f"吐口水,变得快乐")
        self.duration = 0
    
    def cast(self,currentTime: int, caster: chessInterface, target: chessInterface):
        targetList = []
        for (uniqueID, chess) in caster.allChessDict.items():
            if chess.team != caster.team:
                targetList.append(chess)
        target = targetList[randint(0, len(targetList))] 
        print(f"{currentTime/100}   {caster}对{target}使用了*{self}*,{target}心情很差")
  
class rabbit(chessInterface):
    def __init__(self,position= [3,3]):
        super().__init__(chessName = "兔子",
                         id=1,
                         race = "mammal",
                         star = 1,
                         attack = 21,
                         attack_interval=0.9,
                         attack_range = 1,
                         armor=9,
                         health=318,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
############################################################################################################
# 蚂蚁
# 技能：三个臭皮匠
class threeStinkers(skillInterface):
    # spit saliva 
    ant_count = 0
    activate = False
    def __init__(self, attack, armor, health, maxHP, threshold = 5) -> None: 
        super().__init__(skillName = "三个臭皮匠",
                         cd = 0,
                         type = "active",
                         description= f"人多尼酿大")
        # self.duration = 0
        # 不能用target，这样的话会在一个蚂蚁死掉之后其余蚂蚁属性变弱, 所以我们用一个公用的counter
        # 也不能用teamDict， 因为棋子死掉后会从teamDict 去除掉，有可能带了一个其他棋子死掉了，这样的话teamDict 中所有棋子就都是蚂蚁了
        threeStinkers.ant_count += 1
        self.attack = deepcopy(attack)
        self.armor = deepcopy(armor)
        self.health = deepcopy(health)
        self.maxHP = deepcopy(maxHP)
        self.threshold = threshold
        
        # print("三个臭皮匠",self.ant_count)

        
    def cast(self,currentTime: int, caster: chessInterface, target: chessInterface):
        if target.statusDict['broken'] is None and self.ant_count >= self.threshold:
            activate = True
            target.attack = self.attack * self.ant_count
            # target.attack_interval = 1.0 / ant_count
            target.armor = self.armor * self.ant_count
            target.health = target.health / target.maxHP * self.maxHP * self.ant_count
            target.maxHP = self.maxHP * self.ant_count
            if activate is False:
                activate = True
                print(f"{currentTime/100}   {caster}对{target}使用了*{self}*,{target}超进化了")
        elif self.ant_count < self.threshold:
            pass
        else:
            self.activate = False
            target.attack = self.attack
            # target.attack_interval = 1.0
            target.armor = self.armor
            target.health = target.health / target.maxHP * self.maxHP
            target.maxHP = self.maxHP
            print(f"{currentTime/100}   {target}收到了破坏,{target}被打回了原形")

class ant(chessInterface):
    def __init__(self,position= [3,3]):
        super().__init__(chessName = "蚂蚁",
                         id=2,
                         race = "insect",
                         star = 1,
                         attack = 20,
                         attack_interval = 1,
                         attack_range = 1,
                         armor=10,
                         health=180,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        print(self,self.maxHP)
        self.skill = threeStinkers( attack = self.attack, 
                                   armor= self.armor, 
                                   health= self.health, 
                                   maxHP=self.maxHP)

    def cast(self,currentTime: int):
        ''' bigger
        '''
        self.skill.cast(currentTime,caster = self,target=self)
        # super().cast(implemented = True)

############################################################################################################
# 小丑鱼
class littleUglyFish(chessInterface):
    def __init__(self,position= [3,3]):
        super().__init__(chessName = "小丑鱼",
                         id=3,
                         race = "marine",
                         star = 1,
                         attack = 21,
                         attack_interval=0.9,
                         attack_range = 2,
                         armor=13,
                         health=216,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

# 2星卡
# mammal
############################################################################################################
# 羊驼
class hex(skillInterface):
    # turn an enemy into a sheep for x seconds
    def __init__(self, duration = 2) -> None:
        super().__init__(skillName = "变羊",
                         cd = 5.0,
                         type = "active",
                         description= f"把对方星级最高的棋子变成羊,持续{duration}秒")
        self.duration = 2
    
    def cast(self,currentTime: int, caster: chessInterface, target: chessInterface):
        maxStar = 0
        for (chessID,chess) in caster.allChessDict.items():
            if chess.team != caster.team and chess.star >= maxStar and not chess.isDead:
                target = chess
                maxStar = chess.star
        if target is not None:
            # 如果target 不是None，说明有目标可以被羊，羊目标后进入cd
            target.statusDict['hexed'] = hexed(statusOwner=target, currentTime=currentTime)

class llama(chessInterface):
    def __init__(self,position= [3,3]):
        super().__init__(chessName = "羊驼",
                         id=4,
                         race = "mammal",
                         star = 2,
                         attack = 40,
                         attack_interval=1.1,
                         attack_range = 2,
                         armor=13,
                         health=410,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        self.skill = hex()

    def cast(self,currentTime: int):
        ''' hex an opponent based on its 星级
        return a list of id
        '''
        self.skill.cast(currentTime,caster = self,target=None)
        super().cast(implemented = True)

############################################################################################################

# 狼技能，分身
class summonWolfMinions(skillInterface):
    def __init__(self,
                 skillName: str = "召唤狼小弟",
                 cd: float = 5,
                 type: str = "active",
                 description: str = "幻影狼分身") -> None:
        super().__init__(skillName, cd, type, description)
        # self.findPosition() TODO implement this

    def cast(self, currentTime: int, caster: chessInterface, target=None):
        '''在合适的位置召唤狼兵'''
        print(f"{currentTime/100}   {caster}使用了{self}")
        placeTaken = [caster.position]
        for (id, chess) in caster.allChessDict.items():
            placeTaken.append(chess.position)
        bestPlace = None
        secondPlace = None
        shortest = 100
        for row in range(6):
            for col in range(5):
                distance = dist([row,col], caster.position)
                if [row,col] not in placeTaken and distance < shortest:
                    # find the position to be summoned, as close as possible to the owner
                    shortest = distance
                    secondPlace = bestPlace
                    bestPlace = [row,col]
        if bestPlace is not None:
            # 棋盘没满,召唤小狼1
            wolfMinion1 = wolfMinion(position=bestPlace,
                                     currentTime=currentTime,
                                     allChessDict=caster.allChessDict,
                                     teamDict = caster.teamDict)
            caster.teamDict[wolfMinion1.uniqueID] = wolfMinion1
            caster.allChessDict[wolfMinion1.uniqueID] = wolfMinion1
        if secondPlace is not None:
            # 棋盘没满,召唤小狼2
            wolfMinion2 = wolfMinion(position=secondPlace,
                                     currentTime=currentTime,
                                     allChessDict=caster.allChessDict,
                                     teamDict=caster.teamDict)
            caster.teamDict[wolfMinion2.uniqueID] = wolfMinion2
            caster.allChessDict[wolfMinion2.uniqueID] = wolfMinion2
# 狼
class wolf(chessInterface):
    def __init__(self,position = [3,3], skill = summonWolfMinions()):
        super().__init__(chessName = "头狼",
                         id=5,
                         race = "mammal",
                         star = 2,
                         attack = 45,
                         attack_interval=0.85,
                         attack_range = 1, 
                         armor=21,
                         health=520,
                         skill = skill)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def cast(self, currentTime: int):
        self.skill.cast(currentTime=currentTime,
                        caster = self)
        return super().cast(currentTime=currentTime,implemented=True)

class wolfMinion(wolf):
    def __init__(self, allChessDict, teamDict, currentTime:int, position=[3, 3]):
        super().__init__(position, skill = None)
        self.chessName = "狼分身"
        print(f"      {self}被召唤了!")
        self.attack = self.attack/3
        self.armor=self.armor/3
        self.health=self.health/3
        self.maxHP = deepcopy(self.health)
        self.statusDict['summoned'] = summoned(statusDuration=10,
                                               currentTime=currentTime,
                                               statusOwner=self)
        self.id = 28
        self.allChessDict = allChessDict
        self.teamDict = teamDict
        


# insect
############################################################################################################
class transformation(skillInterface):
    def __init__(self,attackAlt = 100, armorAlt = -10, newAttackRange = 3.5) -> None:
        super().__init__(skillName="变身",
                        cd=9,
                        type="active",
                        description="瓢虫张开翅膀飞翔，增加攻击距离以及巨量攻击伤害，但是防御力降低",
                        castRange=100)
        self.attackAlt = attackAlt
        self.armorAlt = armorAlt
        self.newAttackRange = newAttackRange
        self.canCast = True

    def cast(self,currentTime:int, caster: chessInterface, target: chessInterface):
        if self.canCast:
            target.attack += self.attackAlt
            target.armor += self.armorAlt
            target.attack_range = self.newAttackRange
            self.canCast = False
            print(f"{currentTime/100}      {caster}使用了变身,{target}的攻击力提升{target.attack}点,护甲降低{abs(self.armorAlt)}点,攻击距离增加至{self.newAttackRange}")


class ladybug(chessInterface):
    #瓢虫
    def __init__(self, position= [3,3]):
        super().__init__(chessName = "瓢虫",id=6,
                         race = "insect",
                         star = 2,
                         attack = 21,
                         attack_interval=0.8,
                         attack_range = 1,
                         armor=25,
                         health=478,
                         skill = transformation()) # 之前太强了，削弱一些
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def cast(self, currentTime: int):
        # when casting, change the status of the owner
        self.skill.cast(caster = self, target=self, currentTime=currentTime)
        return super().cast(implemented=True)


############################################################################################################

class going_honey(skillInterface):
    def __init__(self,
                 skillName: str = "来一口蜂蜜",
                 cd: float = 6,
                 type: str = "active",
                 description: str = "蜜蜂给一个随机队友喂食蜂蜜，增加其攻速40% 持续3秒") -> None:
        super().__init__(skillName, cd, type, description)
    
    def cast(self, currentTime:int, caster:chessInterface, target: chessInterface = None):
        randomMax = 0
        for (chessID,chess) in caster.teamDict.items():
            temp = random()
            if temp > randomMax and chess != caster: # 优先给队友加
                target = chess
        if target is None:
            target = caster
        print(f"{currentTime/100}   {caster}使用了{self}")
        target.statusDict['attack_interval_change'] = attack_interval_change(statusOwner=target,
                                                                             currentTime=currentTime,
                                                                             changeRatio=0.4,
                                                                             statusDuration=3)

class bee(chessInterface):
    def __init__(self,position= [3,3]):
        super().__init__(chessName = "蜜蜂",id=7,
                         race = "insect",
                         star = 2,
                         attack = 36,
                         attack_interval=1.1,
                         attack_range = 1,
                         armor=20,
                         health=380,
                         skill = going_honey())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.cd_counter = 300
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def cast(self, currentTime: int):
        self.skill.cast(currentTime=currentTime, caster = self, target = None)
        super().cast(implemented=True)

# marine
############################################################################################################
# 食人鱼技能
class swallow(skillInterface):
    def __init__(self, skillName: str = "吞噬",
                 cd: float = 0,
                 type: str = "passive",
                 description: str = "食人鱼吞噬其杀掉的敌人,获得并治疗对手的50%最大生命值的血量") -> None:
        super().__init__(skillName, cd, type, description)

    def cast(self, currentTime:int, caster: chessInterface, opponent: chessInterface):
        '''
        施法者获得攻击目标 50% 的属性'''
        print(f"{currentTime/100}   {caster}used{self}")
        caster.health += opponent.maxHP * 0.5
        caster.maxHP += opponent.maxHP * 0.5
        caster.attack += opponent.attack * 0.3

class swallower(chessInterface):
    #食人鱼
    def __init__(self,position= [3,3],skill:swallow = swallow()):
        super().__init__(chessName = "食人鱼",id=8,
                         race = "marine",
                         star = 2,
                         attack = 88,
                         attack_interval=1.2,
                         attack_range = 1,
                         armor=20,
                         health=380,
                         skill = skill)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def deal_damage_to(self,
                       opponent: chessInterface,
                       amount: float,
                       currentTime: int,
                       coefficient: float = 1.0) -> float:
        damage = amount*coefficient
        opponent.health -= damage
        self.totalDamage += damage
        # check receiver status (比如对手是海胆, id=9，就需要查看对方是否有反伤开启，对手是犀牛，就查看自己是否是昆虫等)
        if not self.id == 9 and opponent.id != 9 and \
            opponent.statusDict['dispersion_status'] is not None:
            # 如果两个海胆在场上，会有无限loop 的情况 所以加一个条件
            # print(damage)
            opponent.statusDict['dispersion_status'].activate(currentTime=currentTime,
                                                              target = opponent,
                                                              damage = damage)
        if opponent.check_death():
            self.skill.cast(currentTime, caster=self, target = opponent)
        return damage

############################################################################################################
# 海胆技能
class dispersion_skill(skillInterface):
    def __init__(self, skillName: str = "尖刺外壳",
                 cd: float = 6,
                 type: str = "active",
                 description: str = "海胆用尖刺外壳伤害对他造成伤害的敌方棋子",
                 returnRate: float = 1.5) -> None:
        super().__init__(skillName, cd, type, description)
        self.returnRate = returnRate

class sea_hedgehog(chessInterface):
    #海胆
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "海胆",id=9,
                         race = "marine",
                         star = 2,
                         attack = 20,
                         attack_interval=1.0,
                         attack_range = 1,
                         armor=3,
                         health=800,
                         skill = dispersion_skill())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,
            "dispersion_status": None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        self.cd_counter += 400 # 开战cd

    def cast(self, currentTime):
        if self.statusDict["dispersion_status"] is None:
            self.statusDict["dispersion_status"] = dispersion_status(currentTime=currentTime,statusOwner=self)
        else:
            self.statusDict["dispersion_status"].activate(currentTime)
        super().cast(implemented=True)

############################################################################################################
# 3星
# mammal 哺乳动物

# 麋鹿技能
class normalHeal(skillInterface):
    def __init__(self, amount: float = 150) -> None:
        super().__init__(skillName = '速效救心丸',
                         cd = 4,
                         type= "active",
                         description= "麋鹿施法治疗友方血量最低的单位，治疗量:150")
        self.healAmount = amount

    def cast(self, currentTime: int, caster: chessInterface, target: chessInterface = None):
        ''' 找到生命值最低人进行治疗'''
        target: chessInterface = None
        minHealth = 100000
        for (id, chess) in caster.teamDict.items():
            if chess.health > 0 and chess.health < minHealth:
                minHealth = chess.health
                target = chess
        if target is not None:
            print(f'{currentTime/100}  {caster}对{target}使用了{self}')
            target.heal(self.healAmount)
# 麋鹿
class heal_deer(chessInterface):
    def __init__(self,position = [3,3],
                 skill: normalHeal = normalHeal()):
        super().__init__(chessName = "麋鹿",id=10,
                         race = "mammal",
                         star = 3,
                         attack = 30,
                         attack_interval=1.05,
                         attack_range = 2.5,
                         armor=27,
                         health=830,
                         skill = None)
        self.skill = skill
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def cast(self, currentTime: int):
        self.skill.cast(currentTime=currentTime,caster = self, target = None)
        super().cast(implemented=True)

############################################################################################################

# TODO: 找到合适的位置跳过去攻击

class monkey(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "忍者猴",id=11,
                         race = "mammal",
                         star = 3,
                         attack = 74,
                         attack_interval=0.7, # 有可能太高
                         attack_range = 3,
                         armor = 17,
                         health= 288,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        
        
############################################################################################################
class antiInsect(skillInterface):
    def __init__(self, reductionRate: float = 0.8) -> None:
        super().__init__(skillName = "昆虫克制",
                    cd= 0,
                    type= "passive",
                    description= "犀牛的皮非常的厚，让昆虫的攻击穿透不了",
                    castRange = 100)
        self.reductionRate = reductionRate

class hippo(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "犀牛",id=12,
                         race = "mammal",
                         star = 3,
                         attack = 68,
                         attack_interval=1.7,
                         attack_range = 1,
                         armor = 91,
                         health= 1250,
                         skill = antiInsect())
        self.statusDict ={'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1


############################################################################################################
# 熊技能
class earth_shock(skillInterface):
    def __init__(self, skillName: str = "震撼大地",
                 cd: float = 7.0,
                 type: str = "active",
                 description: str = "熊震撼大地，眩晕身边的所有敌人") -> None:
        super().__init__(skillName, cd, type, description)

    def cast(self, currentTime, caster: chessInterface, target: chessInterface = None):
        caster.cd_counter = 0 # reset the counter for this skill
        print(f"{currentTime/100}  {caster}使用了{self}")
        for (chessID,chess) in caster.allChessDict.items():
            if chess.team != caster.team and chess.position in caster.get_surrounding(1):
                chess.statusDict['stunned'] = stunned(statusOwner=chess,
                                                      currentTime=currentTime,
                                                      statusDuration=2.5)
# 熊
class bear(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "熊",id=13,
                         race = "mammal",
                         star = 3,
                         attack = 95,
                         attack_interval=0.95,
                         attack_range = 1,
                         armor = 45,
                         health= 760,
                         skill = earth_shock())
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}

    def cast(self, currentTime: int):
        self.skill.cast(currentTime = currentTime, caster = self)
        super().cast(implemented = True)

#insect
############################################################################################################
# 蝴蝶


class butterfly(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "福蝶",id=14,
                         race = "insect",
                         star = 3,
                         attack = 66,
                         attack_interval=1.1,
                         attack_range = 3,
                         armor = 27,
                         health= 518,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

############################################################################################################
# 萤火虫
class holyLight(skillInterface):
    def __init__(self, 
                 skillName: str = "圣光", 
                 cd: float = 1, 
                 type: str = "active",
                 description: str = "萤火虫没有攻击力，但是萤火虫圣光所照之地的敌人会受到伤害，而同伴会被治疗", 
                 castRange: float = 0,
                 diameter = 2,
                 damage = 40) -> None: # 半径为2 的圆圈范围内
        super().__init__(skillName, cd, type, description, castRange)
        self.diameter = diameter
        self.damage = damage

    def cast(self, currentTime: int, caster:chessInterface, target: chessInterface=None):
        print(f"{currentTime}  {caster}对身旁半径为{self.diameter}的范围释放了{self}")
        for (uniqueID, chess) in caster.allChessDict.items():
            if dist(chess.position, caster.position) < self.diameter:
                if chess.team != caster.team:
                    caster.deal_damage_to(opponent=chess,damage = self.damage,currentTime=currentTime)
                else:
                    chess.heal(self.damage)

class fireworm(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "萤火虫",id=15,
                         race = "insect",
                         star = 3,
                         attack = 0,
                         attack_interval=10,
                         attack_range = 2,
                         armor = 30,
                         health= 650,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1


############################################################################################################
# 螳螂
class eclipseStrike(skillInterface):
    def __init__(self,
                 skillName: str = "绝影斩",
                 cd: float = 0,
                 type: str = "passive",
                 description: str = "",
                 damageCoefficient: float = 4,
                 chance: float = 0.2) -> None:
        super().__init__(skillName, cd, type, description)
        self.description = f"螳螂精通格斗，善于进攻并且找到对方的弱点，攻击时有{chance*100}%的概率造成{damageCoefficient*100}%攻击力的伤害"
        self.damageCoefficient = damageCoefficient # 暴击系数
        self.chance = chance

class mantis(chessInterface):
    def __init__(self,position = [3,3],skill :eclipseStrike =eclipseStrike()):
        super().__init__(chessName = "螳螂",id=16,
                         race = "insect",
                         star = 3,
                         attack = 140,
                         attack_interval=0.85,
                         attack_range = 1,
                         armor = 78,
                         health= 270,
                         skill = skill )
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        self.fakeRandom: float = 0

    def do_attack(self, opponent: chessInterface, currentTime: int, coefficient: float = 1) -> None:
        if random() + self.fakeRandom > 1-self.skill.chance: # 1 - 0.2 = 0.8
            coefficient = self.skill.damageCoefficient
            self.fakeRandom = 0 # reset the fakeRandom
            print(currentTime/100, f"  {self}使用了{self.skill}")
        else:
            self.fakeRandom += 0.02
            # print("      ",self, self.fakeRandom
        super().do_attack(opponent,currentTime, coefficient)


############################################################################################################
# 蝎子
class sand_poison(skillInterface):
    def __init__(self, skillName: str = "沙漠剧毒",
                 cd: float = 0,
                 type: str = "passive",
                 description: str = "蝎子向目标注射沙漠剧毒，让其在长时间内收到大量伤害",
                 damage: float = 100.0,
                 duration:float = 5) -> None:
        super().__init__(skillName, cd, type, description)
        self.damage = damage
        self.duration = duration * 100

    def cast(self, currentTime: int, caster:chessInterface, target: chessInterface):
        print(f"{currentTime/100}   {caster}在攻击{target}时使用了*{self}*")
        if target.statusDict["sand_poisoned"] is None:
            # 没被毒过
            target.statusDict["sand_poisoned"] = sand_poisoned(currentTime=currentTime,
                                                                statusOwner=target,
                                                                caster = caster)
        else:
            target.statusDict["sand_poisoned"].statusEnd = currentTime + self.duration # 500 是5秒


class scorpion(chessInterface):
    def __init__(self,position = [3,3], skill:sand_poison = sand_poison()):
        super().__init__(chessName = "蝎子",id=17,
                         race = "insect",
                         star = 3,
                         attack = 58,
                         attack_interval=1.5,
                         attack_range = 1,
                         armor = 32,
                         health= 840,
                         skill = skill)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def do_attack(self, opponent: chessInterface,currentTime: int, coefficient: float = 1) -> None:
        super().do_attack(opponent, currentTime, coefficient)
        self.skill.cast(currentTime=currentTime, caster = self, target = opponent)


#marine

############################################################################################################
class deathBeam(skillInterface):
    def __init__(self,castRange:float, baseDamage:float, ceilingDamage:float) -> None:
        super().__init__(skillName= "死亡射线",
                         cd = 5,
                         type = "active",
                         description="灯笼鱼用死亡射线折磨一个随机对手，对对手造成大量不确定性伤害 （随机性很强的一个棋子，增加对局的不确定性）",
                         castRange = castRange)
        self.baseDamage = baseDamage
        self.ceilingDamage = ceilingDamage

    def cast(self, currentTime: int, caster: chessInterface, target: chessInterface):
        target: chessInterface = None
        targetList = []
        for (uniqueID, chess) in caster.allChessDict.items():
            if chess.team != caster.team:
                targetList.append(chess)
        target = targetList[randint(0, len(targetList))] 
        damage = self.baseDamage + random()*(self.ceilingDamage-self.baseDamage)
        print(f"{currentTime/100}   {caster}对{target}使用了*{self}*,造成了{damage}点伤害")
        caster.deal_damage_to(opponent=target,damage= damage, currentTime=currentTime)

class anglerfish(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "灯笼鱼",id=18,
                         race = "marine",
                         star = 3,
                         attack = 45,
                         attack_interval=1.0,
                         attack_range = 2,
                         armor = 23,
                         health= 470,
                         skill = deathBeam(castRange=3, baseDamage=300, ceilingDamage=600))
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
    
    def cast(self, currentTime: int):
        self.skill.cast(currentTime=currentTime,caster= self,target=None)
        return super().cast(implemented = True)

############################################################################################################
class electric_eel(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "电鳗",id=19,
                         race = "marine",
                         star = 3,
                         attack = 65,
                         attack_interval=0.9,
                         attack_range = 3,
                         armor = 23,
                         health= 560,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

############################################################################################################
class crab(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "螃蟹",id=20,
                         race = "marine",
                         star = 3,
                         attack = 75,
                         attack_interval=1.3,
                         attack_range = 1,
                         armor = 35,
                         health= 880,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

############################################################################################################
class monoceros(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "一角鲸",id=21,
                         race = "marine",
                         star = 3,
                         attack = 88,
                         attack_interval=0.95,
                         attack_range = 1,
                         armor = 27,
                         health= 680,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

############################################################################################################
class turtle(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "海龟",id=22,
                         race = "marine",
                         star = 3,
                         attack = 50,
                         attack_interval=1.0,
                         attack_range = 1,
                         armor = 81,
                         health= 750,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1


# 4星
#mammal
############################################################################################################
class elephant(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "大象",id=23,
                         race = "mammal",
                         star = 4,
                         attack = 115,
                         attack_interval=1.2,
                         attack_range = 2,
                         armor = 65,
                         health= 1600,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

############################################################################################################
class tiger(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "老虎",id=24,
                         race = "mammal",
                         star = 4,
                         attack = 150,
                         attack_interval=0.55,
                         attack_range = 1,
                         armor = 43,
                         health= 1040,# 有点低
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

#insect
############################################################################################################
class unicorn_b(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "独角仙", id=25,
                         race = "insect",
                         star = 4,
                         attack = 112, # 有点低
                         attack_interval=0.55,
                         attack_range = 4,
                         armor = 26,
                         health= 560,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        
############################################################################################################
class ensnarement(skillInterface):
    def __init__(self, skillName: str = "蛛网缠绕",
                 cd: float = 14, 
                 duration: float = 5,
                 type: str = "active",
                 description: str = "蜘蛛跳跃到对方攻击力最高的人的身旁，并且缠绕住他，使其不能攻击",
                 castRange: float = 100) -> None:
        super().__init__(skillName, cd, type, description, castRange)
        self.duration = duration
        
    def move_to_target(self, caster:chessInterface, target: chessInterface, placeTaken: list = []):
        positions = target.get_surrounding(1)
        for p in positions.copy():
            if p in placeTaken:
                # p. 
                pass
    def cast(self, currentTime:int, caster:chessInterface, target: chessInterface= None):
        target = None
        highestAttack = -1
        for (uniqueID, chess) in caster.allChessDict.items():
            if chess.team != caster.team and chess.attack > highestAttack:
                target = chess
        self.move_to_target(caster = caster, target= target)
        if target.statusDict['disarmed'] is not None:
            #  增加缴械时间
            target.statusDict['disarmed'].statusEnd = currentTime + self.duration
        else:
            # 创建缴械对象
            target.statusDict['disarmed'] = disarmed(currentTime=currentTime,
                                                     statusOwner=target,
                                                     statusDuration=self.duration) 
        
class spider(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "蜘蛛", id=26,
                         race = "insect",
                         star = 4,
                         attack = 98, # 有点低
                         attack_interval=0.85,
                         attack_range = 1,
                         armor = 65,
                         health= 1270,
                         skill = ensnarement())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def cast(self, currentTime: int):
        self.skill.cast(currentTime=currentTime,caster= self)
        return super().cast(implemented = True)

#marine
############################################################################################################
class octpus(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "章鱼",id=27,
                         race = "marine",
                         star = 4,
                         attack = 99, # 有点低
                         attack_interval=0.75,
                         attack_range = 2,
                         armor = 42,
                         health= 1550,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1


############################################################################################################
class abyssBite(skillInterface):
    def __init__(self, baseAttack:int, increaseMultiplier = 20) -> None:
        super().__init__(skillName = "深渊撕咬",
                         cd = 0,
                         type= "passive", 
                         description="鲨鱼对目标进行撕咬，每一次都比上一次伤害更高", 
                         castRange=100)
        self.increaseMultiplier = increaseMultiplier
        self.singleTargetAttackCount = 0
        self.lastTarget = None
        self.baseAttack = baseAttack

    def cast(self, currentTime: int, caster:chessInterface, target: chessInterface):
        if target == self.lastTarget:
            print(f"{currentTime/100}  {caster}攻击了同一个目标，攻击力提升{self.increaseMultiplier}")
            self.singleTargetAttackCount += 1
            caster.attack = self.baseAttack + self.increaseMultiplier * self.singleTargetAttackCount
        else:
            self.singleTargetAttackCount = 0


class shark(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "鲨鱼",id=28,
                         race = "marine",
                         star = 4,
                         attack = 80, # 有点低
                         attack_interval=0.5,
                         attack_range = 1,
                         armor = 60,
                         health= 1200,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None}
        self.skill = abyssBite(baseAttack= self.attack)
        self.position = position
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
    
    def do_attack(self, opponent: chessInterface, currentTime: int, coefficient: float = 1) -> None:
        self.skill.cast(currentTime=currentTime,caster = self, target = opponent)
        super().do_attack(opponent, currentTime, coefficient)
        
