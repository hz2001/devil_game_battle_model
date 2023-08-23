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
                self.chessOnField = [guardDevil(position = positions[0]),trollDevilMelee(position = positions[0]),guardDevil(position = positions[2]),
                                     trollDevilRanged(position = positions[0]),trollDevilRanged(position = positions[0]),
                                     trollDevilSupplier(position = positions[0])]
            case 8:
                self.chessOnField = [devilDragon(position = [4,2])] 
                
            case 10:
                self.chessOnField = [] # ???
                
        return deepcopy(self.chessOnField)

    

class game:
    def __init__(self) -> None:
        self.players: dict[int, Player] = {} # int is the playerID 
        self.chessLists: dict[int, list[chessInterface]] = {} # int is the playerID 
        self.playerID = 0
        self.turn = 0
        self.alivePlayers: list[int] = [] # 记录存活玩家的id
        self.NPC = {1: None, 2: None, 3: None, # preparing turns
                    4: None, 6: None, 8: None, 10: None} # devil turns  
    
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
        self.players[self.playerID].printStatus()
        self.alivePlayers.append(self.playerID)
        self.playerID += 1
        
    def findOpponent(self, playerID):
        potential = []
        for target in self.alivePlayers:
            if target != playerID:
                potential.append(target)
        opponentID = randint(0,len(potential))
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
        newChess.position = [row, col]
        return newChess
    
    def flipAllChess(self, chessList) -> list[chessInterface]:
        chessOnFieldAsOpponent:list[chessInterface] = []
        for chess in chessList:
            chessOnFieldAsOpponent.append(self.flipChessPosition(chess))
        return chessOnFieldAsOpponent

    def battleOf2(self, homePlayerID, guestPlayerID):
        # playerID1 是主场玩家，playerID2是客场玩家 只有主场玩家输才会掉血
        redTeam = self.flipAllChess(self.chessLists[guestPlayerID])
        blueTeam = self.chessLists[homePlayerID]
        newBattle = battle()
        newBattle.addRedTeam(redTeam= redTeam)
        newBattle.addBlueTeam(blueTeam= blueTeam)
        wonTeam, damage, current_time = newBattle.battle_with_skills()
        if wonTeam == 'red': # 客场胜利
            wonPlayerID = guestPlayerID
            losePlayerID = homePlayerID
        elif wonTeam == 'blue':
            wonPlayerID = homePlayerID
            losePlayerID = guestPlayerID        
        if guestPlayerID == 666:
            damage = 100
        self.deal_damage_to(playerID = wonPlayerID, receiverID= losePlayerID, damage = damage) 
    

    def deal_damage_to(self, playerID, receiverID,damage,coefficient = 1):
        print(f"玩家{receiverID}受到 {damage*coefficient} 点伤害")
        self.players[receiverID].hp -= damage * coefficient
        if self.players[receiverID].check_death():
            self.players.pop(receiverID)
            print(f'玩家{receiverID}已被淘汰！')

    def devil_game(self):
        """魔鬼游戏主体"""
        print("开始匹配")
        playerNumber = 0
        while playerNumber < 2 or playerNumber > 4:
            playerNumber = int(input("加入几位玩家？(2-4)"))
            for i in range(playerNumber):
                self.add_player()
            print("所有人都已就位")
            if playerNumber < 2 or playerNumber > 4:
                input("格式不正确，输入任何值继续...")
            
        print("战斗开始")
        # 回合阶段
        while len(self.alivePlayers) > 2 or self.turn < 10:
            self.turn += 1
            # 准备阶段
            for playerID in range(self.playerID):
                self.chessLists[playerID] = self.players[playerID].new_turn()
            # 锁定回合，战斗阶段
            match self.turn:
                case 1:
                    for player in self.alivePlayers:
                        opponent = self.NPC[1]
                        self.battleOf2()
                case 2:
                    pass
                case 3:
                    pass
                case 4:
                    pass
                case 6:
                    pass
                case 8:
                    pass
                case 10:
                    pass
                case _:
                    pass
            self.chessLists: dict[int, Player] = [] # 重置
                


                # 战斗阶段
                # 分配战斗