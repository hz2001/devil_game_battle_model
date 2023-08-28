from player import Player
from battle import * 
# from random import randint

class devil(Player):
    def __init__(self, id = 666) -> None:
        super().__init__(id)
        buffList = ['fast_attack', 'spell_amp', 'vulnerable_attack', 'blood_drain', 'electrify']
        self.buffs = buffList[randint(0, len(buffList))] # 开发这个buff 状态
    def findRandPositions(self, rowRange, colRange, count:int):
        positions = []
        while len(positions) < count:
            pos = [randint(low = rowRange[0],high=rowRange[1]),randint(low=colRange[0],high=colRange[1])]
            if pos not in positions:
                positions.append(pos)
        return positions

    def getChessList(self, turn:int ):
        match turn:
            case 1:
                self.chessOnField = [minionDevil(position = [4,2])]
                print("get chess from devil, id = ",self.chessOnField[0].uniqueID)
            case 2:
                self.chessOnField = [minionDevil(position = [4,1]),
                                     minionDevil(position = [4,3])]
            case 3:
                # 找到两个随机位置放置怪物
                positions = self.findRandPositions(rowRange=[3,5], colRange=[0,4], count=2)
                self.chessOnField = [guardDevil(position = positions[0]),
                                     minionDevil(position = positions[1])]
            # 魔鬼关卡
            case 4:
                # 数值比较高的三个怪，随机位置生成，数值基本上匹配3个强化版的2星棋子
                positions = self.findRandPositions(rowRange=[3,5], colRange=[0,4], count=3)
                self.chessOnField = [guardDevil(position = positions[0]),
                                     guardDevil(position = positions[1]),
                                     guardDevil(position = positions[2])]
            case 6:
                # 2小怪，1大怪挡在前面，以及2个输出大怪，输出大怪的攻击速度很快，前面两个大怪会增加所有怪物的护甲。
                positions = [[3,0],[3,2],[3,4], # 小前排，大前排，小前排
                             [4,1],[4,3], # 输出，输出
                             [5,2]] # 辅助
                self.chessOnField = [guardDevil(position = positions[0]),trollDevilMelee(position = positions[1]),guardDevil(position = positions[2]),
                                     trollDevilRanged(position = positions[3]),trollDevilRanged(position = positions[4]),
                                     trollDevilSupplier(position = positions[5])]
            case 8:
                self.chessOnField = [devilDragon(position = [4,2])] 
            case 10:
                self.chessOnField = [] # ???
            case _ :
                return None
                
        return deepcopy(self.chessOnField)

    

