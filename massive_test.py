# 这个文档会记录量化测试，每一人口的情况下，进行1000场战斗，随机棋子/限制棋子星级后随机棋子。
# 记录棋子胜率，棋子平均伤害/单局最高伤害，棋子平均承受伤害/单局最高承受伤害，棋子技能施放频率，
from battle import *
from copy import deepcopy
from json import dumps
import openpyxl 

chess_dict = {1: rabbit, 2:ant, 3:littleUglyFish, 
                
                4:llama, 5:wolf, 
                6:ladybug, 7: bee, 
                8: swallower, 9:sea_hedgehog,  
                
                10: heal_deer, 11: monkey, 
                12: hippo, 13: bear,
                14: butterfly, 15: fireworm,
                16: mantis, 17: scorpion, # 3 star insect melee 螳螂， 蝎子
                  
                18: anglerfish, 19: electric_eel, # 3 star marine ranged 灯笼鱼， 电鳗
                20: crab, 21: monoceros, 22: turtle, # 3 star marine ranged 螃蟹，一角鲸，海龟

                23:elephant,24:tiger, # 大象， 老虎
                25:unicorn_b, 26:spider,  # 独角仙， 蜘蛛
                27:octopus, 28:shark,
                29: wolfMinion} # 章鱼， 鲨鱼

chessName_dict = {1: '兔子 id:1', 2:'蚂蚁 id:2', 3:"小丑鱼 id:3", 
                
                4:"羊 id:4", 5:"狼 id:5", 
                6:'瓢虫 id:6', 7: '蜜蜂 id:7', 
                8: '食人鱼 id:8', 9:'河豚 id:9',  
                
                10: '麋鹿 id:10', 11: '猴子 id:11', 
                12: '河马 id:12', 13: '熊 id:13',
                14: '蝴蝶 id:14', 15: '萤火虫 id:15',
                16: '螳螂 id:16', 17: '蝎子 id:17', # 3 star insect melee 螳螂， 蝎子
                  
                18: '灯笼鱼 id:8', 19: '电鳗 id:19', # 3 star marine ranged 灯笼鱼， 电鳗
                20: '螃蟹 id:20', 21: '一角鲸 id:21', 22: '海龟 id:22', # 3 star marine ranged 螃蟹，一角鲸，海龟

                23:'大象 id:23',24:'老虎 id:24', # 大象， 老虎
                25:'独角仙 id:25', 26:'蜘蛛 id:26',  # 独角仙， 蜘蛛
                27:'章鱼 id:27', 28:'鲨鱼 id:28',
                29: 'wolfMinion id:29'} # 章鱼， 鲨鱼
chessName_dict_inEng = {1: 'rabbit id:1', 2:'ant id:2', 3:"littleUglyFish id:3", 
                
                4:"llama id:4", 5:"wolf id:5", 
                6:'ladyBug id:6', 7: 'bee id:7', 
                8: 'swallower id:8', 9:'sea_hog id:9',  
                
                10: 'heal_deer id:10', 11: 'monkey id:11', 
                12: 'hippo id:12', 13: 'bear id:13',
                14: 'butterfly id:14', 15: 'fireworm id:15',
                16: 'mantis id:16', 17: 'scorpion id:17', # 3 star insect melee 螳螂， 蝎子
                  
                18: 'anglerFish id:8', 19: 'electric_e id:19', # 3 star marine ranged 灯笼鱼， 电鳗
                20: 'crab id:20', 21: 'monocro id:21', 22: 'turtle id:22', # 3 star marine ranged 螃蟹，一角鲸，海龟

                23:'elephant id:23',24:'tiger id:24', # 大象， 老虎
                25:'unicorn_b id:25', 26:'spider id:26',  # 独角仙， 蜘蛛
                27:'octopus id:27', 28:'shark id:28',
                29: 'wolfMinion id:29'} # 章鱼， 鲨鱼

everythingWeNeedToKnowAboutAChess = {'chessName': '',
                                     'totalMatch': 0, 
                                     'winCount':0, 
                                     'maxDamageInOneMatch': 0, # 单局造成最高伤害
                                     'totalDamage': 0,# 总伤害
                                     'totalAttackDamage': 0, # 总攻击伤害
                                     'totalSpellDamage': 0, # 总技能伤害
                                     'maxDamageReceivedInOneMatch':0, # 单局受到最高伤害
                                     'totalDamageReceived':0, # 总承受伤害
                                     'totalSpellCasted': 0, # 技能施放总数
                                     'totalMatchLength': 0, # 总战斗时长
                                     'longestMatchLength': 0, # 最长战斗时长
                                     'shortestMatchLength': 100000, # 最短战斗时长
                                     'totalLivingLength': 0, # 总在场时长
                                     'winRate': None, # 总胜率
                                     'averageMatchLength': None,
                                     'averageDamagePerMatch': None,
                                     'averageDamageReceivedPerMatch': None,
                                     
                                     # 和那些棋子一起上场的时候胜率高
                                     }
