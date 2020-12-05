import pandas as pd
import numpy as np
import json
import math

class Church:
    def __init__(self, devil_list, comb_json):
        self.unitPrice = {
            "★★★★★": {10:60000, 9:1500000, 8:3000000, 7:4200000},
            "★★★★": {9:3000, 8:6000, 7:150000, 6:300000, 5:320000},
            "★★★": {7:250, 6:500, 5:2500, 4:5000, 3:5200, 2:5400},
            "★★": {6:5, 5:5, 4:5 , 3:25, 2:50},
            "★": {5:5, 4:5, 3:5, 2:5},
        };
        self.gradePrice = [
            0.0, 0.150, 0.30, 0.450, 60.0,
            75, 1080, 1260, 14400, 16200
        ];
        self.data = pd.read_csv(devil_list)
        self.init_score()
        with open(comb_json) as f:
            self.comb = json.load(f)
    def searchDevilByNo(self, no):
        return self.data[self.data.no == no].iloc[0]
    def searchDevilByName(self, name):
        return self.data[self.data.name == name].iloc[0]
    def getDevilsByRace(self, type_):
        return self.data[self.data.type == type_]
    def getDevilsNameByRare(self, rare):
        return self.data[self.data["rare"] == rare]["name"]
    def getLesserGrade(self, devil):
        devil_list = self.getDevilsByRace(devil.type).sort_values("grade").reset_index(drop=True)
        target_rank = devil_list[devil_list.name == devil["name"]].index[0]  # type内でのgradeの順位
        if target_rank == 0:
            return 0
        else:
            return devil_list.iloc[target_rank - 1].grade

    def invoice(self, target, left, right):
        sumRare = len(left.rare) + len(right.rare)
        price = self.unitPrice[target.rare][sumRare]
        
        choice = math.floor(target.grade / 10)
        step = target.grade - (left.grade + right.grade) / 2.0
        price += math.floor(self.gradePrice[choice] * step)
        if price < 0:
            price = 0
        return price
    def summon_search(self, devil, arch):
        x = []
        lesser = self.getLesserGrade(devil)
        for pair in self.comb[devil.type]:
            lefts  = self.getDevilsByRace(pair["n1"]);
            rights = self.getDevilsByRace(pair["n2"]);
            for i, left in lefts.iterrows():
                for j, right in rights.iterrows():
                    z = math.floor((left.grade + right.grade) / 2 ) + 1;
                    if lesser < z and z <= devil.grade:
                        arch_price = self.invoice(devil, left, right)
                        if devil["rare"] == "★★★★★":
                            base_price = math.ceil(arch_price / 2)
                        elif devil["rare"] == "★★★★":
                            base_price = math.ceil(arch_price * 0.7)
                        else:
                            base_price = arch_price
                        if len(left["rare"]) <= len(devil["rare"]) and len(right["rare"]) <= len(devil["rare"]):
                            if arch:
                                x.append( {"left":left, "right":right,
                                           "base_price":base_price, "arch_price": arch_price,
                                           "left_arch":True, "right_arch":False
                                          })
                                x.append( {"left":left, "right":right,
                                           "base_price":base_price, "arch_price": arch_price,
                                           "left_arch":False, "right_arch":True
                                          })
                            else:
                                x.append( {"left":left, "right":right,
                                           "base_price":base_price, "arch_price": arch_price,
                                           "left_arch":False, "right_arch":False
                                          })
        return x


    def init_score(self, base_score_zero_devils=[], arch_score_zero_devils=[]):
        self.base_scores = {}
        self.arch_scores = {}
        
