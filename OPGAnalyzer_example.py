import pandas as pd
import time

class OPGAnalyzer_example:
    def __init__(self, start, overs, productions, log_level=0):
        self.productions = productions
        self.productions['S'] = ['#' + start + '#', ]
        self.nonterminals = self.productions.keys()
        self.overs = overs
        self.overs.append('#')
        self.log_level = log_level
        self.get_firstvt()
        self.get_lastvt()
        self.get_relation_matrix()

    # 生成firstvt集
    def get_firstvt(self):
        self.firstvt = {nontermainal: set() for nontermainal in self.nonterminals}
        stack = []
        # 根据规则1，遍历产生式
        for nontermainal in self.nonterminals:
            for right in self.productions[nontermainal]:
                # 若有规则U→b…或规则U→Vb…，将b加入U的firstvt集中，同时将元组(U, b)入栈
                if right[0] in self.overs:
                    self.firstvt[nontermainal].add(right[0])
                    stack.append((nontermainal, right[0]))
                if len(right) > 1 and right[1] in self.overs and right[0] in self.nonterminals:
                    self.firstvt[nontermainal].add(right[1])
                    stack.append((nontermainal, right[1]))
        # 根据规则2，反复遍历产生式直到栈为空
        while len(stack) > 0:
            V, b = stack.pop()
            for nontermainal in self.nonterminals:
                for right in self.productions[nontermainal]:
                    # 对每一个形如U→V…的规则
                    if V == right[0]:
                        # 如果b不在U的firstvt集中，将b加入U的firstvt集中，同时将元组(U, b)入栈
                        if b not in self.firstvt[nontermainal]:
                            self.firstvt[nontermainal].add(b)
                            stack.append((nontermainal, b))
        if self.log_level:
            print(self.firstvt)

    # 生成lastvt集
    def get_lastvt(self):
        self.lastvt = {nontermainal: set() for nontermainal in self.nonterminals}
        stack = []
        # 根据规则1，遍历产生式
        for nontermainal in self.nonterminals:
            for right in self.productions[nontermainal]:
                # 若有规则U→…a或规则U→…aV，将a加入U的lastvt集中，同时将元组(U, a)入栈
                if right[-1] in overs:
                    self.lastvt[nontermainal].add(right[-1])
                    stack.append((nontermainal, right[-1]))
                if len(right) > 1 and right[-2] in self.overs and right[-1] in self.nonterminals:
                    self.lastvt[nontermainal].add(right[-2])
                    stack.append((nontermainal, right[-2]))
        # 根据规则2，反复遍历产生式直到栈为空
        while len(stack) > 0:
            V, a = stack.pop()
            for nontermainal in self.nonterminals:
                for right in self.productions[nontermainal]:
                    # 对每一个形如U→…V的规则
                    if V == right[-1]:
                        # 如果a不在U的lastvt集中，将a加入U的firstvt集中，同时将元组(U, a)入栈
                        if a not in self.lastvt[nontermainal]:
                            self.lastvt[nontermainal].add(a)
                            stack.append((nontermainal, a))
        if self.log_level:
            print(self.lastvt)

    # 生成优先矩阵
    def get_relation_matrix(self):
        # 1为大于，0为等于，-1为小于
        self.relation_matrix = pd.DataFrame(index=overs, columns=overs)
        # 对于每一条规则
        for nontermainal in self.nonterminals:
            for right in self.productions[nontermainal]:
                # 对于产生式右部的每一个非末尾符号
                for i, a in enumerate(right[:-1]):
                    # 如果是终结符
                    if a in self.overs:
                        # 如果是形如…ab…的产生式右部，置a=b
                        if right[i + 1] in self.overs:
                            b = right[i + 1]
                            self.relation_matrix[a][b] = 0
                        else:
                            # 如果是形如…aU…的产生式右部，对于U的firstvt集中的每一个非终结符b，置a<b
                            for b in self.firstvt[right[i + 1]]:
                                self.relation_matrix[a][b] = -1
                            # 如果是形如…aVb…的产生式右部，置a=b
                            if i + 2 < len(right) and right[i + 2] in self.overs:
                                b = right[i + 2]
                                self.relation_matrix[a][b] = 0
                    # 如果是形如…Ub…的产生式右部，对于U的firstvt集中的每一个非终结符a_，置a_>b
                    elif right[i + 1] in self.overs:
                        U, b = a, right[i + 1]
                        for a_ in self.lastvt[U]:
                            self.relation_matrix[a_][b] = 1
        if self.log_level:
            # 行列违反直觉，故转置输出
            print(self.relation_matrix.T)

    # 判断string是否不是任何一个产生式的右部
    def is_not_right(self, string):
        for nontermainal in self.nonterminals:
            for right in self.productions[nontermainal]:
                tag = True
                # 如果string长度和right不相同，当然不是，下一个产生式
                if len(right) != len(string):
                    continue
                # 逐个比对right和string的符号
                for ch1, ch2 in zip(right, string):
                    # 如果终结符号与非终结符号类别不相同，不是，下一个产生式
                    if (ch1 in self.overs and ch2 not in self.overs) or (ch1 not in self.overs and ch2 in self.overs):
                        tag = False
                        break
                    # 如果是均为终结符号，如果不相同，不是，下一个产生式
                    if ch1 in self.overs and ch1 != ch2:
                        tag = False
                        break
                # 匹配到某一产生式右部，返回False
                if tag:
                    return False
        # 没有匹配到任何一个产生式右部，返回True
        return True

    def print_fail_info(self, info=''):
        print('fail', self.raw_string, '[%d, %s] %s.' % (self.index, self.a, info))

    # 分析算法的主体程序
    def OPG(self):
        # 初始化分析栈stack和待分析输入符号a
        stack = ['#', ]

        # 从本质上说，每轮循环都是在找最左素短语，即最靠近栈顶拥有<…>形式的短语
        while True:
            # 由于只有终结符号有偏序关系，先找到最接近栈顶的终结符号
            j = -1
            while stack[j] not in self.overs:
                j -= 1
            # 如果该终结符号 > 待分析输入符号a，这是可能被规约的情况
            if self.relation_matrix[stack[j]][self.a] == 1:
                # 查找<关系
                while True:
                    # temp记录较为靠近栈顶的终结符号
                    temp = stack[j]
                    # 找下一个终结符号
                    while True:
                        j -= 1
                        if j >= -len(stack) and stack[j] in self.overs or j < -len(stack):
                            break
                    # 无论找到<关系还是找不到，结束查找
                    if j < -len(stack) or self.relation_matrix[stack[j]][temp] == -1:
                        break
                # 大多数情况下，由于#的优先级总是比较低的，可以找到<关系，<与>之间的就是待归约串
                # 如果待归约串并匹配任何一个产生式右部，那么归约失败，输出失败信息并return
                # 少数情况下，找不到<关系，同样归约失败，输出失败信息并return
                if j < -len(stack):
                    self.print_fail_info('cannot find "<" relation')
                    return
                if self.is_not_right(stack[j + 1:]):
                    self.print_fail_info('cannot fit any right of productions')
                    return
                # 找到了最左素短语，归约
                stack = stack[:j + 1] + ['N', ]
                if self.log_level:
                    print(stack, j, self.a)
                # 归约后检查是否满足成功条件，满足则输出成功信息并return
                # 不满足则继续查找素短语
                if stack == ['#', 'N'] and self.a == '#':
                    print('ok  ', self.raw_string)
                    return
            # 如果该终结符号 <或= 待分析输入符号a，那么不是最左素短语（重点在“左”）
            # 那么将a入栈，并分析下一个输入符号，即向右寻找最左素短语
            # 当然如果已经没有下一个输入符号，归约失败，输出失败信息并return
            else:
                if self.index == len(self.string) - 1:
                    self.print_fail_info('cannot find ">" relation')
                    return
                stack.append(self.a)
                self.index += 1
                self.a = self.string[self.index]
                if self.a not in self.overs:
                    self.print_fail_info('unfined terminal char')
                    return
                if self.log_level:
                    print(stack, j, self.a)

    # 分析程序的入口程序，过滤导致死循环的空串，并初始化string
    def analyse(self, string=''):
        self.raw_string = string
        self.index = 0
        self.string = string + '#'
        self.a = self.string[self.index]
        if string == '':
            self.print_fail_info('the input string cannot be null')
        elif self.a not in self.overs:
            self.print_fail_info('unfined terminal char')
        else:
            self.OPG()


# S和N不可以作为非终结符，为测试算法健壮性，加入文法'E→E--'
productions = {
    'E': ['E+T', 'T', 'E-T', 'E--'],
    'T': ['T*F', 'F', 'T/F'],
    'F': ['(E)', 'i'],
}
start = 'E'
nonterminals = productions.keys()
# '#'不可以作为终结符号
overs = ['+', '*', 'i', '(', ')', '/', '-']

opg_analyzer_example = OPGAnalyzer_example(start=start, productions=productions, overs=overs, log_level=0)
# 以下测试样例中，
# '='和'i=i*i'针对的是输入非法终结符号的情况
# 'i++'和'(i--+i)*i'针对的是文法'E→E--'
# ')+i'针对的是在寻找最左素短语时找不到 <关系 的情况
# '('针对的是在寻找最左素短语时找不到 >关系 的情况
string_list = ['i+i*i', 'i*i/(i+i)-i', '=', 'i=i*i', '(i+i)*i/i', '/i+', '*i', '((i*i-i)+(i))', 'i++', '(i--+i)*i', 'i-+i', '', ')+i', '(']
for string in string_list:
    opg_analyzer.analyse(string)