chessBattleResult_dict: dict[int,dict[str,float]] = {} 
for id, chessChineseName in chessName_dict_inEng.items():
    chessBattleResult_dict[id] = deepcopy(everythingWeNeedToKnowAboutAChess)
    chessBattleResult_dict[id]['chessName'] = chessChineseName
    
# 在没做棋子判定随机的情况下，哪个队伍更有可能获胜。
redTeamWinRate = 0.5
blueTeamWinRate = 1-redTeamWinRate

turnRestrains = {1: {1:1, 2:0,3:0,4:0},  # [1, 0, 0, 0]
                  2: {1:3, 2:1,3:0,4:0},  # [0.5, 0.5, 0, 0]
                  3: {1:6, 2:3,3:1,4:0},  # [0.3, 0.5, 0.2, 0]
                  4: {1:9, 2:4,3:2,4:1},  # [0.15, 0.4, 0.4, 0.05] # 如果有四星就不能满人口
                  5: {1:12,2:6,3:3,4:1},  # [0.1, 0.25, 0.4, 0.15] # 必有一个三星
                  6: {1:16,2:8,3:4,4:2},  # [0.1, 0.25, 0.5, 0.15] # 必有一个四星
                  7: {1:21,2:10,3:5,4:2}, # [0.05, 0.25, 0.4, 0.3]
                  8: {1:28,2:14,3:7,4:3}, # [0.05, 0.25, 0.4, 0.3]
                  9: {1:34,2:17,3:8,4:4}, # [0.05, 0.25, 0.35, 0.35]
                  10: {1:40,2:20,3:10,4:5}}
turnChessPossibility = {
                  1:[1, 0, 0, 0],            # 必有一个一星
                  2: [0.5, 0.5, 0, 0],       # 必有一个2星
                  3: [0.3, 0.5, 0.2, 0],     # 纯随机
                  4: [0.15, 0.4, 0.4, 0.05], # 如果有四星就不能满人口
                  5: [0.1, 0.25, 0.4, 0.15], # 必有一个三星
                  6: [0.1, 0.25, 0.5, 0.15], # 必有一个四星
                  7: [0.05, 0.25, 0.4, 0.3], # 必有一个四星，一个三星
                  8: [0.05, 0.25, 0.4, 0.3], # 必有一个四星, 两个三星
                  9: [0.05, 0.25, 0.35, 0.35],
                  10: [0.05, 0.25, 0.35, 0.35]}
def chess_level(pop, turn) -> list[int]:
    """根据人口和回合，返回一个含有棋子星级的list

    Args:
        pop (_type_): _description_
        turn (_type_): _description_

    Returns:
        list[int]: _description_
    """
    possibilities = deepcopy(turnChessPossibility[turn])
    chessLevels = []
    for i in range(pop):
        rand = random()
        # print("pop= ",i, " randomValue: ",rand)
        if i == 0:
            if turn == 1:
                chessLevels.append(1)
                continue
            elif turn == 2:
                chessLevels.append(2)
                continue
            elif turn == 4 and rand>0.6: 
                chessLevels.append(3)
                continue
            elif turn == 5:
                chessLevels.append(3)
                continue
            elif turn == 6:
                chessLevels.append(4)
                continue
            elif turn == 7:
                chessLevels.append(4)
                continue
            elif turn == 8:
                chessLevels.append(4)
                continue
        if rand <= possibilities[0]:
            chessLevels.append(1)
        elif rand > possibilities[0] and \
                rand <= possibilities[0]+ possibilities[1]:
            chessLevels.append(2)
        elif rand > possibilities[0]+ possibilities[1] and \
                rand <=  possibilities[0]+ possibilities[1]+ possibilities[2]:
            chessLevels.append(3)
        else:
            chessLevels.append(4)
    return chessLevels    
    
turnPopulationRestriction = {
                  1: [1,1], # 括号中是人口下限和上限
                  2: [2,2],
                  3: [2,2],
                  4: [3,3],
                  5: [3,4],
                  6: [3,4],
                  7: [4,5],
                  8: [4,5], 
                  9: [4,5,6],
                  10: [4,5,6]}

star1 = [1,2,3]
star2 = [4,5,6,7,8,9]
star3 = [10,11,12,13,14,15,16,17,18,19,21,22] # 20 还没加进去
star4 = [23,24,25,26,27,28]
        
        
def get_random_chess_with_level(level:int):
    if level > 4:
        return None
    if level == 1:
        chessID = star1[randint(len(star1))]
    elif level == 2:
        chessID = star2[randint(len(star2))]
    elif level == 3:
        chessID = star3[randint(len(star3))]
    elif level == 4:
        chessID = star4[randint(len(star4))]
    chess = chess_dict[chessID]
    return  chess

def get_random_chesses_with_pop(population:int, turn: int, team: int):
    chessLevels = chess_level(pop=population,turn=turn)
    rowRange = []
    colRange = [0,1,2,3,4]
    positions = []
    if team == 0:
        rowRange =[0,1,2]
    else:
        rowRange =[3,4,5]
    i = 1
    while i <= population:
        position = [rowRange[randint(len(rowRange))], colRange[randint(len(colRange))]]
        if position not in positions:
            positions.append(position)
            i += 1
    
    chesses = [] # a list of initiated chess
    for j in range(population):
        chessLevel  = chessLevels[j]
        # print(position)
        chessPosition = positions[j]
        chess = get_random_chess_with_level(chessLevel)
        
        chesses.append(chess(position=chessPosition))
    return chesses
        
    # random chess positions 
    
    
