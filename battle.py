# This Python file uses the following encoding: utf-8
#  目标是计算出自走棋一回合的时间是多少

from math import dist, ceil, floor
from termcolor import colored
from chess_info import *

class battle:
    '''
    主循环流程
        每一次判定顺序: 状态判定--仇恨判定--移动判定--攻击/技能 判定 -- 被攻击者技能判定
        进攻方判定:
            根据一个随机条件 判定先接受判定的队伍
        状态判定:
            根据当前棋子的状态 计算棋子属性/将会掉的血量/
        施法仇恨判定:
            判定下一次攻击/施法的单位是什么 如果攻击范围内有敌人 就跳过移动判定 否则进行移动判定
        移动判定:
            判定当前棋子需要移动到什么位置 并且移动棋子 正在移动的棋子会有0.3秒攻击/技能滞后
        技能判定:
            如果时间符合技能cd 那么call当前棋子的技能方法 并且判定攻击/受益对象
        攻击判定:
            进行攻击判定 掉血或者击杀对方棋子
        被攻击者判定:
            如果被攻击者是<海胆> 这种被攻击触发技能 那么需要判定其状态 技能是否为开启状态
            如果攻击者是<蝎子> 这种带有攻击特效的棋子 那么给被攻击者施加相应状态
    '''
    board:list[list[chessInterface]] = [[None,None,None,None,None],
                                        [None,None,None,None,None],
                                        [None,None,None,None,None],

                                        [None,None,None,None,None],
                                        [None,None,None,None,None],
                                        [None,None,None,None,None]]

    #  遗留物品，其实并不需要这个作为判定手段，因为有更简单的判定方法
    redTeamDict:dict[int,chessInterface] = {}
    blueTeamDict:dict[int,chessInterface] ={}

    redTeamAliveNO:int = 0
    blueTeamAliveNO:int = 0

    allChessDict:dict[int,chessInterface] = {}

    def __init__(self) -> None:
        self.redTeamDict:dict[int,chessInterface] = {}
        self.blueTeamDict:dict[int,chessInterface] = {}

    def addRedTeam(self, redTeam:list[chessInterface]):
        for chess in redTeam:
            chess.team = 0
            self.redTeamDict[chess.uniqueID] = chess
            self.redTeamAliveNO += 1
            self.add_chess_to_board(chess)
            self.allChessDict[chess.uniqueID] = chess
            chess.add_team_dict(self.redTeamDict)
            chess.add_allChessDict(self.allChessDict)
        
    def addBlueTeam(self, blueTeam:list[chessInterface]):
        for chess in blueTeam:
            chess.team = 1 # 把棋子的阵营改成蓝色方
            self.blueTeamAliveNO += 1
            self.blueTeamDict[chess.uniqueID] = chess
            self.add_chess_to_board(chess)
            self.allChessDict[chess.uniqueID] = chess
            chess.add_team_dict(self.blueTeamDict)
            chess.add_allChessDict(self.allChessDict)
    # 通用方法
    def get_opponent_dict(self, chess:chessInterface) -> dict[int, chessInterface]:
        '''根据棋子的阵营找到对方阵营'''
        if chess.team == 0:
            return self.blueTeamDict
        else:
            return self.redTeamDict

    def teamAlive(self, team:dict[int,chessInterface],empty:dict[int,chessInterface] = {}):
        '''如果一方的全部棋子都被移除，那么这一方就输掉这一回合的战斗，反之，这只队伍就还能战斗，战斗继续'''
        return team != empty

    # 棋盘设定/
    # 棋盘
    # [ [0,0] [0,1] [0,2] [0,3] [0,4] ]
    # [ [1,0] [1,1] [1,2] [1,3] [1,4] ]
    # [ [2,0] [2,1] [2,2] [2,3] [2,4] ]
    # [ [3,0] [3,1] [3,2] [3,3] [3,4] ]
    # [ [4,0] [4,1] [4,2] [4,3] [4,4] ]
    # [ [5,0] [5,1] [5,2] [5,3] [5,4] ]

    def add_chess_to_board(self, chessToBeAdded: chessInterface):
        '''把新建棋子放在棋盘上'''
        row = chessToBeAdded.position[0]
        col = chessToBeAdded.position[1]
        self.board[row][col] = chessToBeAdded

    def clear_position(self, position: list[int]):
        self.board[position[0]][position[1]] = None

    def board_print(self):
        '''打印当前棋盘'''
        print()
        for row in self.board:
            print(f"{[chess for chess in row]}")
            print()
        print()

    def opponent_distances(self, attacker:chessInterface):
        '''返回所有对方棋子的距离和id的 tuple'''
        enemyDict = self.get_opponent_dict(chess=attacker)
        return [(floor(abs(dist(attacker.position,
                                e.position))),uniqueID) for (uniqueID,e) in enemyDict.items()]

    # 位置判定
    def update_chess_position_onboard(self, chessToBeMoved: chessInterface) -> None:
        '''
        棋盘更新方法
        在这个方法里不可以修改棋子本身的位置信息，而是根据现在棋子的位置属性更新棋盘，棋子位置的变更应该由棋子自身完成，而不是战斗功能完成
        '''
        currentPosition = chessToBeMoved.position
        # print(chessToBeMoved)
        # print(currentPosition)
        showNewBoard = False
        # if self.board[position[0]][position[1]] is None:
        # 不存在位置没有孔雀开屏的情况因为移动的时候已经判定过了，现在只是更新棋盘
        # 移除之前的棋子
        for row in range(6):
            for col in range(5):
                if self.board[row][col] is not None and \
                    self.board[row][col] == chessToBeMoved and \
                        [row, col] != chessToBeMoved.position: # means we need to remove
                    # print(self.board[row][col])
                    # print(chessToBeMoved)
                    # print(currentPosition)
                    # print(chessToBeMoved.position)
                    self.board[row][col] = None
                    showNewBoard = True
                    # print()
                    # print(self.board[row][col])
                    # print(currentPosition)
                    break
                elif self.board[row][col] is None and \
                    [row,col] == chessToBeMoved.position and \
                    'summoned' in chessToBeMoved.statusDict.keys():
                    # 说明有棋子被召唤需要更新棋盘
                    showNewBoard = True
                    break

        if currentPosition != [-1,-1] and showNewBoard:
            # 说明棋子没死，从新把棋子添加回棋盘
            self.add_chess_to_board(chessToBeAdded=chessToBeMoved)
        else:
            # 棋子死掉了，不重新添加棋子
            pass
        if showNewBoard:
            self.board_print()
            pass

    def get_hate_mechanism(self,attacker:chessInterface) ->int:
        '''
        这个方法意在找到当前棋子的下一个攻击对象
            返回值为敌方棋子库中的棋子uniqueID
        '''
        # TODO 重新计算目标距离
        # locate attacker on the board
        # attack the closest enemy in its range unless it has special target
        opponents_distances = self.opponent_distances(attacker)
        opponents_distances = sorted(opponents_distances)
        IDtoBeAttacked = opponents_distances[0][1]
        # 如果下两个棋子的距离相同导致优先级一样怎么办？那就看上次受到的伤害来自于谁
        # TODO: implement this
        # use 0.3 sec to move to the **empty** position where it can reach the next opponent,
        # if this enemy is not in the range of attack,


        return IDtoBeAttacked

    # 技能判定用棋子自身的方法

    # 攻击判定
    # 计算伤害的公式
    def calculate_attack_damage(self, attack, opponentArmor):
        return attack * (1 - opponentArmor*0.09/(1+0.09*opponentArmor)) * 2

    def chess_attack(self,
                     currentTime: int,
                     attacker:chessInterface,
                     opponent:chessInterface):
        '''棋子攻击时调用这个函数'''
        if attacker.team == 0:
            opponentTeamDict = self.blueTeamDict
            attackerDict = self.redTeamDict
        else:
            opponentTeamDict = self.redTeamDict
            attackerDict = self.blueTeamDict

        damage = self.calculate_attack_damage(attacker.attack, opponent.armor)
        attacker.deal_damage_to(opponent=opponent, amount=damage, currentTime = currentTime)
        if not isinstance(attacker, sea_hedgehog) and isinstance(opponent, sea_hedgehog) and \
            opponent.statusDict['dispersion_status'] is not None:
            # 如果两个海胆在场上，会有无限loop 的情况 所以加一个条件
            opponent.statusDict['dispersion_status'].activate(currentTime=currentTime,
                                                              target = attacker,
                                                              damage = damage)
        # TODO: 改成棋子自己攻击，而不是在这里攻击

    # 对战
    def battle_with_skills(self):
        current_time = 0
        while self.teamAlive(self.redTeamDict) and self.teamAlive(self.blueTeamDict):
            current_time += 5

            for (attackerID, attackerChess) in self.allChessDict.copy().items():
                if self.update_chess_position_onboard(chessToBeMoved=attackerChess):
                    # print(self.board_print())
                    pass
                if attackerChess.isDead:
                    # print("*****attacker is Dead, something is wrong")
                    continue
                # print(current_time/100, attackerChess, id(attackerChess.statusDict))
                # 根据时间更新剩余间隔
                attackerChess.attack_counter += 5
                attackerChess.cd_counter += 5
                # 进行状态判定
                attackerChess.activate_status(currentTime=current_time)
                #进行仇恨判定
                # opponentDict = self.get_opponent_dict(attackerChess)
                if attackerChess.can_cast(): # 技能判定
                    # 是时候放技能了！
                    attackerChess.cast(currentTime=current_time)
                    # TODO 漏洞：为了减小算法难度，计算对手状态的效果等到loop到该棋子的时候再完成，但是这样会导致如果有棋子在这之前对其发动攻击，则该伤害无法计算buff/debuff
                if attackerChess.can_attack(): # 攻击判定
                    opponent = attackerChess.get_hate_mechanism()
                    attackerChess.do_attack(currentTime=current_time, opponent=opponent)
                if attackerChess.can_move(): # 攻击判定
                    action = attackerChess.move(self.board)
                    if action['target_distance'] is not None and action['target_distance'] > 1:
                        attackerChess.statusDict['moving'] = moving(statusOwner=attackerChess, currentTime=current_time, newPosition=action['target_position'])
                        attackerChess.move_to(action['direction'],currentTime=current_time)
                        self.update_chess_position_onboard(chessToBeMoved=attackerChess)
                        # self.board_print()
        if self.teamAlive(self.redTeamDict):
            print(f"{colored('红','red')}方获胜!")
        else:
            print(f"{colored('蓝','blue')}方获胜!")
        # print(self.allChessDict)


