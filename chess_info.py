from __future__ import annotations
from termcolor import colored
from skillInterface import skillInterface
from statusInterface import statusInterface
from chessInterface import chessInterface
from copy import deepcopy
from numpy.random import random, randint
from math import dist, floor

from status_info import *

##################################################
##### 棋子技能以及 单位信息
##################################################


# 卡
# 1星卡
############################################################################################################
# 兔子
class spellDodge(skillInterface): # 兔子的躲避技能的技能应当作为一个高等级卡的技能，并且附带cd而不是一局一次。这个技能比较复杂，而且效果并不直观，不适合玩家一开始上手
    # spit saliva 
    def __init__(self) -> None:
        super().__init__(skillName = "走位走位",
                         cd = 0,
                         type = "active",
                         description= f"兔子用灵巧的走位，闪避了第一个对其使用的指向性技能")
        self.duration = 0
    
    def cast(self,currentTime: int, caster: chessInterface, target: chessInterface):
        print(f"{currentTime/100}   {caster}使用了{self},闪避了技能")
        if caster.canDodge is True:
            caster.canDodge = False

class huishoutao(skillInterface):
    def __init__(self,
                 cd:float = 4,
                 stunDuration:float = 1,
                 damage: float =100) -> None:
        super().__init__(skillName = "回手掏",
                         cd = cd,
                         type = "active",
                         description= f"对距离自己最近的目标进行飞踢，眩晕敌人1秒并且造成100点伤害")
        self.stunDuration = stunDuration
        self.damage = damage
    
    def cast(self,currentTime: int, caster: chessInterface, target: chessInterface = None):
        target = caster.get_hate_mechanism()
        print(f"{currentTime/100}   {caster}对{target}使用了{self},造成{self.damage}点伤害")
        if target.statusDict['stunned'] is not None:
            # 增加时长替代重新负值
            target.statusDict['stunned'].addBuff(currentTime=currentTime,duration = self.stunDuration)
        else:
            target.statusDict['stunned'] = stunned(currentTime=currentTime,
                                                statusDuration=self.stunDuration,
                                                statusOwner=target)
        caster.deal_damage_to(opponent=target,damage = self.damage,currentTime=currentTime)
  
class rabbit(chessInterface): 
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "兔子",
                         id=1,
                         race = "mammal",
                         star = 1,
                         attack = 21,
                         attack_interval=0.9,
                         attack_range = 1.5,
                         armor=10,
                         health=250,
                         skill = huishoutao())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
    def cast(self, currentTime: int = 0):
        self.skill.cast(currentTime=currentTime, caster = self)
        return super().cast(implemented= True)
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
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "蚂蚁",
                         id=2,
                         race = "insect",
                         star = 1,
                         attack = 20,
                         attack_interval = 1,
                         attack_range = 1.5,
                         armor=9,
                         health=180,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        self.skill = threeStinkers( attack = self.attack, 
                                   armor= self.armor, 
                                   health= self.health, 
                                   maxHP=self.maxHP)

    def cast(self,currentTime: int):
        ''' bigger
        '''
        self.skill.cast(currentTime,caster = self,target=self)
        # super().cast(implemented = True)
    def reset(self, test=False):
        threeStinkers.ant_count = 0 # 不重置的话在进行新游戏的时候会不停增加，导致蚂蚁无敌。
        return super().reset(test)

############################################################################################################
# 小丑鱼
class fearMove(skillInterface):
    def __init__(self,
                 cd:float = 2) -> None:
        super().__init__(skillName = "孩怕",
                         cd = cd,
                         type = "passive",
                         description= f"受到攻击后会害怕，并且向后撤")
    
    def cast(self,currentTime: int, caster: chessInterface):
        target = caster.get_hate_mechanism()
        position = target.position
        print(f"{currentTime/100}   {caster}{self}了,向后退了一格")
        row = position[0]
        col = position[1]
        if row > caster.position[0] and caster.position[0] > 0:
            caster.position[0] -= 1
            return
        elif row < caster.position[0] and caster.position[0] < 5:
            caster.position[0] += 1
            return
        if col > caster.position[1] and caster.position[1] > 0:
            caster.position[1] -= 1
            return
        elif col < caster.position[1] and caster.position[1] < 4:
            caster.position[1] += 1
            return

