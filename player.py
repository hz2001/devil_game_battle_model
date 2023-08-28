from numpy.random import random, randint
from termcolor import colored
from util import *

cost1Card = [ant, littleUglyFish, rabbit]
cost2Card = [llama, wolf, ladybug, bee, swallow, sea_hedgehog]

class Player:
    def __init__(self, id) -> None:
        self.id = id
        self.turn:int = 1
        self.chesses: dict[int, chessInterface] = {}
        self.chessInHand: list[chessInterface] = [] # max Of 5 cards
        self.chessOnField:list[chessInterface] = []
        self.goldAvail = 1
        self.buffs = []
        self.population = 1
        self.turnToNextPop = 1
        self.goldToNextPop = 1
        self.cost2Chance = 0 # 抽到2星卡的概率
        self.hp = 100
        self.cardLock = False
        self.chessList = []
    def __eq__(a, b):
        return a.id == b.id

    def __repr__(self) -> str:
        color = 'red'
        if self.id == 0:
            color = 'red'
        elif self.id == 1: 
            color = 'blue'
        elif self.id == 2:
            color = 'green'
        elif self.id == 3:
            color = 'cyan'
        elif self.id == 666:
            color = 'black'
        return f"{colored('玩家'+str(self.id),color)}"
    
    def printStatus(self) -> None:
        print (f"\n" + \
            f"当前回合 {self.turn}, 剩余血量：{self.hp}\n" + \
            f"{self} 现在拥有 {colored(self.population,'green')} 人口，距离下次升级还需要{colored(self.turnToNextPop,'light_cyan')}回合，或者{colored(self.goldToNextPop*self.turnToNextPop,'light_cyan')}金钱；\n" + \
            f"现在拥有的棋子为{self.chesses}\n" + \
            f"备战区棋子：{self.chessInHand}，上场棋子{[(c, c.position) for c in self.chessOnField]}；\n"+ \
            f"当前回合还有可用金钱{colored(self.goldAvail, 'yellow')}；\n" + \
            f"玩家buff有{self.buffs}；\n")

    def next_turn(self):
        '''每回合开始阶段调用这个方法'''
        self.hp -= 10
        self.turn += 1
        self.goldAvail = deepcopy(self.turn)
        self.checkPopulationUpdate()      
        
    # 血量部分
    def check_death(self):
        if self.hp <= 0:
            return True
        else:
            return False 
      
    # 金钱部分
    def reduce_gold(self, howMuch, purpose: str):
        '''花钱的时候调用这个方法'''
        if self.goldAvail - howMuch >= 0:
            self.goldAvail -= howMuch
            print(self,purpose,f"{colored('成功','green')},共花费: ",howMuch," 金币，还剩 ",self.goldAvail," 金币。")
            return True
        else:
            print(self,purpose,f"{colored('失败','red')},需要: ",howMuch,' 金币，现有 ',self.goldAvail,f" 金币，差{howMuch - self.goldAvail}金币。")
            return False
        
    def checkPopulationUpdate(self):
        """检查人口是否上升"""
        self.turnToNextPop -= 1
        self.goldToNextPop -= self.population
        if self.turnToNextPop == 0:
            self.population += 1
            self.turnToNextPop = deepcopy(self.population)
            self.goldToNextPop = deepcopy(self.population) ** 2 # population 的平方
            print(f"玩家{self.id} 现在拥有 {colored(self.population,'green')} 人口，升级至下一人口还需要{colored(self.turnToNextPop,'light_cyan')}回合，或者 {colored(self.goldToNextPop*self.turnToNextPop,'light_cyan')} 金钱；\n")
        
    # 人口部分
    def upgrade_pop(self):
        """用金币升级人口"""
        if self.reduce_gold(purpose=f"升级人口", howMuch=self.population):
            self.checkPopulationUpdate()
        
    # 棋子部分
    def printChesses(self):
        print(self.chesses)
        
    def get_random_chess_to_draw(self):
        """每回合随机抽卡"""
        cardList = []
        for i in range(3):
            if random() < self.cost2Chance:
                cardList.append( cost2Card[randint(0,len(cost2Card))] )
            else:
                cardList.append( cost1Card[randint(0,len(cost1Card))] )
        # print(self,"本次选择有",cardList)
        self.chessList=  cardList

    def redraw(self):
        """重新抽卡"""
        if self.reduce_gold(purpose=f'刷新棋子', howMuch = 3):
            self.get_random_chess_to_draw()
        
    def checkChessID(self, chessID:int) -> chessInterface:
        """检查玩家所有棋子中有没有 这个unique id代表的棋子

        Args:
            chessID (int): _description_

        Raises:
            KeyError: _description_

        Returns:
            chessInterface: _description_
        """
        # print(chessID, type(chessID),self.chesses)
        try:
            chess = self.chesses[chessID]
        except:
            raise KeyError(f"{self}没有这张卡")
        return chess

    def get_chess(self,newChess: chessInterface, purchase = True):
        """购买棋子"""
        newChess.team = self.id
        if purchase is True:
            if self.reduce_gold(purpose=f"购买棋子{newChess}", howMuch=newChess.star):
                self.chessInHand.append(newChess)
                self.chesses[newChess.uniqueID] = newChess 
        else:
            print(self,f"通过升级获取了 <{newChess}>")
            self.chessInHand.append(newChess)
            self.chesses[newChess.uniqueID] = newChess 
            # self.printStatus()

    def sell_chess(self, chessID: int):
        """出售棋子"""
        chess = self.checkChessID(chessID=chessID)
        if chess.onField:
            self.chessOnField.remove(chess)
            self.goldAvail += chess.star # 玩家在升级四星之后，如果出售棋子只能获得一半的金钱，所以需要提前斟酌自己的阵容
            print(f"{self}:已被卖掉，从chessOnField and chesses中移除,{self}获得金钱{chess.star}，现在闲置金钱{self.goldAvail}")
        else:
            self.chessInHand.remove(chess)
            self.goldAvail += chess.star
            print(f"{self}:已被卖掉，从chessInHand and chesses中移除,{self}获得金钱{chess.star}，现在闲置金钱{self.goldAvail}")
        for (s, c) in self.chesses.items():
            if c == chess:
                break
        del self.chesses[s]
        # print(  f"       现在拥有的棋子为{self.chesses}")
        # print(  f"       备战区棋子：{self.chessInHand}，\n       上场棋子{[(c, c.position) for c in self.chessOnField]}；")
        
    def hand_to_field(self, chessID: int, position: list[int]):
        """上场棋子"""
        # 判定人口
        if len(self.chessOnField) >= self.population:
            print(f"人口不足，请先下棋子，选项有{self.chessOnField}")
            return
        chess = self.checkChessID(chessID=chessID)
        if chess in self.chessOnField:
            print(f"棋子{chess}已经在场上了，请勿重复上场!")
            return
        self.chessInHand.remove(chess)
        self.chessOnField.append(chess)
        chess.setInitialPosition(position = position)
        chess.onField = True
        print(f"{self}:{chess}上场到位置{colored(str(chess.position), color='magenta')}")
        # print(f"       备战区棋子：{self.chessInHand}，\n       上场棋子{[(c, c.position) for c in self.chessOnField]}；")
        
    def field_to_hand(self, chessID: int):
        """下场棋子"""
        chess = self.checkChessID(chessID=chessID)
        if chess in self.chessInHand:
            print(f"棋子{chess}已经在备战区了，不能下场！")
            return
        chess.position = [-1,-1]
        self.chessOnField.remove(chess)
        self.chessInHand.append(chess)
        chess.onField = False
        print(f"{self}:{chess}下场")
        # print(f"       备战区棋子：{self.chessInHand}，\n       上场棋子{[(c, c.position) for c in self.chessOnField]}；")

    # 棋子升级
    def find_all_copies(self, chessID: int) -> list[chessInterface]:
        """找到所有这个uniqueid 下的相同类型棋子

        Args:
            chessID (int): _description_

        Returns:
            list[chessInterface]: _description_
        """
        chess = self.checkChessID(chessID=chessID)
        sameChess = []
        for c in self.chesses.values():
            if c.id == chess.id:
                sameChess.append(c)
        if len(sameChess) >= 2:
            return sameChess
        else:
            return None

    def upgrade_chess(self, chessID: int ) -> None:
        """升级棋子

        Args:
            chessID (int): _description_
        """
        chess = self.checkChessID(chessID=chessID)
        sameChessList = self.find_all_copies(chessID=chessID)
        if sameChessList is not None:
            inp: int = -1
            while inp not in upgrade_dict[chess.id]:
                try:
                    inp = int(input(f"         选项有：{[chessName_dict[i] for i in upgrade_dict[chess.id]]}"))
                except:
                    print('输入不合法，请重新输入')
                    continue
                if inp not in upgrade_dict[chess.id]:
                    print(f"    {chess}不可以升级为{chess_dict[inp]}\n    请在{upgrade_dict[chess.id]}中选择合理的棋子ID：")
            
            if input(f"确认升级吗。(1=是，0=否)") != "1":
                print("已返回主菜单。。。")
                return 

            for c in sameChessList[:2]:
                if c.onField:
                    self.chessOnField.remove(c)
                else:
                    self.chessInHand.remove(c)
                del self.chesses[c.uniqueID]
                c.onField = False
            # print(f"  {self}:{chess}升级{colored('成功','green')}，请选择一个 {chess.star + 1} 星棋子")
            
            self.get_chess(chess_dict[inp](),purchase=False)
        else:
            print(f"  {self}:{chess}升级{colored('失败','red')}，请检查棋子持有数量")

    def new_turn(self, turn:int):
        # 玩家回合循环
        # self.hp -= 10
        row = [3,4,5] # 玩家只能把棋子放在自己这边的棋盘上
        col = [0,1,2,3,4]
        
        if turn != 1: # if not the first turn
            self.next_turn()
        if self.check_death():
            print(self,"is Dead")
        self.printStatus() # 显示玩家当前信息
        if self.cardLock:
            self.cardLock = False# 自动解锁
        else:
            self.get_random_chess_to_draw()
        
        while True:
            action = input(f"\n{self},您要做的事情是：\n1.购买棋子 2.重新抽卡 3.出售棋子 4.上阵棋子 5.下场棋子 6.升级棋子 7.升级人口 8.变更棋子位置 9.查看当前状态 10.锁定当前棋子 0.完成操作\n")
            try:
                action = int(action)
            except:
                print("建议查看有没有可上场棋子和可更新棋子")
                continue
            match action:
                case 1:
                    # 购买棋子
                    if self.goldAvail < 1:
                        print("当前金币为 0  不能进行购买和升级人口操作.")
                        continue
                    elif len(self.chessInHand) >= 5:
                        print("棋子数量超过手牌上线，不能进行购买.")
                        continue
                    # chessIndex = -1
                    # while chessIndex not in [0,1,2] or self.chessList[chessIndex] is None:
                    #     chessIndex = input(f"现有选项 {[str(index+1)+'. '+str(self.chessList[index]) for index in range(len(self.chessList))]},您的选择是：(0/1/2) 按任意键加回车返回菜单。")
                    #     chessIndex = int(chessIndex)-1
                    #     if chessIndex not in [0,1,2]:
                    #         print("格式不正确，请问您想要【购买】第几个棋子？")
                    try:
                        chessIndex = -1
                        while chessIndex not in [0,1,2] or self.chessList[chessIndex] is None:
                            chessIndex = input(f"现有选项 {[(index+1,str(self.chessList[index])) for index in range(len(self.chessList))]},您的选择是：(0/1/2) 按任意键加回车返回菜单。")
                            chessIndex = int(chessIndex)-1
                            if chessIndex not in [0,1,2]:
                                print("格式不正确，请问您想要【购买】第几个棋子？")
                    except:
                        print("已返回主菜单。。。")
                        continue
                    newChess = self.chessList[chessIndex]() # 初始化棋子
                    self.get_chess(newChess = newChess)
                    self.chessList[chessIndex] = None
                case 2:
                    # 重新抽卡
                    if self.goldAvail < 3:
                        print(f"当前金币为 {self.goldAvail}  不能进行抽卡操作.")
                        continue
                    elif self.cardLock:
                        print('当前棋子锁是开启状态，请先关闭棋子锁')
                    try:
                        beSure = int(input("抽卡将会花费3金币，您确定要重新抽卡吗？(1=是,0=否)\n"))
                        if beSure == 1:
                            self.redraw()
                    except:
                        print("已返回主菜单。。。")
                        continue
                case 3:
                # 出售棋子
                    if self.chesses == {}:
                        print("当前没有任何棋子")
                        continue
                    try:
                        chessIndex = -1
                        chessIDs = []
                        for i in self.chesses.keys(): 
                            chessIDs.append(i)
                        while chessIndex not in range(len(chessIDs)):
                            chessIndex = input(f"现有选项 {[(index+1,self.chesses[chessIDs[index]]) for index in range(len(chessIDs))]},请选择：(0/1/2/3...) 按任意键加回车返回菜单。\n")
                            chessIndex = int(chessIndex) -1
                            if chessIndex not in range(len(chessIDs)):
                                print("格式不正确，请问您想要【出售】第几个棋子？请输入数字")
                    except:
                        print("已返回主菜单。。。")
                        continue
                    self.sell_chess(chessID = chessIDs[chessIndex])     
                case 4:
                    # 上场棋子
                    if self.chessInHand == []:
                        print("场下没有棋子。")
                        continue
                    elif len(self.chessOnField) >= self.population:
                        print(f"人口不足，请先下棋子，选项有{self.chessOnField}")
                        continue
                    try:
                        chessIndex = -1
                        while chessIndex not in range(len(self.chessInHand)):
                            chessIndex = input(f"现有选项 {[(index+1,self.chessInHand[index]) for index in range(len(self.chessInHand))]},请选择棋子Index：(1/2/3...) 按任意键加回车返回菜单。\n")
                            chessIndex = int(chessIndex)-1
                            if chessIndex not in range(len(self.chessInHand)):
                                print("格式不正确，请问您想要【上场】第几个棋子？")
                        
                        unavailPos = [chess.position for chess in self.chessOnField]
                        position = [-1,-1]

                        while position[0] not in row or position[1] not in col or position in unavailPos:
                            r = input(f"请输入棋子在第几排：选项有{row}；按任意键加回车返回菜单。\n")
                            c = input(f"请输入棋子在第几列：选项有{col}；按任意键加回车返回菜单。\n")
                            r = int(r)
                            c = int(c)
                            position = [r,c]
                            if position in unavailPos:
                                print(f"{[r,c]}被占据，请重新输入位置")
                            elif position[0] not in row or position[1] not in col:
                                print(f"{[r,c]}不在棋盘里，请重新输入位置")
                    except:
                        print('已返回至主菜单。。。')
                        continue

                    chess = self.chessInHand[chessIndex]
                    chessID = chess.uniqueID
                    self.hand_to_field(chessID = chessID,position=position)
                    print(f"变更棋子位置成功，当前人口：{len(self.chessOnField)/self.population};\n现在的场上棋子位置为：\n{[(c, c.position) for c in self.chessOnField]}")
                case 5:
                    # 下场棋子
                    if self.chessOnField == []:
                        print("场上没有棋子。")
                        continue
                    try:
                        chessIndex = -1
                        while chessIndex not in range(len(self.chessOnField)):
                            chessIndex = input(f"现有选项\n{[(index+1,self.chessOnField[index]) for index in range(len(self.chessOnField))]},请选择棋子ID：(1/2/3...) 按任意键加回车返回菜单。\n")
                            chessIndex = int(chessIndex)-1
                            if chessIndex not in range(len(self.chessOnField)):
                                print("格式不正确，请问您想要【下场】第几个棋子？")
                    except:
                        print('已返回至主菜单。。。')
                        continue
                    self.field_to_hand(chessID = self.chessOnField[chessIndex].uniqueID)
                case 6:
                    # 升级棋子
                    canBeUpgraded = []
                    for chessID,chess in self.chesses.items():
                        if self.find_all_copies(chessID=chessID) is not None:
                            canBeUpgraded.append((chessID,chess))
                    if canBeUpgraded == []:
                        print('当前没有可升级的棋子,请选择其他操作')
                        continue
                    try:
                        chessID = int(input(f"可升级棋子为{canBeUpgraded},按任意键加回车返回菜单\n"))
                        while chessID not in [t[0] for t in canBeUpgraded]:
                            chessID = int(input(f"格式不正确，可升级棋子为{canBeUpgraded},按任意键加回车返回菜单。请重新选择：\n"))
                    except:
                        print('已返回至主菜单。。。')
                        continue
                    self.upgrade_chess(chessID = chessID)
                case 7:
                    # 升级人口
                    if self.goldAvail < self.population:
                        print(f"当前金币为 {self.goldAvail}/{self.population}  不能进行升级人口操作.")
                        continue
                    try:
                        beSure = int(input("确定升级人口吗？这个操作不能撤回。(1=是/0=否) 按任意键加回车返回菜单。\n"))
                        if beSure == 1:
                            self.upgrade_pop()
                    except:
                        print('已返回至主菜单。。。')
                case 8:
                    # 变更棋子位置
                    if self.chessOnField == []:
                        print("棋盘中没有棋子,不能更改棋子位置。已返回主菜单")
                        continue
                    chessIndex = -1
                    try:
                        while chessIndex not in range(len(self.chessOnField)):
                            chessIndex = input(f"现有选项\n{[(index+1,self.chessOnField[index],self.chessOnField[index].position) for index in range(len(self.chessOnField))]},请选择棋子Index：(1/2/3...) 按任意键加回车返回菜单。\n")
                            chessIndex = int(chessIndex)-1
                            if chessIndex not in range(len(self.chessOnField)):
                                print("格式不正确，请问您想要【移动】第几个棋子？")
                    except:
                        print("已返回主菜单。。。")
                        continue
                        
                    unavailPos = [chess.position for chess in self.chessOnField]
                    position = [-1,-1]
                    try:
                        while position[0] not in row or position[1] not in col or position in unavailPos:
                            r = input(f"请输入棋子在第几排：选项有{row} 按任意其他键取消操作。\n")
                            c = input(f"请输入棋子在第几列：选项有{col} 按任意其他键取消操作。\n")
                            r = int(r)
                            c = int(c)
                            position = [r,c]
                            if position in unavailPos:
                                print(f"{[r,c]}被占据，请重新输入位置，不可选位置：{unavailPos}")
                            elif position[0] not in row or position[1] not in col:
                                print(f"{[r,c]}不在棋盘里，请重新输入位置")
                    except:
                        print("已返回主菜单。。。")
                        continue

                    chess = self.chessOnField[chessIndex]
                    chess.setInitialPosition(position)
                    print(f"变更棋子位置成功，当前人口：{len(self.chessOnField)/self.population};\n现在的场上棋子位置为：\n{[(c, c.position) for c in self.chessOnField]}")
                case 9:
                    self.printStatus()
                    print()
                case 10:
                    if self.cardLock:
                        print("当前卡牌锁定状态为 【关闭】")
                        self.cardLock = False
                    else:
                        print("当前卡牌锁定状态为 【开启】")
                        self.cardLock = True
                case 0:
                    # 完成操作
                    inp = input("确定完成该回合吗，此操作不能取消。1=是 其他键=否")
                    if inp == "1":
                        print("此回合操作完成，等待其他玩家...\n")
                        break
                    else:
                        continue
                case _:
                    print("建议查看有没有可上场棋子和可更新棋子")
        return deepcopy(self.chessOnField)
            