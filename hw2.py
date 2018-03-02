from hw1 import Tree, Grammar, Index, Rule
import sys

class Parser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.chart = {}
        self.edges = Index()
        self.todo = []
        self.words = None

    def reset(self):
        self.chart = {}
        self.edges = Index()
        self.todo = []

    def __call__(self, words):
        self.reset()
        self.words = words

        #Main Loop
        for j in range(1, len(words) + 1):           
            self.Shift(j)
            while self.todo:
                self.step()

        if (self.grammar.start, 0, len(self.words)) in self.chart:
            node = self.chart[(self.grammar.start, 0, len(self.words))]

            return node.trees()
        else:
            return []

    def ToAdd(self, item):
        self.todo.append(item)

    def step(self):
        item = None
        if self.todo:
            item = self.todo[-1]
        self.todo.pop()

        if (item[0] == "node"):
            self.AddNode(*item[1:])
        elif (item[0] == "edge"):
            self.AddEdge(item[1])
        else:
            print("Error: Item/Tuple wasn't a \"node\" or \"edge\" ")
            sys.exit(1)

        

    def AddNode(self, pos, expansion, i, j):
        if (pos, i, j) in self.chart:
            existing = self.chart[(pos, i, j)]
            existing.add(expansion)
        else:
            node = Node(pos, expansion, i, j)
            self.chart[(pos, i, j)] = node
            self.Start(node)
            self.Combine(node)

    def AddEdge(self, edge):
        afterdot = edge.afterdot()
        if afterdot:
            i = edge.end()
            self.edges.add((i, afterdot), edge)
        else:
            assert(len(edge.expansion) == len(edge.rule.rhs))
            self.Complete(edge)   

    def Shift(self, j):
        word = self.words[j - 1]
        parts = self.grammar.lexicon.parts(word)
        for pos in parts:
            self.ToAdd(("node", pos, word, j-1, j))

    def Start(self, node):
        for rule in self.grammar.continuations(node.cat):
            self.ToAdd(("edge", Edge(rule, [node])))

    def Combine(self, node):
        edges = self.edges[(node.i, node.cat)]
        for edge in edges:
            if edge.afterdot() == node.cat and edge.end() == node.i:
                item = edge + node
                assert(isinstance(item, Edge))
                self.ToAdd(("edge", item))
                

    def Complete(self,e):
        assert(isinstance(e, Edge))
        cat = e.rule.lhs
        i = e.expansion[0].i
        j = e.expansion[-1].j
        self.ToAdd(("node", cat, e.expansion, i, j))


class Node:
    def __init__(self, cat, item, i, j):
        self.cat = cat
        self.i = i
        self.j = j
        self.expansions = [item]

    def add(self, expansion):
        if not(expansion in self.expansions):
            self.expansions.append(expansion)

    def __repr__(self):
        return " ".join([str(self.cat), str(self.i), str(self.j)])

    def trees(self):
        return list(self.itertrees())

    def itertrees(self):
        for e in self.expansions:
            if isinstance(e, str):
                yield Tree(self.cat, word=e)
            else:
                for childlist in tree_expansions(e):
                    yield Tree(self.cat, childlist)

class Edge:
    def __init__(self, rule, expansion):
        self.rule = rule
        self.expansion = expansion

    def __str__(self):
        string = self.rule.lhs + " -> ["
        for node in self.expansion:
            string += " ".join([str(node.i), node.cat, str(node.j)])
        string += "]" + " * " + self.afterdot()
        return string

    def __repr__(self):
        return "<Edge " + self.__str__() + ">"

    def cat(self):
        return self.rule.lhs

    def start(self):
        return self.expansion[0].i

    def end(self):
        return self.expansion[-1].j

    # Adding node to an edge
    def __add__(self, rhs):
        new = Edge(self.rule, self.expansion + [rhs])
        assert(isinstance(new, Edge))
        return new

    def afterdot(self):
        dot_pos = len(self.expansion)
        if dot_pos >= len(self.rule.rhs):
            return None
        else:
            return self.rule.rhs[dot_pos]

def cross_product(items):
    product = [tuple()]

    for row in items:
        new_products = []
        for a in product:
            for b in row:
                new_products.append((*a, b))
        product = new_products

    return product

def tree_expansions(node_exps):
    choices = [n.trees() for n in node_exps]
    return cross_product(choices)

# r = Rule('S', ['NP', 'VP'])
# n = Node('NP', 'I', 0, 1)
# e = Edge(r, [n])