class littleUglyFish(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "小丑鱼",
                         id=3,
                         race = "marine",
                         star = 1,
                         attack = 33,
                         attack_interval=0.8,
                         attack_range = 2,
                         armor=12,
                         health=252,
                         skill = fearMove())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        
    def cast(self, currentTime: int):
        self.skill.cast(currentTime=currentTime, caster = self)
        return super().cast(currentTime, implemented = True)

# 2星卡
# mammal
############################################################################################################
# 羊驼
class hex(skillInterface):
    # turn an enemy into a sheep for x seconds
    def __init__(self, duration:float = 2) -> None:
        super().__init__(skillName = "变羊",
                         cd = 5.0,
                         type = "active",
                         description= f"把对方星级最高的棋子变成羊,持续{duration}秒")
        self.duration: float = duration
    
    def cast(self,currentTime: int, caster: chessInterface, target: chessInterface):
        maxStar = 0
        for (chessID,chess) in caster.allChessDict.items():
            if chess.team != caster.team and chess.star >= maxStar and not chess.isDead:
                target = chess
                maxStar = chess.star
        if target is not None:
            # 如果target 不是None，说明有目标可以被羊，羊目标后进入cd
            if target.statusDict['hexed'] is not None:
                # 增加时长替代重新负值
                target.statusDict['hexed'].addBuff(currentTime,self.duration)
            else:
                target.statusDict['hexed'] = hexed(statusOwner=target,
                                               currentTime=currentTime,
                                               statusDuration=self.duration)

class llama(chessInterface):
    def __init__(self,position = [3,3]):
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
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
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
            wolfMinion1 = wolfMinion(position =bestPlace,
                                     currentTime=currentTime,
                                     allChessDict=caster.allChessDict,
                                     teamDict = caster.teamDict)
            caster.teamDict[wolfMinion1.uniqueID] = wolfMinion1
            caster.allChessDict[wolfMinion1.uniqueID] = wolfMinion1
        if secondPlace is not None:
            # 棋盘没满,召唤小狼2
            wolfMinion2 = wolfMinion(position =secondPlace,
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
                         attack_range = 1.5, 
                         armor=16,
                         health=520,
                         skill = skill)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def cast(self, currentTime: int):
        self.skill.cast(currentTime=currentTime,
                        caster = self)
        return super().cast(currentTime=currentTime,implemented=True)

class wolfMinion(wolf):
    def __init__(self, allChessDict, teamDict, currentTime:int, position = [3, 3]):
        super().__init__(position, skill = None)
        self.chessName = "狼分身"
        print(f"      {self}被召唤了!")
        self.attack = self.attack/3
        self.armor=int(self.armor*0.7)
        self.health=self.health/3
        self.maxHP = deepcopy(self.health)
        self.statusDict['summoned'] = summoned(statusDuration=10,
                                               currentTime=currentTime,
                                               statusOwner=self)
        self.id= 29
        self.allChessDict = allChessDict
        self.teamDict = teamDict
        


# insect
############################################################################################################
class transformation(skillInterface):
    def __init__(self,attackAlt = 110, armorAlt = -10, newAttackRange = 3.5) -> None:
        super().__init__(skillName="变身",
                        cd=7,
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
    def __init__(self, position = [3,3]):
        super().__init__(chessName = "瓢虫",id=6,
                         race = "insect",
                         star = 2,
                         attack = 21,
                         attack_interval=0.8,
                         attack_range = 1.5,
                         armor=28,
                         health=478,
                         skill = transformation()) # 之前太强了，削弱一些
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
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
                 description: str = "蜜蜂给一个随机队友喂食蜂蜜，增加其攻速40% 持续3秒",
                 enhanceRatio: float = 0.4,
                 duration: float = 3) -> None:
        super().__init__(skillName, cd, type, description)
        self.enhanceRatio = enhanceRatio
        self.duration = duration
    
    def cast(self, currentTime:int, caster:chessInterface, target: chessInterface = None):
        randomMax = 0
        for (chessID,chess) in caster.teamDict.items():
            temp = random()
            if temp > randomMax and chess != caster: # 优先给队友加
                target = chess
        if target is None:
            target = caster
        print(f"{currentTime/100}   {caster}对{target}使用了{self}")
        if target.statusDict['attack_interval_change'] is not None:
            # 分别记录攻击时长
            target.statusDict['attack_interval_change'].addBuff(currentTime, self.duration, self.enhanceRatio)
        else:
            target.statusDict['attack_interval_change'] = attack_interval_change(statusOwner=target,
                                                                                currentTime=currentTime,
                                                                                changeRatio=self.enhanceRatio,
                                                                                statusDuration=self.duration)