def main():
    # tested:{sea_hedgehog(position = [3,3]), # 海胆， 熊，蜜蜂，羊，螳螂, 蝎子，麋鹿
    #                 bear(position=[3,4]),
    #                 bee(position = [4,4]),
    #                 mantis(position=[3,2]),
    #                 llama(position=[2,2]),
    #                 heal_deer(position = [1,2]), 
    #                 scorpion(position=[2,4])}
    # not_tested = {littleUglyFish(),
    #               ant(),
    #               hippo(),
    #               shark(),
    #               monkey(),
    #               ladybug(),
    #               wolf(),
    #               rabbit(),
    #               butterfly(), 
    #               octpus(), 
    #               swallower() }
    
    newBattle = battle()
    redTeam = [ant(position=[0,0]), 
               wolf(position =[1,0])]
    blueTeam = [hippo(position=[3,1]),ladybug(position=[4,4])]
    newBattle.addRedTeam(redTeam)
    newBattle.addBlueTeam(blueTeam)
    newBattle.board_print()
    # newBattle.battle_between_2(newBattle.redTeamChess[0], newBattle.blueTeamChess[0])
    newBattle.battle_with_skills()
    print(newBattle.board_print())
    for uniqueID, chess in newBattle.allChessDict.items():
        print(chess, chess.getTotalDamageDealt())

if __name__ == '__main__':
    main()