def random_battle(turn: int, n):
    """随机 n 个单局游戏 并且记录战斗信息
    """
    redTeamWins = 0
    blueTeamWins = 0
    for i in range(n): # 循环n次
        populationRestriction = turnPopulationRestriction[turn]
        redPop = populationRestriction[randint(len(populationRestriction))]
        bluePop = populationRestriction[randint(len(populationRestriction))]
        redTeam: list[chessInterface] = get_random_chesses_with_pop(population = redPop, turn = turn, team = 0)
        blueTeam: list[chessInterface] = get_random_chesses_with_pop(population = bluePop, turn = turn, team = 1)

        newBattle = battle()
        newBattle.board_print()
        newBattle.addRedTeam(redTeam)
        newBattle.addBlueTeam(blueTeam)
        wonTeam, matchLength = newBattle.battle_with_skills_test(recordDict=chessBattleResult_dict)
        
        for (uniqueID, chess) in newBattle.allChessDict.items():
            chessBattleResult_dict[chess.id]['totalMatch'] += 1
            if wonTeam == chess.team:
                chessBattleResult_dict[chess.id]['winCount'] += 1
            # 记录伤害
            if chess.totalDamage > chessBattleResult_dict[chess.id]['maxDamageInOneMatch']:
                chessBattleResult_dict[chess.id]['maxDamageInOneMatch'] = chess.totalDamage
            chessBattleResult_dict[chess.id]['totalDamage'] += chess.totalDamage
            
            chessBattleResult_dict[chess.id]['totalAttackDamage'] += chess.totalAttackDamage
            chessBattleResult_dict[chess.id]['totalSpellDamage'] += (chess.totalDamage -chess.totalAttackDamage)
            # 记录承伤
            if chess.totalDamageReceived > chessBattleResult_dict[chess.id]['maxDamageReceivedInOneMatch']:
                chessBattleResult_dict[chess.id]['maxDamageReceivedInOneMatch'] = chess.totalDamageReceived
            chessBattleResult_dict[chess.id]['totalDamageReceived'] += chess.totalDamageReceived
            # 记录对局信息
            chessBattleResult_dict[chess.id]['totalMatchLength'] += matchLength
            if matchLength > chessBattleResult_dict[chess.id]['longestMatchLength']:
                chessBattleResult_dict[chess.id]['longestMatchLength'] = matchLength
            elif matchLength < chessBattleResult_dict[chess.id]['shortestMatchLength']:
                chessBattleResult_dict[chess.id]['shortestMatchLength'] = 1
            if chess.isDead:
                chessBattleResult_dict[chess.id]['totalLivingLength'] += chess.deathTime
                
                                    #  'totalSpellCasted': 0, # 技能施放总数
        if wonTeam == 0:
            redTeamWins += 1
        else:
            blueTeamWins += 1
        print("Battle: ", i," finished")
    
            
    
def main():
    for turn in range(1,11):
        # random a population for that guy
        print("\nturn: ", turn)
        random_battle(turn = turn, n = 10)
    # print(chessBattleResult_dict)

    #  'averageDamageReceivedPerMatch': None,
    for cid, chess in chessBattleResult_dict.items():
        totalBattles = chessBattleResult_dict[cid]['totalMatch']
        if totalBattles == 0:
            totalBattles += 1
        wonBattles = chessBattleResult_dict[cid]['winCount']
        chessBattleResult_dict[cid]['winRate'] = round(wonBattles/totalBattles,3) * 100
        
        totalMatchLen = chessBattleResult_dict[cid]['totalMatchLength']
        chessBattleResult_dict[cid]['averageMatchLength'] = round(totalMatchLen/totalBattles,3)
        
        totalDamage = chessBattleResult_dict[cid]['totalDamage']
        chessBattleResult_dict[cid]['averageDamagePerMatch'] = round(totalDamage/totalBattles,3)
        
        totalDamageReceived = chessBattleResult_dict[cid]['totalDamageReceived']
        chessBattleResult_dict[cid]['averageDamageReceivedPerMatch'] = round(totalDamageReceived/totalBattles,3)



    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Battle Data"
    col = 1
    for attr in everythingWeNeedToKnowAboutAChess.keys():
        ws.cell(row=1, column=col, value = attr)
        col += 1
    row = 2
    for chessID, chessData in chessBattleResult_dict.items():
        col = 1
        for value in chessData.values():
            ws.cell(row=row, column=col, value = value)
            col += 1
        row += 1 
    wb.save('battleData.xlsx')
    # save to json
    # with open("battle_results.json", 'w') as f:
    #     f.write(dumps(chessBattleResult_dict))
    
    
if __name__ == '__main__':
    main()