#         for name in self.data[self.data["rare"] == "★★★★"]["name"]:
#             self.arch_scores[name]= {"score": 0}
#         for name in self.data[self.data["rare"] == "★★★"]["name"]:
#             self.arch_scores[name]= {"score": 0}
#         for name in self.data[self.data["rare"] == "★★"]["name"]:
#             self.base_scores[name]= {"score": 0}
#         for name in self.data[self.data["rare"] == "★"]["name"]:
#             self.base_scores[name]= {"score": 0}
        
        for name in base_score_zero_devils:
            self.set_score(name, False, 0)
        for name in arch_score_zero_devils:
            self.set_score(name, True, 0)

    def calc_devil_score(self, devil, arch, passing_devil_names):
        if arch:
            if devil['name'] in self.arch_scores:
                return self.arch_scores[devil['name']]["score"]
        else:
            if devil['name'] in self.base_scores:
                return self.base_scores[devil['name']]["score"]
        pairs = self.summon_search(devil,arch=arch)
        min_score = np.inf
        min_pair = {}
        for pair in pairs:
            temp_score = self.calc_union_score(left=pair["left"],
                                               right=pair["right"],
                                               left_arch=pair["left_arch"],
                                               right_arch=pair["right_arch"],
                                               arch_price=pair["arch_price"],
                                               base_price=pair["base_price"],
                                               passing_devil_names=passing_devil_names.copy().union(set([devil["name"]])))
            if temp_score < min_score:
                min_score = temp_score
                min_pair = {"left_name": pair["left"]["name"],
                            "right_name": pair["right"]["name"],
                            "left_arch": pair["left_arch"],
                            "right_arch": pair["right_arch"],
                           }
        self.set_score(devil["name"], arch, min_score, min_pair)
        return min_score


    def calc_union_score(self, left, right, left_arch, right_arch, arch_price, base_price, passing_devil_names):
        if left["name"] in passing_devil_names:
            return np.inf
        if right["name"] in passing_devil_names:
            return np.inf
        left_score = self.calc_devil_score(left, left_arch, passing_devil_names.copy().union(set([left["name"]])))
        right_score = self.calc_devil_score(right, right_arch, passing_devil_names.copy().union(set([right["name"]])))
        if left_arch == False and right_arch == False:
            price = base_price
        else:
            price = arch_price
        return left_score + right_score + price


    def set_score(self, name, arch, score, min_pair={}):
        assert name in self.data["name"].values, "リストにない悪魔名称です。"
        if arch:
            self.arch_scores[name] = min_pair
            self.arch_scores[name]["score"] = score
        else:
            self.base_scores[name] = min_pair
            self.base_scores[name]["score"] = score

    def calcOptimalPath(self, name, arch, base_score_zero_devils, arch_score_zero_devils):
        self.init_score(base_score_zero_devils, arch_score_zero_devils)
        self.target = self.searchDevilByName(name)
        self.arch = arch
        self.score = self.calc_devil_score(self.target, arch, set([]))
        print(f"score: {self.score}")
        self.printOptimalPair(name, arch)


    def printOptimalPair(self, name, arch):
        if arch:
            if 'left_name' in self.arch_scores[name]:
                print(f"{name}({self.getArchStr(arch)}) = {self.arch_scores[name]['left_name']}({self.getArchStr(self.arch_scores[name]['left_arch'])}) + {self.arch_scores[name]['right_name']}({self.getArchStr(self.arch_scores[name]['right_arch'])})")
                self.printOptimalPair(self.arch_scores[name]['left_name'], self.arch_scores[name]["left_arch"])
                self.printOptimalPair(self.arch_scores[name]['right_name'], self.arch_scores[name]["right_arch"])
        else:
            if 'left_name' in self.base_scores[name]:
                print(f"{name}({self.getArchStr(arch)}) = {self.base_scores[name]['left_name']}({self.getArchStr(self.base_scores[name]['left_arch'])}) + {self.base_scores[name]['right_name']}({self.getArchStr(self.base_scores[name]['right_arch'])})")
                self.printOptimalPair(self.base_scores[name]['left_name'], self.base_scores[name]["left_arch"])
                self.printOptimalPair(self.base_scores[name]['right_name'], self.base_scores[name]["right_arch"])


    def getArchStr(self, arch):
        if arch:
            return "ア"
        else:
            return "素"