class game:
    def __init__(self) -> None:
        self.players: dict[int, Player] = {} # int is the playerID 
        self.chessLists: dict[int, list[chessInterface]] = {} # int is the playerID 
        self.playerID = 0
        self.turn = 0
        self.alivePlayers: list[int] = [] # 记录存活玩家的id
        self.devil = devil()
        self.devilChessListOnTurn = {1: self.devil.getChessList(1), 
                    2: self.devil.getChessList(2), 
                    3: self.devil.getChessList(3), # preparing turns
                    
                    4: self.devil.getChessList(4), 
                    6: self.devil.getChessList(6), 
                    8: self.devil.getChessList(8), 
                    10: self.devil.getChessList(10)} # devil turns  
    
    def check_wonPlayer(self) -> int:
        alivePlayerCounter = 4
        alivePlayer = -1
        for i in range(self.playerID):
            if self.players[i].check_death():
                alivePlayerCounter -= 1
            else:
                alivePlayer = i
        if alivePlayerCounter < 2:
            return alivePlayer
        else:
            return None
        
    def add_player(self):
        self.players[self.playerID] = Player(id = self.playerID)
        print(self.players[self.playerID], "加入成功。")
        self.alivePlayers.append(self.playerID)
        self.playerID += 1
        
    def findOpponent(self, playerID):
        potential = []
        for targetID in self.alivePlayers:
            if targetID != playerID:
                potential.append(targetID)
        opponentID = potential[randint(0,len(potential))]
        return opponentID

    def flipChessPosition(self, chess:chessInterface) -> chessInterface:
        """ 拿一个棋子，返回这个棋子作为客场棋子的复制体

        Args:
            chess (chessInterface): 一个棋子

        Returns:
            chessInterface: 返回一个输入棋子的复制，位置由主场切换为客场
        """
        position = chess.position
        row = 5-position[0]
        col = 4-position[1]
        newChess = deepcopy(chess)
        newChess.setInitialPosition(position=[row, col])
        return newChess
    
    def flipAllChess(self, chessList) -> list[chessInterface]:
        chessOnFieldAsOpponent:list[chessInterface] = []
        for chess in chessList:
            chessOnFieldAsOpponent.append(self.flipChessPosition(chess))
        return chessOnFieldAsOpponent

    def battleOf2(self, homePlayerID, guestPlayerID):
        # playerID1 是主场玩家，playerID2是客场玩家 只有主场玩家输才会掉血
        if guestPlayerID != 666:
            redTeam = self.chessLists[guestPlayerID]
        else:
            redTeam = self.devilChessListOnTurn[self.turn]

        # print(f"主场:{homePlayerID}")
        # print(f"客场:{guestPlayerID}")
        redTeam = self.flipAllChess(redTeam)
        blueTeam = self.chessLists[homePlayerID]
        # print(blueTeam)
        # print(redTeam)
        newBattle = battle()
        newBattle.addRedTeam(redTeam= redTeam)
        newBattle.addBlueTeam(blueTeam= blueTeam)
        newBattle.board_print()
        # print(newBattle.blueTeamDict)
        # print(newBattle.redTeamDict)
        # print(newBattle.allChessDict)
        wonTeam, damage, current_time = newBattle.battle_with_skills()
        if wonTeam == 'red': # 客场胜利
            wonPlayerID = guestPlayerID
            losePlayerID = homePlayerID
            if guestPlayerID == 666 and self.turn>=4:# 只有第四回合之后才会直接死掉
                damage = 100
            return self.deal_damage_to(playerID = wonPlayerID, receiverID= losePlayerID, damage = damage) 
        elif wonTeam == 'blue':
            # 主场胜利，不掉血，啥也不干
            wonPlayerID = homePlayerID
            losePlayerID = guestPlayerID        
            return False

    def deal_damage_to(self, playerID, receiverID,damage,coefficient = 1):
        print(f"玩家{receiverID}受到 {damage*coefficient} 点伤害")
        self.players[receiverID].hp -= damage * coefficient
        if self.players[receiverID].check_death():
            self.players.pop(receiverID)
            self.alivePlayers.remove(receiverID)
            print(f'玩家{receiverID}已被淘汰！',"依然存活的玩家有：",self.players)
            return True
        return False

    def devil_game(self):
        """魔鬼游戏主体"""
        print("开始匹配")
        playerNumber = 0
        while playerNumber not in ['2','3','4']:
            playerNumber = input("加入几位玩家？(2-4)")
            if playerNumber not in ['2','3','4']:
                print("格式不正确，请重新输入...")
                continue
        for i in range(int(playerNumber)):
            self.add_player()
            
        print("所有人都已就位")
        print("战斗开始")
        # 回合阶段
        while len(self.alivePlayers) >= 2 and self.turn < 10:
            self.turn += 1
            input(f"当前回合：{self.turn}, 按下任意键继续 \n")
            # 准备阶段
            for playerID,player in self.players.items():
                self.chessLists[playerID] = player.new_turn(turn = self.turn)
            # 锁定回合，战斗阶段
            match self.turn:
                case 1 | 2 | 3:
                    for playerID in self.alivePlayers:
                        print()
                        print("_____________________________战斗分割线________________________________")
                        input(f"当前战斗:{self.players[playerID]},客场:《魔鬼》按下任意键开始战斗\n")
                        self.battleOf2(playerID,666)
                case 4 | 6 | 8 | 10:
                    # 选人
                    playerChoiceID = self.alivePlayers[randint(0,len(self.alivePlayers))]
                    print(f"玩家{playerChoiceID}被恶魔选中了，祝你好运")
                    for playerID in self.alivePlayers:
                        if playerID != playerChoiceID:
                            opponentID = self.findOpponent(playerID=playerID)
                        else:
                            opponentID = 666
                        print()
                        print("_____________________________战斗分割线________________________________")
                        input(f"当前战斗:{self.players[playerID]},客场:玩家{opponentID}按下任意键开始战斗\n")
                        self.battleOf2(playerID,opponentID)
                case _: # 玩家对战
                    for playerID in self.alivePlayers:
                        opponentID = self.findOpponent(playerID=playerID)
                        print()
                        print("_____________________________战斗分割线________________________________")
                        input(f"当前战斗:{self.players[playerID]},客场:玩家{opponentID}按下任意键开始战斗\n")
                        self.battleOf2(playerID,opponentID)
            self.chessLists: dict[int, Player] = {} # 重置
        print(self.alivePlayers,"胜出")
        
        
def main():
    newGame = game()
    newGame.devil_game()

if __name__ == '__main__':
    main()