class bee(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "蜜蜂",id=7,
                         race = "insect",
                         star = 2,
                         attack = 36,
                         attack_interval=1.1,
                         attack_range = 1.5,
                         armor=17,
                         health=380,
                         skill = going_honey())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.cd_counter = 300
        self.initialPosition = position
        self.position = deepcopy(position)
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

    def cast(self, currentTime:int, caster: chessInterface, target: chessInterface):
        '''
        施法者获得攻击目标 50% 的属性'''
        print(f"{currentTime/100}   {caster}used{self}")
        caster.health += target.maxHP * 0.5
        caster.maxHP += target.maxHP * 0.5
        caster.attack += target.attack * 0.3

class swallower(chessInterface):
    #食人鱼
    def __init__(self,position = [3,3],skill:swallow = swallow()):
        super().__init__(chessName = "食人鱼",id=8,
                         race = "marine",
                         star = 2,
                         attack = 88,
                         attack_interval=1.2,
                         attack_range = 1.5,
                         armor=15,
                         health=380,
                         skill = skill)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def deal_damage_to(self, opponent: chessInterface, damage: float, currentTime: int) -> bool:
        if super().deal_damage_to(opponent, damage, currentTime):
            self.skill.cast(currentTime, caster=self, target = opponent)


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
                         attack_range = 1.5,
                         armor=7,
                         health=1000,
                         skill = dispersion_skill())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None ,
            "dispersion_status": None}
        self.initialPosition = position
        self.position = deepcopy(position)
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
                         armor=19,
                         health=830,
                         skill = None)
        self.skill = skill
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
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
                         armor = 14,
                         health= 288,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        
        
############################################################################################################
class antiInsect(skillInterface):
    def __init__(self, reductionRate: float = 0.4) -> None:
        super().__init__(skillName = "昆虫克制",
                    cd= 0,
                    type= "passive",
                    description= "犀牛的皮非常的厚，让昆虫的攻击穿透不了,降低80%昆虫对其造成的伤害",
                    castRange = 100)
        self.reductionRate = reductionRate

class hippo(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "犀牛",id=12,
                         race = "mammal",
                         star = 3,
                         attack = 68,
                         attack_interval=1.7,
                         attack_range = 1.5,
                         armor = 63,
                         health= 1250,
                         skill = antiInsect())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1


############################################################################################################
# 熊技能
class earth_shock(skillInterface):
    def __init__(self, skillName: str = "震撼大地",
                 cd: float = 7.0,
                 type: str = "active",
                 description: str = "熊震撼大地，眩晕身边的所有敌人,并且造成伤害",
                 damage:float = 150,
                 duration:float = 2.5) -> None:
        super().__init__(skillName, cd, type, description)
        self.damage = damage
        self.duration = duration

    def cast(self, currentTime, caster: chessInterface, target: chessInterface = None):
        caster.cd_counter = 0 # reset the counter for this skill
        print(f"{currentTime/100}  {caster}使用了{self}")
        for (chessID,chess) in caster.allChessDict.items():
            if chess.team != caster.team and chess.position in caster.get_surrounding(1) and not chess.isDead:
                if chess.statusDict['stunned'] is None:
                    chess.statusDict['stunned'] = stunned(statusOwner=chess,
                                                        currentTime=currentTime,
                                                        statusDuration=self.duration)
                else:
                    chess.statusDict['stunned'].addBuff(currentTime, self.duration)
                caster.deal_damage_to(opponent=chess,damage = self.damage, currentTime=currentTime)
# 熊
class bear(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "熊",id=13,
                         race = "mammal",
                         star = 3,
                         attack = 95,
                         attack_interval=0.95,
                         attack_range = 1.5,
                         armor = 31,
                         health= 760,
                         skill = earth_shock())
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }

    def cast(self, currentTime: int):
        self.skill.cast(currentTime = currentTime, caster = self)
        super().cast(implemented = True)

#insect
############################################################################################################
# 蝴蝶

