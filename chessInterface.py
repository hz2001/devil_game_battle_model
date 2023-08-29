from __future__ import annotations
import random
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
                 attack_range: float,
                 armor: int,
                 health: float,
                 skill: skillInterface,
                 statusDict: dict[str, statusInterface] = {},
                 team: int = 0,
                 evasion: float = 0,
                 moving_speed = 0.5 # 一个棋子从一个格子挪到下一个格子所用的时间
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
        self.initialPosition = [3,3] # 棋子在棋盘上的初始位置，每回合结束自动复原
        self.team = team # team 0 = 红方, team 1 = 蓝方
        self.teamDict: dict[int,chessInterface] = {}  # 己方棋子字典
        self.allChessDict: dict[int,chessInterface] = {} # 所有棋子字典，其实可以和上面的己方棋子字典合二为一
        self.statusDict = statusDict # 棋子状态栏
        self.movingSpeed = moving_speed
        self.onField = False

        self.attack_counter:int = 0 # take track of when this chess can attack
        if self.skill is not None:
            self.cd_counter:int = int(self.skill.initialCD*100)
        else:
            self.cd_counter:int = 0 # take track of when this chess can cast spell
        
        # for test purposes
        self.totalDamageReceived: float = 0
        self.totalDamage:float = 0
        self.totalAttackDamage:float = 0
        self.deathTime: float = 0

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
    def reset(self, test = False):
        
        self.isDead = False
        self.resetPosition()
        self.resetHealth()
        self.resetStatus()
        self.cd_counter = 0
        self.attack_counter = 0
        # print(self,f"被重置了，位置为{self.position},血量为{self.health}/{self.maxHP}")

    def resetStatus(self):
        for statusName in self.statusDict.keys():
            self.statusDict[statusName] = None

    def resetHealth(self):
        self.health = deepcopy(self.maxHP)

    def resetPosition(self):
        self.position = deepcopy(self.initialPosition)

    def setInitialPosition(self, position):
        self.initialPosition = position
        self.resetPosition()

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
        '''
        判断在攻击范围内有无敌方单位
        '''
        try:
            if sorted(self.opponent_distances())[0] <= self.attack_range:
                return True
        except: 
            return False

        return False


    def can_attack(self) -> bool:
        '''判定棋子是否可以攻击, attack_interval 100 = 1 秒'''

        if self.statusDict['stunned'] is None and \
            self.statusDict['hexed'] is None and \
            self.statusDict['silenced'] is None and \
            self.statusDict['moving'] is None:
            return self.attack_counter >= self.attack_interval
    
    def enemy_in_cast_range(self) -> bool:
        '''
        判断在施法范围内有无敌方单位
        '''
        if self.skill is None:
            return False
        if hasattr(self.skill,'castRange'):
            try:
                if sorted(self.opponent_distances())[0] <= self.skill.castRange:
                    return True
            except: 
                return False
             
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
        for (statusID, status) in self.statusDict.copy().items():
            if status is not None:
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

    def check_death(self, currentTime: int) -> bool:
        '''
        检查当前棋子是否死亡，并且做出相应操作
        '''
        if self.isDead:
            return True
        else:
            if self.health <= 0:
                self.deathTime = currentTime
                # remove this chess from opponent's team list
                print()
                print(f"    {self} 已经被打败!")
                print()
                self.isDead = True # 标记死亡
                self.position=[-1,-1] # 移除棋盘
                del self.teamDict[self.uniqueID]
                return True
            else:
                return False

    def calculate_attack_damage(self, attack:float, opponent: chessInterface):
        return attack * (1 - opponent.armor*0.09/(1+0.09*opponent.armor)) * 2

    def do_attack(self,
            opponent: chessInterface,
            currentTime: int,
            coefficient: float = 1.0) -> float:
        """在棋子需要攻击的时候调用这个方法，这个方法会计算伤害，调用 deal_damage_to()方法造成伤害,并且打印attack info。
        
           返回：
                返回造成的伤害: float
        Args:
            opponent (chessInterface): _description_
            currentTime (int): _description_
            coefficient (float, optional): _description_. Defaults to 1.0.
        """
        self.attack_counter = 0
        if random.random() < opponent.evasion:
            print(currentTime/100, f" <{self}> 攻击了<{opponent}>,但是被闪避了。")
            return 0
        damage = self.calculate_attack_damage(attack = self.attack*coefficient, opponent=opponent)
        self.print_attack_info(opponent,currentTime,damage)
        self.deal_damage_to(opponent=opponent,
                            damage= damage,
                            currentTime=currentTime)
        return damage

    def print_attack_info(self,opponent: chessInterface, currentTime: int, damage: float):
        print(currentTime/100,f"<{self}> 攻击了<{opponent}>, 造成了{colored(damage,'cyan')}点伤害，<{opponent}>生命值还剩:{colored(opponent.health-damage,'green')} / {opponent.maxHP}") 
    
    def deal_damage_to(self,
                       opponent: chessInterface,
                       damage: float,
                       currentTime: int) -> bool:
        """这个方法只造成伤害，伤害是在调用这个方法之前就算好的。这个方法不改变任何值输入值，只改变目标血量和判定特殊情况。
            
            返回True 如果棋子受伤害后死亡，返回False 如果不是
        Args:
            opponent (chessInterface): _description_
            damage (float): _description_
            currentTime (int): _description_
        """
        if opponent.isDead:
            return True
        if self.id in {2,6,7,14,15,16,17,25,26} and opponent.id == 12: # 自己如果是虫，对方如果是犀牛，就减少自己对其造成的伤害
            damage = damage * (1-opponent.skill.reductionRate)
        if opponent.statusDict['vulnerable'] is not None:
            damage = damage * ((opponent.statusDict['vulnerable'].amplification) + 1)
        opponent.health -= damage
        opponent.totalDamageReceived += damage
        self.totalDamage += damage
        # check receiver status (比如对手是海胆, id=9，就需要查看对方是否有反伤开启，对手是犀牛，就查看自己是否是昆虫等)
        if self.id != 9 and opponent.id == 9 and \
            opponent.statusDict['dispersion_status'] is not None:
            # 如果两个海胆在场上，会有无限loop 的情况 所以加一个条件
            opponent.statusDict['dispersion_status'].activate(currentTime=currentTime,
                                                              target = self,
                                                              damage = damage)
        if opponent.check_death(currentTime = currentTime):
            return True
        else:
            return False
        

    def heal(self, amount)->None:
        '''
        当棋子进行治疗的时候调用这个方法
        '''
        final_health = self.health + amount
        if final_health >= self.maxHP:
            self.health = self.maxHP
        else:
            self.health = final_health
        print(f"    {self}受到{colored(amount, 'green')}点治疗，的生命值恢复到了{colored(self.health, 'green')} / {self.maxHP}")

    def moveChessTo(self, currentTime:int,  newPosition: list[int]):
        '''
        在棋子需要移动的时候调用这个方法, 来激活moving状态
        '''
        self.position = newPosition
        self.statusDict['moving'].activate(currentTime=currentTime)

    def get_surrounding(self, searchingRange:int = 1) -> list[list[int]]:
        '''
        range 是n*n 的范围，而不是圈的范围，可以做优化 TODO
        
        return:
            所有符合这个范围的，在棋盘之内的格子 list(position), 不会返回棋子
        '''
            # select (range*2+1)^2 area around self
        surrounding:list[list[int]] = []
        for row in range(self.position[0] - searchingRange, self.position[0] + searchingRange+1):
            for col in range(self.position[1] - searchingRange, self.position[1] + searchingRange+1):
                if row in range(6) and col in range(5):
                    surrounding.append([row, col])
        return surrounding
    
    def get_ali_distances(self) -> list[tuple[list, chessInterface]]:
        """返回一个 (position, chessInterface) 的tuple list

        Returns:
            list[tuple[list, chessInterface]]: _description_
        """
        return [(chess.position, chess) for chess in self.teamDict.values()]
            

    def opponent_ids(self) -> list[int]:
        '''返回所有对方棋子的id的 list'''
        return [uniqueID for (uniqueID,chess) in self.allChessDict.items() if chess.team != self.team]

    def opponent_distances(self) -> dict[float, chessInterface]:
        '''返回所有对方棋子的直线距离和chess的 dict'''
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
                        distance[curr_pos[0]][curr_pos[1]] = step
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
        这个方法意在找到当前棋子的下一个攻击对象,判定方式是直线距离
        '''
        opponents_distances = self.opponent_distances()
        nearest = sorted(opponents_distances)[0]
        chessToBeAttacked = opponents_distances[nearest]
        return chessToBeAttacked
    

    def get_enemy(self,board:list[list[chessInterface]])->dict[str, any]:
        '''
        返回棋子 移动距离最近的敌人\n
        {target_distance:移动距离,\n 
        target_position:目标位置,\n
        target:目标,\n
        direction:方向}
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
            # queue.put({'step':1, 'pos':[source_pos[0]-1,source_pos[1]], 'direction':'up'}) # 上 
            # queue.put({'step':1, 'pos':[source_pos[0]+1,source_pos[1]], 'direction':'down'}) # 下
            # queue.put({'step':1, 'pos':[source_pos[0],source_pos[1]-1], 'direction':'left'}) # 左
            # queue.put({'step':1, 'pos':[source_pos[0],source_pos[1]+1], 'direction':'right'}) # 右
            directions = [{'pos':[source_pos[0]-1,source_pos[1]], 'direction':'up'},
                          {'pos':[source_pos[0]+1,source_pos[1]], 'direction':'down'},
                          {'pos':[source_pos[0],source_pos[1]-1], 'direction':'left'},
                          {'pos':[source_pos[0],source_pos[1]+1], 'direction':'right'}]
            while directions: # 路径探索方向随机化
                pos_direction = directions.pop(random.randrange(len(directions)))
                queue.put({'step':1, 'pos':pos_direction['pos'], 'direction':pos_direction['direction']})

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
                            # queue.put({'step':step + 1, 'pos':[curr_pos[0]-1,curr_pos[1]], 'direction':direction}) # 上
                            # queue.put({'step':step + 1, 'pos':[curr_pos[0]+1,curr_pos[1]], 'direction':direction}) # 下
                            # queue.put({'step':step + 1, 'pos':[curr_pos[0],curr_pos[1]-1], 'direction':direction}) # 左
                            # queue.put({'step':step + 1, 'pos':[curr_pos[0],curr_pos[1]+1], 'direction':direction}) # 右
                            directions = [{'pos':[curr_pos[0]-1,curr_pos[1]]},
                                        {'pos':[curr_pos[0]+1,curr_pos[1]]},
                                        {'pos':[curr_pos[0],curr_pos[1]-1]},
                                        {'pos':[curr_pos[0],curr_pos[1]+1]}]
                            while directions: # 路径探索方向随机化
                                pos_direction = directions.pop(random.randrange(len(directions)))
                                queue.put({'step':step + 1, 'pos':pos_direction['pos'], 'direction':direction})

                    elif chess.team != self.team: # 发现距离棋子 移动距离最近 的敌方棋子
                        return {'target_distance':step, 'target_position':curr_pos, 'target':chess, 'direction':direction}
                except IndexError: # 寻路超出棋盘范围
                    continue
                except Empty: # queue为空
                    break
            return {'target_distance':None, 'target_position':None, 'target':None, 'direction':None}
        return bfs_queue(self.position)


    def move_to(self,
            direction: str,
            currentTime: int) -> None:
        '''
        棋子往{direction}方向移动一格
        '''
        new_pos = {
            'up':lambda x,y: [x-1,y],
            'down':lambda x,y: [x+1,y],
            'left':lambda x,y: [x,y-1],
            'right':lambda x,y: [x,y+1]
        }
        self.moveChessTo(currentTime=currentTime,newPosition=new_pos[direction](self.position[0],self.position[1]))
        self.print_move_info(direction,currentTime)

    def start_moving(self, currentTime:int, board:list[list[chessInterface]], moving):
        '''
        棋子开始移动
        '''
        action = self.get_enemy(board)
        if action['target_distance'] is not None and action['target_distance'] > self.attack_range: # TODO 
            self.statusDict['moving'] = moving(statusOwner=self, 
                                                currentTime=currentTime, 
                                                newPosition=action['target_position'])
            self.move_to(action['direction'],currentTime=currentTime)

    def print_move_info(self,direction: str, currentTime: int):
        print(currentTime/100,f"<{self}>向<{direction}> 移动了一格") 
