from collections import defaultdict
import time
class OPGAnalyzer:
    def __init__(self, start, productions):
        self.productions = productions
        self.productions['S'] = ['#' + start + '#', ]
        self.nonterminals = self.productions.keys()
        #python Double Iteration in List Comprehension
        self.overs = set(i for left in productions.keys() for right in productions[left] for i in right    if i not in self.nonterminals)
        self.overs.add('#')

        #规约字典
        self.reduce = {right:left for left in productions.keys() for right in productions[left]}

        self.get_firstvt_all()
        self.get_lastvt_all()
        self.get_matrix()
        # self.get_relation_matrix()
    

    #该算法将比书上的快两倍,简单样例测试
    def get_firstvt_all(self):
        self.firstvt = defaultdict(set)
        for nontermainal in self.nonterminals:
            self.get_firstvt(nontermainal)
        
    #因为不会出现互相依赖的情况,所以一定存在一个底层产生式,可以一步得到

    #不会出现循环依赖,所以一旦firstvt[nontermainal]非空,则表示处理完毕
    def get_firstvt(self, nontermainal):
        for right in self.productions[nontermainal]:
            if right[0] in self.overs:
                self.firstvt[nontermainal].add(right[0])
            else:
                if len(right)>1 and  right[1] in self.overs:
                    self.firstvt[nontermainal].add(right[1])
                if len(self.firstvt[right[0]]) ==0 :
                    self.get_firstvt(right[0])
                for new_firstvt in self.firstvt[right[0]]:
                        self.firstvt[nontermainal].add(new_firstvt)

    def get_lastvt_all(self):
        self.lastvt = defaultdict(set)
        for nontermainal in self.nonterminals:
            self.get_lastvt(nontermainal)

    # 因为不会出现互相依赖的情况,所以一定存在一个底层产生式,可以一步得到

    # 不会出现循环依赖,所以一旦lastvt[nontermainal]非空,则表示处理完毕
    def get_lastvt(self, nontermainal):
        for right in self.productions[nontermainal]:
            if right[-1] in self.overs:
                self.lastvt[nontermainal].add(right[-1])
            else:
                if len(right) > 1 and right[-2] in self.overs:
                    self.lastvt[nontermainal].add(right[-2])
                if len(self.lastvt[right[-1]]) == 0:
                    self.get_lastvt(right[-1])
                for new_lastvt in self.lastvt[right[-1]]:
                    self.lastvt[nontermainal].add(new_lastvt)

    def gen_matrix(self):
        return {i:None for i in self.overs}

    def get_matrix(self):
        self.matrix = defaultdict(self.gen_matrix)
        for nontermainal in self.nonterminals:
            for right in self.productions[nontermainal]:
                #非末尾符号
                for i, a in enumerate(right[:-1]):
                    # 如果是终结符
                    if a in self.overs:
                        # ...ab..., a=b
                        if right[i + 1] in self.overs:
                            self.matrix[a][right[i+1]] = 0
                        else:
                            # ...aU...., a< U中firstvt的每一个元素
                            for j in self.firstvt[right[i + 1]]:
                                self.matrix[a][j] = -1
                            # ...aUb.... a=b
                            if i+2 <len(right) and right[i + 2] in self.overs:
                                self.matrix[a][right[i+2]] = 0

                    # ...Ub....
                    elif right[i + 1] in self.overs:
                            for j in self.lastvt[a]:
                                self.matrix[j][right[i+1]] = 1
    #算符优先,无法按规则规约
    def ana(self, words):
        # 初始化分析栈stack和待分析输入符号a
        stack = ['#', ]

        for i in words:
            # 最靠近栈顶的终结符
            k = -1
            while stack[k] not in self.overs:
                k -= 1

            top_non = stack[k]

            while self.matrix[top_non][i] == 1:
                j = k-1
                len_stack = len(stack)
                while stack[j] not in self.overs or j+len_stack>=0 and self.matrix[top_non][stack[j]] ==0:
                    j-=1
                if stack[j] in self.overs:
                    j+=1
                stack = stack[:j]+['N']

                k = -1
                while stack[k] not in self.overs:
                    k -= 1
                top_non = stack[k]

            if self.matrix[top_non][i] != 1:
                stack.append(i)
        print(stack)


        



    


productions = {
    'E': ['E+T', 'T', 'E-T', 'E--'],
    'T': ['T*F', 'F', 'T/F'],
    'F': ['(E)', 'i'],
}
start = 'E'

opg_analyzer = OPGAnalyzer(start=start, productions=productions)
opg_analyzer.ana('i+i#')