class silenceAttack(skillInterface):
    def __init__(self, skillName: str = "沉默花粉",
                 cd: float = 0,
                 type: str = "passive",
                 description: str = "蝴蝶用花粉蒙蔽敌人的知觉，让其不沉默，持续1.5秒",
                 castRange: float = 100,
                 duration:float = 1.5) -> None:
        super().__init__(skillName, cd, type, description, castRange)
        self.duration = duration

    def cast(self, currentTime, caster, target: chessInterface):
        super().cast(currentTime=currentTime, caster = caster, target = target)
        if target.statusDict['silenced'] is not None:
            # 增加时长
            target.statusDict['silence'].addBuff(currentTime=currentTime,duration = self.duration)
        else:
            target.statusDict['silence'] = silenced(currentTime=currentTime,
                                                    statusDuration=self.duration,
                                                    statusOwner = target)
class butterfly(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "福蝶",id=14,
                         race = "insect",
                         star = 3,
                         attack = 66,
                         attack_interval=1.1,
                         attack_range = 3,
                         armor = 22,
                         health= 518,
                         skill = silenceAttack(duration = 1.5))
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        
    def do_attack(self, opponent: chessInterface, currentTime: int, coefficient: float = 1) -> float:
        damage =  super().do_attack(opponent, currentTime, coefficient)
        self.skill.cast(currentTime=currentTime,caster = self, target =opponent)
        return damage

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
                if chess.team != caster.team and not chess.isDead:
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
                         armor = 24,
                         health= 650,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
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
                         attack_range = 1.5,
                         armor = 65,
                         health= 270,
                         skill = skill )
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        self.fakeRandom: float = 0

    def do_attack(self, opponent: chessInterface, currentTime: int, coefficient: float = 1) -> float:
        if random() + self.fakeRandom > 1-self.skill.chance: # 1 - 0.2 = 0.8
            coefficient = self.skill.damageCoefficient
            self.fakeRandom = 0 # reset the fakeRandom
            print(currentTime/100, f"  {self}使用了{self.skill}")
        else:
            self.fakeRandom += 0.02
        return super().do_attack(opponent,currentTime, coefficient)


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
                         attack_range = 1.5,
                         armor = 25,
                         health= 840,
                         skill = skill)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def do_attack(self, opponent: chessInterface,currentTime: int, coefficient: float = 1) -> float:
        damage = super().do_attack(opponent, currentTime, coefficient)
        self.skill.cast(currentTime=currentTime, caster = self, target = opponent)
        return damage


#marine

############################################################################################################
class deathBeam(skillInterface):
    def __init__(self,castRange:float, baseDamage:float, ceilingDamage:float) -> None:
        super().__init__(skillName= "死亡射线",
                         cd = 5,
                         type = "active",
                         description="灯笼鱼用死亡射线折磨一个随机对手，对对手造成大量不确定性伤害 （随机性很强的一个棋子，增加对局的不确定性）",
                         castRange=3, 
                         baseDamage=300, 
                         ceilingDamage=600)
        self.baseDamage = baseDamage
        self.ceilingDamage = ceilingDamage

    def cast(self, currentTime: int, caster: chessInterface, target: chessInterface):
        target: chessInterface = None
        targetList = []
        for (uniqueID, chess) in caster.allChessDict.items():
            if chess.team != caster.team and not \
                chess.isDead and \
                dist(chess.position, caster.position) <= self.castRange : # 目标要活着
                targetList.append(chess)
        if targetList == []:
            # 没有合适的对象
            return False
        target = targetList[randint(0, len(targetList))] 
        damage = self.baseDamage + random()*(self.ceilingDamage-self.baseDamage)
        print(f"{currentTime/100}   {caster}对{target}使用了*{self}*,造成了{damage}点伤害")
        caster.deal_damage_to(opponent=target,damage= damage, currentTime=currentTime)
        return True

class anglerfish(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "灯笼鱼",id=18,
                         race = "marine",
                         star = 3,
                         attack = 45,
                         attack_interval=1.0,
                         attack_range = 2,
                         armor = 17,
                         health= 470,
                         skill = deathBeam())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
    
    def cast(self, currentTime: int):
        if self.skill.cast(currentTime=currentTime,caster= self,target=None):
            # 如果施放成功
            return super().cast(implemented = True)

############################################################################################################
class electricChain(skillInterface):
    def __init__(self, 
                 skillName: str = "闪电链", 
                 cd: float = 0, 
                 type: str = "passive",
                 description: str = "电鳗在攻击敌方的时候放电，有50%的概率电击范范围内的至多三个敌人（单一目标不会重复受到伤害）",
                 castRange: float = 100) -> None:
        super().__init__(skillName, cd, type, description, castRange)
    

