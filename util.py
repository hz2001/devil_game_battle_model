from chess_info import *

upgrade_dict = {1: [4, 5], 2: [6, 7], 3: [8, 9], # 1 star 兔子，蚂蚁，小丑鱼

                  4: [10, 11], 5: [12, 13], # 2 star mammal 4：羊驼， 5:狼 
                  6: [16, 17], 7: [14, 15],  # 2 star insect 6: 瓢虫 ，7: 蜜蜂
                  18: [30, 19], 9: [21, 22], 8:[], # 2 star marine  8: 食人鱼 9: 海胆 18:灯笼鱼

                  10: [23,24], 11: [23,24], # 3 star mammal ranged 麋鹿， 猴
                  12: [23,24], 13: [23,24], # 3 star mammal melee 犀牛， 熊

                  14: [25,26], 15: [25,26], # 3 star insect ranged 蝴蝶， 萤火虫
                  16: [25,26], 17: [25,26], # 3 star insect melee 螳螂， 蝎子
                  
                  30: [27,28], 19: [27,28], # 3 star marine ranged 虎鲸， 电鳗
                  20:[] , 21: [27,28], 22:[27,28], # 3 star marine ranged 螃蟹，一角鲸，海龟

                  23:[],24:[], # 大象， 老虎
                  25:[], 26:[],  # 独角仙， 蜘蛛
                  27:[], 28:[]} # 章鱼， 鲨鱼
chess_dict = {1: rabbit, 2:ant, 3:littleUglyFish, 
                
                4:llama, 5:wolf, 
                6:ladybug, 7: bee, 
                18: anglerfish, 9:sea_hedgehog,  8: swallower, 
                
                10: heal_deer, 11: monkey, 
                12: hippo, 13: bear,
                14: butterfly, 15: fireworm,
                16: mantis, 17: scorpion, # 3 star insect melee 螳螂， 蝎子
                  
                30:killer_whale, 19: electric_eel, # 3 star marine ranged 灯笼鱼， 电鳗
                20: crab, 21: monoceros, 22: turtle, # 3 star marine ranged 螃蟹，一角鲸，海龟

                23:elephant,24:tiger, # 大象， 老虎
                25:unicorn_b, 26:spider,  # 独角仙， 蜘蛛
                27:octopus, 28:shark} # 章鱼， 鲨鱼

chessName_dict = {1: '兔子 id:1', 2:'蚂蚁 id:2', 3:"小丑鱼 id:3", 
                
                4:"羊 id:4", 5:"狼 id:5", 
                6:'瓢虫 id:6', 7: '蜜蜂 id:7', 
                18: '灯笼鱼 id:18',9:'河豚 id:9',  8: '食人鱼 id:8', 
                
                10: '麋鹿 id:10', 11: '猴子 id:11', 
                12: '河马 id:12', 13: '熊 id:13',
                14: '蝴蝶 id:14', 15: '萤火虫 id:15',
                16: '螳螂 id:16', 17: '蝎子 id:17', # 3 star insect melee 螳螂， 蝎子
                  
                30: '虎鲸 id:30', 19: '电鳗 id:19', # 3 star marine ranged 灯笼鱼， 电鳗
                20: '螃蟹 id:20', 21: '一角鲸 id:21', 22: '海龟 id:22', # 3 star marine ranged 螃蟹，一角鲸，海龟

                23:'大象 id:23',24:'老虎 id:24', # 大象， 老虎
                25:'独角仙 id:25', 26:'蜘蛛 id:26',  # 独角仙， 蜘蛛
                27:'章鱼 id:27', 28:'鲨鱼 id:28'} # 章鱼， 鲨鱼
