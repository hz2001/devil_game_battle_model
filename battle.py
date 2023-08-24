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
        技能判定:
            如果时间符合技能cd 那么call当前棋子的技能方法 并且判定攻击/受益对象
        攻击判定:
            进行攻击判定 掉血或者击杀对方棋子
        移动判定:
            判定当前棋子需要移动到什么位置 并且移动棋子 正在移动的棋子会有0.3秒攻击/技能滞后
    '''

    def __init__(self) -> None:
        self.redTeamDict:dict[int,chessInterface] = {}
        self.blueTeamDict:dict[int,chessInterface] = {}
        self.board:list[list[chessInterface]] = [[None,None,None,None,None],
                                        [None,None,None,None,None],
                                        [None,None,None,None,None],

                                        [None,None,None,None,None],
                                        [None,None,None,None,None],
                                        [None,None,None,None,None]]

        #  遗留物品，其实并不需要这个作为判定手段，因为有更简单的判定方法
        self.redTeamDict:dict[int,chessInterface] = {}
        self.blueTeamDict:dict[int,chessInterface] ={}

        self.redTeamAliveNO:int = 0
        self.blueTeamAliveNO:int = 0

        self.allChessDict:dict[int,chessInterface] = {}
    def board_clear(self):
        """重置棋盘
        """
        battle.board = [[None,None,None,None,None],
                    [None,None,None,None,None],
                    [None,None,None,None,None],

                    [None,None,None,None,None],
                    [None,None,None,None,None],
                    [None,None,None,None,None]]

    def addRedTeam(self, redTeam:list[chessInterface]):
        for chess in redTeam:
            chess.team = 0
            self.redTeamDict[chess.uniqueID] = chess
            self.redTeamAliveNO += 1
            self.add_chess_to_board(chess,finished= False)
            self.allChessDict[chess.uniqueID] = chess
            chess.add_team_dict(self.redTeamDict)
            chess.add_allChessDict(self.allChessDict)
        
    def addBlueTeam(self, blueTeam:list[chessInterface]):
        for chess in blueTeam:
            chess.team = 1 # 把棋子的阵营改成蓝色方
            self.blueTeamAliveNO += 1
            self.blueTeamDict[chess.uniqueID] = chess
            self.add_chess_to_board(chess,finished= False)
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

    def add_chess_to_board(self, chessToBeAdded: chessInterface, finished = True):
        '''检测棋子的位置是否为正确位置，并且把新建棋子放在棋盘上'''

        if finished == False:
            row = chessToBeAdded.initialPosition[0]
            col = chessToBeAdded.initialPosition[1]
            if self.board[row][col] is not None:
                if self.board[row][col] == chessToBeAdded:
                    return
                raise Exception(f"{chessToBeAdded}的位置已被{self.board[row][col]}占据，请更换位置后重试") 
            if chessToBeAdded.team == 0 and chessToBeAdded.initialPosition[0]>=3:
                print(chessToBeAdded.initialPosition)
                raise Exception(f"请把红方棋子{chessToBeAdded}放置在前三排") 
            elif chessToBeAdded.team == 1 and chessToBeAdded.initialPosition[0] <=2:
                print(chessToBeAdded.initialPosition)
                raise Exception(f"请把蓝方棋子{chessToBeAdded}放置在后三排") 
        else:
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
                    self.board[row][col] = None
                    showNewBoard = True
                    break
                elif self.board[row][col] is None and \
                    [row,col] == chessToBeMoved.position and \
                    'summoned' in chessToBeMoved.statusDict.keys():
                    showNewBoard = True
                    # 说明有棋子被召唤需要更新棋盘
                    break

        if currentPosition != [-1,-1] and showNewBoard:
            # 说明棋子没死，从新把棋子添加回棋盘
            self.add_chess_to_board(chessToBeAdded=chessToBeMoved)
        else:
            # 棋子死掉了，不重新添加棋子
            # showNewBoard = False
            pass
        if showNewBoard:
            self.board_print()
            pass
    
    # 对战
    def battle_with_skills(self):
        self.board_print()
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
                if attackerChess.enemy_in_cast_range():
                    if attackerChess.can_cast(): # 技能判定
                        # 是时候放技能了！
                        attackerChess.cast(currentTime=current_time)
                if attackerChess.enemy_in_attack_range(): # 如果敌人在攻击范围内则不移动
                    if attackerChess.can_attack(): # 攻击判定
                        opponent = attackerChess.get_hate_mechanism()
                        attackerChess.do_attack(currentTime=current_time, opponent=opponent)
                elif attackerChess.can_move(): # 移动判定
                    attackerChess.start_moving(currentTime= current_time, board = self.board,moving=moving)
                    self.update_chess_position_onboard(chessToBeMoved=attackerChess)
                        # self.board_print()
        if self.teamAlive(self.redTeamDict):
            print(f"{colored('红','red')}方获胜!")
            wonTeam = 'red'
        else:
            print(f"{colored('蓝','blue')}方获胜!")
            wonTeam = 'blue'
        
        # 判定玩家掉血
        damage = 0
        for row in self.board:
            for slot in row:
                if slot is not None:
                    damage += 1 
        
        # self.board_print()
        # for uniqueID, chess in self.allChessDict.items():
        #     print(chess, chess.getTotalDamageDealt())
        # reset everything 
        for uid, chess in self.allChessDict.items():
            chess.reset()
        self.board_clear()
        # return the won team 
        return wonTeam, damage, current_time
        
    def battle_with_skills_test(self):
        # 对战测试版，会记录棋子的详细信息
        # self.board_print()
        current_time = 0
        while self.teamAlive(self.redTeamDict) and self.teamAlive(self.blueTeamDict):
            current_time += 5
            if current_time > 6000:
                return 0, current_time

            for (attackerID, attackerChess) in self.allChessDict.copy().items():
                if self.update_chess_position_onboard(chessToBeMoved=attackerChess):
                    # print(self.board_print())
                    pass
                if attackerChess.isDead:
                    
                    continue
                # print(current_time/100, attackerChess, id(attackerChess.statusDict))
                # 根据时间更新剩余间隔
                attackerChess.attack_counter += 5
                attackerChess.cd_counter += 5
                # 进行状态判定
                attackerChess.activate_status(currentTime=current_time)
                #进行仇恨判定
                # opponentDict = self.get_opponent_dict(attackerChess)
                if attackerChess.enemy_in_cast_range():
                    if attackerChess.can_cast(): # 技能判定
                        # 是时候放技能了！
                        attackerChess.cast(currentTime=current_time)
                if attackerChess.enemy_in_attack_range(): # 如果敌人在攻击范围内则不移动
                    if attackerChess.can_attack(): # 攻击判定
                        opponent = attackerChess.get_hate_mechanism()
                        attackerChess.totalAttackDamage += attackerChess.do_attack(currentTime=current_time, opponent=opponent)
                elif attackerChess.can_move(): # 移动判定
                    attackerChess.start_moving(currentTime= current_time, board = self.board,moving=moving)
                    self.update_chess_position_onboard(chessToBeMoved=attackerChess)
                        # self.board_print()
        if self.teamAlive(self.redTeamDict):
            wonTeam = 0
            # print(f"{colored('红','red')}方获胜!")
        else:
            wonTeam = 1
            # print(f"{colored('蓝','blue')}方获胜!")
        # print the board after the battle
        # self.board_print()

        # reset everything 
        for uid, chess in self.allChessDict.items():
            chess.reset()
        self.board_clear()
        # return the won team 
        return wonTeam, current_time

# def main():
#     newBattle = battle()
#     # redTeam = [ladybug(position=[0,0]),turtle(position=[0,1]),butterfly(position=[0,3]),
#     #            mantis(position=[1,4]),unicorn_b(position=[2,4])]
#     # blueTeam = [tiger(position=[3,3]),
#     #             anglerfish(position=[4,0]),hippo(position=[4,2]),
#     #            bee(position=[5,2]),fireworm(position=[5,4])]
#     redTeam = [octopus(position = [2,2])]
#     blueTeam = [fireworm(position = [3,0]),fireworm(position = [3,1]),fireworm(position = [4,3]),fireworm(position = [5,4])]


#     newBattle.addRedTeam(redTeam)
#     newBattle.addBlueTeam(blueTeam)
#     # newBattle.battle_between_2(newBattle.redTeamChess[0], newBattle.blueTeamChess[0])
#     newBattle.battle_with_skills()

# if __name__ == '__main__':
#     main()