class electric_eel(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "电鳗",id=19,
                         race = "marine",
                         star = 3,
                         attack = 65,
                         attack_interval=0.9,
                         attack_range = 3,
                         armor = 18,
                         health= 560,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
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
                         attack_range = 1.5,
                         armor = 28,
                         health= 880,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
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
                         attack_range = 1.5,
                         armor = 22,
                         health= 680,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
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
                         attack_range = 1.5,
                         armor = 56,
                         health= 750,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1


# 4星
#mammal
############################################################################################################
class warSmash(skillInterface):
    def __init__(self, skillName: str = "战争重碾",
                 cd: float = 10, # 一锤定音
                 type: str = "active", 
                 description: str = "大象蓄力后向一个方向冲锋，对路径和周围的敌人造成伤害并且击退",
                 castRange: float = 3,
                 hold: float = 2.0 #蓄力时间
                 ) -> None:
        super().__init__(skillName, cd, type, description, castRange)
        
    def cast(self, currentTime: int, caster: chessInterface, target = None):
        target = []
        # 选定方向
        
        # 蓄力
        
        # 冲锋
        print(f"{currentTime/100}  {caster}使用了{self}")        

class elephant(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "大象",id=23,
                         race = "mammal",
                         star = 4,
                         attack = 115,
                         attack_interval=1.2,
                         attack_range = 2,
                         armor = 46,
                         health= 1600,
                         skill = warSmash())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def cast(self, currentTime: int = 0):
        
        return super().cast(currentTime, implemented = True)
############################################################################################################
# old虎
class bite(skillInterface):
    def __init__(self,
                 duration: float = 3.0,
                 amplification: float = 0.3,
                 bleedInstanceDamage: float = 25) -> None:
        super().__init__(skillName= "重伤",
                         cd = 6,
                         type = "active",
                         description=f"老虎使用重击攻击目标，造成150%的暴击，使对手收到的所有伤害增加{amplification}，并且流血,在{duration}秒内共造成{duration*bleedInstanceDamage}点伤害",
                         castRange = 1)
        self.duration = duration
        self.amplification = amplification
        self.instanceDamage = bleedInstanceDamage

    def cast(self, currentTime: int, caster: chessInterface, target: chessInterface):
        print(f"{currentTime/100}   {caster}对{target}使用了*{self}*,施加流血和脆弱效果")
        if target.statusDict['vulnerable'] is None:
            target.statusDict['vulnerable'] = vulnerable(currentTime=currentTime,
                                                        statusDuration=self.duration,
                                                        amplification=self.amplification,
                                                        statusOwner=target)
        else:
            target.statusDict['vulnerable'].addBuff(currentTime, self.duration)
            
        if target.statusDict['bleeding'] is None:
            target.statusDict['bleeding'] = bleeding(currentTime=currentTime,
                                                    statusDuration=self.duration,
                                                    statusOwner=target,
                                                    caster=caster,
                                                    instanceDamage=self.instanceDamage)
        else:
            target.statusDict['bleeding'].addBuff(currentTime, self.duration)
        caster.do_attack(opponent=target, coefficient=1.5, currentTime=currentTime)
        

class tiger(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "老虎",id=24,
                         race = "mammal",
                         star = 4,
                         attack = 140,
                         attack_interval=0.7,
                         attack_range = 1.5,
                         armor = 34,
                         health= 1040,# 有点低
                         skill = bite())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def cast(self, currentTime: int):
        # opponents_distances = self.opponent_distances()
        # nearest = sorted(opponents_distances)[0]
        # chessToBeAttacked = opponents_distances[nearest]
        target = self.opponent_distances()[sorted(self.opponent_distances())[0]]
        self.skill.cast(currentTime=currentTime,caster=self,target=target)
        return super().cast(implemented = True)

#insect
############################################################################################################
# 独角仙
class rebirth(skillInterface):
    def __init__(self, skillName: str = "重生",
                 cd: float = 999,
                 duration: float = 0.5,
                 type: str = "active",
                 description: str = "重生") -> None:
        super().__init__(skillName, cd, type, description)
        self.duration = duration
    
    def cast(self, currentTime:int, caster:chessInterface, target: chessInterface):
        target.statusDict['reviving'] = reviving(currentTime=currentTime,
                                                     statusDuration=self.duration,
                                                     statusOwner=target) 
        target.isDead = False
        
        
class unicorn_b(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "独角仙", id=25,
                         race = "insect",
                         star = 4,
                         attack = 112, # 有点低
                         attack_interval=0.6,
                         attack_range = 4,
                         armor = 16,
                         health= 560,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
        self.revived = False

    # def cast(self, currentTime: int):
    #     self.skill.cast(currentTime=currentTime,caster=self,target=self)
    #     return super().cast(implemented = True)
    
    # def can_attack(self) -> bool:
    #     if 'reviving' not in self.statusDict:
    #         return super().can_attack()
    #     else:
    #         return False

    # def can_cast(self) -> bool:
    #     if 'reviving' not in self.statusDict:
    #         return super().can_cast()
    #     else:
    #         return False

    # def check_death(self, currentTime:int) -> bool:
    #     '''
    #     检查当前棋子是否死亡，并且做出相应操作
    #     '''
    #     if self.health <= 0:
    #         if self.revived:
    #             if 'reviving' in self.statusDict:
    #                 self.health = 1
    #                 return False
    #             else:
    #                 self.deathTime = currentTime
    #                 # remove this chess from opponent's team list
    #                 print()
    #                 print(f"    {self} 已经被打败!")
    #                 print()
    #                 self.isDead = True # 标记死亡
    #                 self.position=[-1,-1] # 移除棋盘
    #                 print(self.teamDict, self.uniqueID)
    #                 del self.teamDict[self.uniqueID]
    #                 return True
    #         else:
    #             self.cast(currentTime=0)
    #             self.health = 1
    #             self.revived = True
    #             return False
    #     else:
    #         return False
        
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
        """找到一个目标旁边的随机地点
        Returns:
            list[int]: 目标旁边的一个随机坐标
        """
        positions = target.get_surrounding(1)
        for p in positions.copy():
            if p in placeTaken:
                positions.remove(p)
        return positions[randint(0,len(positions))] 
        
    def cast(self, currentTime:int, caster:chessInterface, target: chessInterface= None):
        target = None
        highestAttack = -1
        for (uniqueID, chess) in caster.allChessDict.items():
            if chess.team != caster.team and chess.attack > highestAttack and not chess.isDead:
                target = chess
        pos = self.move_to_target(caster = caster, target= target)
        caster.position = pos
        # TODO: 更新棋盘
        if target.statusDict['disarmed'] is not None:
            #  增加缴械时间
            target.statusDict['disarmed'].addBuff(currentTime, self.duration)
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
                         attack_range = 1.5,
                         armor = 45,
                         health= 1270,
                         skill = ensnarement())
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1

    def cast(self, currentTime: int):
        self.skill.cast(currentTime=currentTime,caster= self)
        return super().cast(implemented = True)

#marine
############################################################################################################
class octopus(chessInterface):
    def __init__(self,position = [3,3]):
        super().__init__(chessName = "章鱼",id=27,
                         race = "marine",
                         star = 4,
                         attack = 99, # 有点低
                         attack_interval=0.75,
                         attack_range = 2,
                         armor = 33,
                         health= 1550,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.initialPosition = position
        self.position = deepcopy(position)
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
        self.lastTarget = caster 
        if target == self.lastTarget or self.lastTarget is None: # 第一次攻击没有last target
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
                         attack_range = 1.5,
                         armor = 42,
                         health= 1200,
                         skill = None)
        self.statusDict = {'moving': None,
            'silenced': None, 'disarmed':None, 'stunned': None, 'hexed': None, 'taunted': None,
            'blood_draining':None, 'sand_poisoned': None, 'broken': None,
            'armor_change':None, 'attack_change':None, 'attack_interval_change':None,'vulnerable':None,'bleeding':None }
        self.skill = abyssBite(baseAttack= self.attack)
        self.initialPosition = position
        self.position = deepcopy(position)
        self.uniqueID = chessInterface.uniqueID + 1
        chessInterface.uniqueID += 1
    
    def do_attack(self, opponent: chessInterface, currentTime: int, coefficient: float = 1) -> None:
        self.skill.cast(currentTime=currentTime,caster = self, target = opponent)
        return super().do_attack(opponent, currentTime, coefficient)
        
