from __future__ import annotations
from skillInterface import skillInterface
from statusInterface import statusInterface
from termcolor import colored
from copy import deepcopy
from math import dist, floor
from queue import Empty, Queue

class chessInterface:
    
    '''
    这是棋子接口  所有的棋子都通过这个借口实现 以保证格式正确
    需要重写 cast 方法
    属性：
        race: str,
        star: int,
        chessName: str,
        attack: int,
        attack_interval: float,
        attack_range: int,
        armor: int,
        health: float,
        skill: skillInterface,
        statusDict: dict[str, statusInterface] = {},
        team: int = 0,
        evasion: float = 0,
        moving_speed = 0.3
    方法:
        can_attack(self) -> bool
        can_cast(self) -> bool
        activate_status(self, currentTime: int)-> None
        cast(self, currentTime: int, allChessDict: dict) -> list
        check_death()
        add_team_dict()
    '''
    def __init__(self,
                 race: str,
                 star: int,
                 chessName: str,
                 id: int,
                 attack: int,
                 attack_interval: float,
                 attack_range: int,
                 armor: int,
                 health: float,
                 skill: skillInterface,
                 statusDict: dict[str, statusInterface] = {},
                 team: int = 0,
                 evasion: float = 0,
                 moving_speed = 0.3 # 一个棋子从一个格子挪到下一个格子所用的时间
                 ):
        self.isDead = False # 棋子存活状态
        self.chessName = chessName # 棋子名称
        self.id = id # 棋子类ID
        self.race = race # 棋子种族
        self.star = star # 棋子星级
        self.attack = attack # 棋子攻击力
        self.attack_interval = int(attack_interval * 100) # 棋子攻击间隔
        self.attack_range = attack_range # 棋子攻击范围
        self.armor = armor # 棋子护甲
        self.maxHP = deepcopy(health) #棋子最大生命值
        self.health = health # 棋子当前生命值
        self.skill = skill # 棋子技能
        self.evasion = evasion # 棋子闪避概率
        self.position = [3,3] # 棋子在棋盘上的位置, 默认位置是 【3，3】
        self.team = team # team 0 = 红方, team 1 = 蓝方
        self.teamDict: dict[int,chessInterface] = {}  # 己方棋子字典
        self.allChessDict: dict[int,chessInterface] = {} # 所有棋子字典，其实可以和上面的己方棋子字典合二为一
        self.statusDict = statusDict # 棋子状态栏
        self.movingSpeed = moving_speed

        self.totalDamage:float = 0
        self.attack_counter:int = 0 # take track of when this chess can attack
        self.cd_counter:int = 0 # take track of when this chess can cast spell
    # 公用ID，每添加一个棋子，id就会加1
    uniqueID = 0
    def __repr__(self) -> str:
        if self.team == 0:
            return f"{colored(self.chessName+str(self.uniqueID), 'red')}"
        else:
            return f"{colored(self.chessName+str(self.uniqueID), 'blue')}"
    def __eq__(self, otherChess: chessInterface):
        return self.uniqueID == otherChess.uniqueID

    def getTotalDamageDealt(self):
        return self.totalDamage

    def add_team_dict(self, teamDict):
        """add team dict to the chess
        Args:
            teamDict (_type_): the dict for that team
        """
        self.teamDict = teamDict

    def add_allChessDict(self, allChessDict: dict[int, chessInterface]):
        """add AllChessDict to that chess

        Args:
            allChessDict (dict[int, chessInterface]): _description_
        """
        self.allChessDict = allChessDict

    def can_move(self) -> bool:
        '''判定棋子是否可以移动'''
        if self.statusDict['stunned'] is None and \
            self.statusDict['hexed'] is None and \
            self.statusDict['taunted'] is None and \
            self.statusDict['moving'] is None and \
            not self.isDead:
            return True
        return False
    
    def enemy_in_attack_range(self) -> bool:
        return sorted(self.opponent_distances())[0] <= self.attack_range


    def can_attack(self) -> bool:
        '''判定棋子是否可以攻击, attack_interval 100 = 1 秒'''
        # print("attack?",self.attack_counter, self.attack_interval )
        # print(self)
        if self.statusDict['stunned'] is None and \
            self.statusDict['hexed'] is None and \
            self.statusDict['silenced'] is None and \
            self.statusDict['taunted'] is None and \
            self.statusDict['moving'] is None:
            return self.attack_counter >= self.attack_interval
    
    def enemy_in_cast_range(self) -> bool:
        if self.skill is None:
            return False
        if hasattr(self.skill,'castRange'):
            return sorted(self.opponent_distances())[0] <= self.skill.castRange
        else: 
            return True

    def can_cast(self) -> bool:
        ''' 判定棋子是否可以施法
        check if the caster should cast the spell.
        The chess will not cast even if the counter reaches the limit if it is silenced/stunned/hexed/taunted
        如果没有敌方棋子在施法范围内，也不能施放'''
        if self.skill is None:
            return False
        if self.skill.type == 'active':
            if self.statusDict['stunned'] is None and \
                self.statusDict['hexed'] is None and \
                self.statusDict['silenced'] is None and \
                self.statusDict['taunted'] is None and \
                self.statusDict['moving'] is None:
                return self.cd_counter >= int(self.skill.cd * 100) # 如果计数器满了，就判定为可以施放技能
        else:
            if self.statusDict['broken'] is None:
                return self.cd_counter >= int(self.skill.cd * 100)
            else:
                return False

    def activate_status(self, currentTime: int)-> None:
        '''如果激活条件满足，就触发状态效果'''
        for (statusID, status) in self.statusDict.items():
            if status is not None:
                # print(self,status)
                status.activate(currentTime=currentTime)

    def cast(self, currentTime:int=0, implemented: bool = False):
        ''' this method is to cast the skill, implement with special needs \n
        currentTime 是placeholder \n
        如果implemented is not True，说明这个主动技能还没有被开发 \n
        ** 调用此父方法会自动重置 cd_counter 和 attack_counter.
        return: None
        '''
        if implemented:
            # 方法被实现，说明可以在此做操作，这个操作就是 把自己的攻击和技能counter重置
            self.cd_counter = 0
            self.attack_counter = 0
        elif self.skill is None or self.skill.type == "passive":
            return
        else:
            print(f"{self}Implement the cast method!!!! remember to reset the timer to 0")

    def check_death(self) -> bool:
        '''
        检查当前棋子是否死亡，并且做出相应操作
        '''
        if self.isDead:
            return True
        else:
            if self.health <= 0:
                # remove this chess from opponent's team list
                print()
                print(f"    {self} 已经被打败!")
                print()
                self.isDead = True # 标记死亡
                self.position=[-1,-1] # 移除棋盘
                # print(self.teamDict, self.uniqueID)
                del self.teamDict[self.uniqueID]
                return True
            else:
                return False

    def calculate_attack_damage(self, attack:float, opponent: chessInterface):
        return attack * (1 - opponent.armor*0.09/(1+0.09*opponent.armor)) * 2

    def do_attack(self,
            opponent: chessInterface,
            currentTime: int,
            coefficient: float = 1.0) -> None:
        """在棋子需要攻击的时候调用这个方法，这个方法会计算伤害，调用 deal_damage_to()方法造成伤害,并且打印attack info。

        Args:
            opponent (chessInterface): _description_
            currentTime (int): _description_
            coefficient (float, optional): _description_. Defaults to 1.0.
        """
        damage = self.calculate_attack_damage(attack = self.attack*coefficient, opponent=opponent)
        self.print_attack_info(opponent,currentTime,damage)
        self.deal_damage_to(opponent=opponent,
                            damage= damage,
                            currentTime=currentTime)
        self.attack_counter = 0

    def print_attack_info(self,opponent: chessInterface, currentTime: int, damage: float):
        # print(currentTime/100,f"{t}方棋子<{colored(self.chessName,'magenta')}> 攻击了{ot}方棋子<{colored(opponent.chessName,'magenta')}>, 造成了{colored(damage,'cyan')}点伤害，{ot}方棋子<{colored(opponent.chessName,'magenta')}>生命值还剩:{colored(opponent.health,'green')} / {opponent.maxHP}") 
        print(currentTime/100,f"<{self}> 攻击了<{opponent}>, 造成了{colored(damage,'cyan')}点伤害，<{opponent}>生命值还剩:{colored(opponent.health-damage,'green')} / {opponent.maxHP}") 
    
    def deal_damage_to(self,
                       opponent: chessInterface,
                       damage: float,
                       currentTime: int) -> None:
        """这个方法只造成伤害，伤害是在调用这个方法之前就算好的。这个方法不改变任何值输入值，只改变目标血量和判定特殊情况。

        Args:
            opponent (chessInterface): _description_
            damage (float): _description_
            currentTime (int): _description_
        """
        if self.id in {2,6,7,14,15,16,17,25,26} and opponent.id == 12: # 自己如果是虫，对方如果是犀牛，就减少自己对其造成的伤害
            damage = damage * opponent.skill.reductionRate
        opponent.health -= damage
        self.totalDamage += damage
        # check receiver status (比如对手是海胆, id=9，就需要查看对方是否有反伤开启，对手是犀牛，就查看自己是否是昆虫等)
        if self.id != 9 and opponent.id == 9 and \
            opponent.statusDict['dispersion_status'] is not None:
            # 如果两个海胆在场上，会有无限loop 的情况 所以加一个条件
            opponent.statusDict['dispersion_status'].activate(currentTime=currentTime,
                                                              target = self,
                                                              damage = damage)
        opponent.check_death()
        

    def heal(self, amount)->None:
        # 当棋子进行治疗的时候调用这个方法
        final_health = self.health + amount
        if final_health >= self.maxHP:
            self.health = self.maxHP
        else:
            self.health = final_health
        print(f"    {self}受到{colored(amount, 'green')}点治疗，的生命值恢复到了{colored(self.health, 'green')} / {self.maxHP}")

    def moveToCastPosition(self):
        '''将棋子移动到最佳施法位置'''
        bestPos = self.find_position_to_move(considerAttack=False, ConsiderSpell=True)
        self.moveChessTo(newPosition=bestPos)

    def moveChessTo(self, currentTime:int,  newPosition: list[int]):
        '''
        在棋子需要移动的时候调用这个方法
        '''
        self.position = newPosition
        self.statusDict['moving'].activate(currentTime=currentTime)

    def get_surrounding(self, searchingRange:int = 1) -> list[list[int]]:
        '''
        range 是n*n 的范围，而不是圈的范围，可以做优化 TODO
        
        return:
            所有符合这个范围的，在棋盘之内的格子 list(position)
        '''
            # select (range*2+1)^2 area around self
        surrounding:list[list[int]] = []
        for row in range(self.position[0] - searchingRange, self.position[0] + searchingRange+1):
            for col in range(self.position[1] - searchingRange, self.position[1] + searchingRange+1):
                if row in range(6) and col in range(5):
                    surrounding.append([row, col])
        return surrounding

    def opponent_ids(self) -> list[int]:
        '''返回所有对方棋子的距离和chess的 dict'''
        return [uniqueID for (uniqueID,chess) in self.allChessDict.items() if chess.team != self.team]

    def opponent_distances(self) -> dict[float, chessInterface]:
        '''返回所有对方棋子的直线距离和chess的 dict'''
        # print(self.allChessDict)
        return {abs(dist(self.position,
                                chess.position)):chess
                for (uniqueID,chess) in self.allChessDict.items()
                if chess.team != self.team}
    
    def opponent_step_distances(self,board:list[list[chessInterface]]) -> dict[int, chessInterface]:
        '''返回所有对方棋子的路径距离和chess的 dict'''
        distance:list[list[int]] = [[30 for _ in range(5)] for _ in range(6)]
        def bfs(step:int, curr_pos:list[int]):
            '''
            distance: 棋子距离矩阵
            step: 步数
            curr_pos: 当前棋子位置
            '''
            try:
                if board[curr_pos[0]][curr_pos[1]] is None or step == 0:
                    if distance[curr_pos[0]][curr_pos[1]] > step:
                        # print(distance[curr_pos[0]][curr_pos[1]])
                        distance[curr_pos[0]][curr_pos[1]] = step
                        # print(distance[curr_pos[0]][curr_pos[1]])
                        # distance_print(distance)
                        bfs(step + 1, [curr_pos[0],curr_pos[1]-1]) # 上
                        bfs(step + 1, [curr_pos[0],curr_pos[1]+1]) # 下
                        bfs(step + 1, [curr_pos[0]-1,curr_pos[1]]) # 左
                        bfs(step + 1, [curr_pos[0]+1,curr_pos[1]]) # 右
            except IndexError:
                pass
        bfs(0,self.position)
        return {abs(dist(self.position,
                                chess.position)):chess
                for (uniqueID,chess) in self.allChessDict.items()
                if chess.team != self.team}

    def get_hate_mechanism(self)-> chessInterface:
        '''
        这个方法意在找到当前棋子的下一个攻击对象
        '''
        opponents_distances = self.opponent_distances()
        nearest = sorted(opponents_distances)[0]
        # print(self,nearest,opponents_distances)
        chessToBeAttacked = opponents_distances[nearest]
        return chessToBeAttacked
    

    def get_enemy(self,board:list[list[chessInterface]])->dict[str, any]:
        '''
        返回棋子最近敌人距离和方向
        '''
        def bfs_queue(source_pos:list[int]): # queue实现bfs
            '''
            通过广度优先搜索
            返回移动距离最近的敌方棋子
            '''
            # 初始化
            distance:list[list[int]] = [[30 for _ in range(5)] for _ in range(6)] # 棋子与棋盘上每个格 的移动距离
            distance[source_pos[0]][source_pos[1]] = 0
            queue = Queue()
            
            # 棋子初始移动方向
            queue.put({'step':1, 'pos':[source_pos[0]-1,source_pos[1]], 'direction':'up'}) # 上 
            queue.put({'step':1, 'pos':[source_pos[0]+1,source_pos[1]], 'direction':'down'}) # 下
            queue.put({'step':1, 'pos':[source_pos[0],source_pos[1]-1], 'direction':'left'}) # 左
            queue.put({'step':1, 'pos':[source_pos[0],source_pos[1]+1], 'direction':'right'}) # 右

            # 优先处理距离棋子距离为1的格，然后2，3，4，以此类推
            while queue.not_empty:
                try:
                    curr = queue.get_nowait() # 获取下一个未探索的格
                    step = curr['step'] # 当前距离棋子的移动距离
                    curr_pos = curr['pos'] # 当前位置
                    if curr_pos[0] < 0 or curr_pos[1] < 0: # python接受负的index值，这里避免这种情况发生
                        # raise IndexError(f"Index is out of range")
                        continue
                    chess = board[curr_pos[0]][curr_pos[1]]
                    direction = curr['direction'] # 传递初始移动方向 至输出
                    if chess is None: # path reached another chess
                        if distance[curr_pos[0]][curr_pos[1]] > step: # 更新 棋子与当前格 的最短移动距离
                            distance[curr_pos[0]][curr_pos[1]] = step
                            queue.put({'step':step + 1, 'pos':[curr_pos[0]-1,curr_pos[1]], 'direction':direction}) # 上
                            queue.put({'step':step + 1, 'pos':[curr_pos[0]+1,curr_pos[1]], 'direction':direction}) # 下
                            queue.put({'step':step + 1, 'pos':[curr_pos[0],curr_pos[1]-1], 'direction':direction}) # 左
                            queue.put({'step':step + 1, 'pos':[curr_pos[0],curr_pos[1]+1], 'direction':direction}) # 右
                    elif chess.team != self.team: # 发现距离棋子 移动距离最近 的敌方棋子
                        return {'target_distance':step, 'target_position':curr_pos, 'target':chess, 'direction':direction}
                except IndexError: # 寻路超出棋盘范围
                    continue
                except Empty: # queue为空
                    break
            return {'target_distance':None, 'target_position':None, 'target':None, 'direction':None}
        return bfs_queue(self.position)

    



    def find_attack_target(self, placesAvailable: list[list[int]]):
        # sort the targets in the order of distance to the attacker(or other restrains), 
        # find the position ranking where it can attack each target
        # compare to find the best among this ranking #TODO: optimize this algorithm
        target = None
        goodPlaces = {}
        opponentDistances: dict[float, chessInterface] = self.opponent_distances()
        # sort the target in distances:
        opponentDistances = sorted(opponentDistances, key = opponentDistances.keys())
        # find the position where self can attack each of them
        for distance,opponent in opponentDistances.items():
            for position in placesAvailable:
                if (position in opponent.get_surrounding(self.attack_range)) and (position not in goodPlaces.keys()): # 在这些格子中攻击者都可以打到被攻击者
                    goodPlaces[position] = opponent # 因为position not in goodPlaces.keys()， 说明这个position 没有更好的可攻击对象，我们也就可以改变其键值对
        goodPlaces = sorted(goodPlaces,key = goodPlaces.keys()) # 按照 distance 给这些格子排序
        # 按照这个顺序检查最短路径，并且返回这个路径 TODO
        for (distance, opponent) in goodPlaces:
            self.find_path(opponent)
        
        for position in placesAvailable:
            distance = dist([position[0],position[1]], self.position)
            if distance < shortest and distance < self.attack_range:
                # find the position to move, as close as possible to the owner
                shortest = distance
                bestPlace = [position[0],position[1]]
        return bestPlace, target

    # def find_position_to_move(self, considerAttack = True, ConsiderSpell = True) -> list[int]:
    #     '''返回一个最好的可以移动的位置 （现在没考虑能被卡住的情况 和多次走的情况，也就是说现在是直接走到下一个合适位置，而没有中间过程） TODO
    #     '''
    #     opponentDistances = self.opponent_distances()

    #     position_to_move_for_attack, target = self.find_attack_target(target)
    #     # 就近原则

    #     find_skill_target()# 找到合适的施法对象并且移动到施法距离之内 （什么是合适的施法格：施法单位和施法者的距离等于两者距离，并且施法格离施法者的距离（移动距离）最近）
    #     # 如果施法范围内有敌方单位，那么就对其施法，否则，就需要移动
    #     placeAvailable = []
    #     for i in range(6):
    #         for j in range(5):
    #             placeAvailable.append([i,j])
    #     placeTaken = [self.position]
    #     opponentCanBeAttacked = {}
    #     opponentOutOfAttackRange = {}
    #     bestPlace = None

    #     for (uniqueID, chess) in self.allChessDict.items():
    #         placeTaken.append(chess.position)
    #         placeAvailable.remove(chess.position)
    #         distanceToOpponent = dist(chess.position, self.position)
    #         if distanceToOpponent < self.attack_range:
    #             opponentCanBeAttacked[distanceToOpponent] = chess
    #         else:
    #             opponentOutOfAttackRange[distanceToOpponent] = chess

    def move_to(self,
            direction: str,
            currentTime: int,
            coefficient: float = 1.0) -> None:
        """在棋子需要攻击的时候调用这个方法，这个方法会计算伤害，调用 deal_damage_to()方法造成伤害,并且打印attack info。

        Args:
            opponent (chessInterface): _description_
            currentTime (int): _description_
            coefficient (float, optional): _description_. Defaults to 1.0.
        """
        new_pos = {
            'up':lambda x,y: [x-1,y],
            'down':lambda x,y: [x+1,y],
            'left':lambda x,y: [x,y-1],
            'right':lambda x,y: [x,y+1]
        }
        self.moveChessTo(currentTime=currentTime,newPosition=new_pos[direction](self.position[0],self.position[1]))
        # distanceToOpponent = self.calculate_distance_to_opponent
        # damage = self.calculate_attack_damage(attack = self.attack*coefficient, opponent=opponent)
        self.print_move_info(direction,currentTime)
        # self.deal_damage_to(opponent=opponent,
        #                     damage= damage,
        #                     currentTime=currentTime)
        # self.attack_counter = 0

    def print_move_info(self,direction: str, currentTime: int):
        # print(currentTime/100,f"{t}方棋子<{colored(self.chessName,'magenta')}> 攻击了{ot}方棋子<{colored(opponent.chessName,'magenta')}>, 造成了{colored(damage,'cyan')}点伤害，{ot}方棋子<{colored(opponent.chessName,'magenta')}>生命值还剩:{colored(opponent.health,'green')} / {opponent.maxHP}") 
        print(currentTime/100,f"<{self}>向<{direction}> 移动了一格") 