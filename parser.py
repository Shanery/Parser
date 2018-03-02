import re
import data_structs
from data_structs import Tree

class Index:
    def __init__(self):
        self.map = {}

    def __getitem__(self, key):
        if key in self.map:
            return self.map[key]
        else:
            return []

    def add(self, key, value):
        if key in self.map:
            self.map[key].append(value)
        else:
            self.map[key] = [value]


class Category(tuple):
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        parts = []
        for part in self:
            if isinstance(part, int):
                parts.append("$" + str(part))
            else: 
                parts.append(str(part))
        return ".".join(parts)

def tokenize(string):
    return re.findall(r'\(|\)|[^()\s]+',string)

def parse_category(string, table=None):
    parts = string.split('.')
    
    cat = []
    for part in parts:
        if part[0] == '$':
            if table == None:
                print('Exception: Variables are not allowed')
                return None
            
            symbol = part[1:]
            if symbol in table:
                cat.append(table[symbol])
            else:
                cat.append(len(table))
                table[symbol] = len(table)
        else:
            cat.append(part)

    return Category(cat)

def meet(left, right):    
    if left == right:
        return left
    elif isinstance(left, int) or left == '*':
        return right
    elif right == '*':
        return str(left)

def unify(x,y,b):

    if x[0] != y[0] or len(x) != len(y):
        print("Type is wrong")
        return None

    bindings = list(b)
    for i in range(len(x)):
        u = x[i]
        v = y[i]

        if isinstance(v, int):
            raise 
            return None
        
        is_variable = isinstance(u, int)

        if is_variable:
            u = bindings[u]
        
        val = meet(u, v)

        if val:
            if is_variable:
                bindings[x[i]] = val
        else:
            return None
 
    return tuple(bindings)
    
def subst(b, x):
    cat = list(x)

    for i in range(len(cat)):
        feature = cat[i]
        if isinstance(feature, int):
            cat[i] = b[feature]
    
    return Category(cat)
        
    
class Lexicon:
    def __init__(self, file_name):
        self.wrds = Index()
        self.prts = Index()

        file = open(file_name, "r")

        lines = file.readlines()

        for line in lines:
            secs = line.split()

            word = secs[0]

            for part in secs[1:]:
                cat = parse_category(part)
                self.prts.add(word, cat)
                self.wrds.add(cat[0], word)

        file.close()

    def parts(self, word):
        return self.prts[word]

    def words(self, part):
        return self.wrds[part]

class Rule:
    def __init__(self, lhs, rhs, b=None):
        self.lhs = lhs
        self.rhs = rhs
        self.bindings = b

        assert(isinstance(lhs, Category))
        for cat in rhs:
            assert(isinstance(cat, Category))

        if not b:
            num_vars = 0
            for feature in lhs:
                if isinstance(feature, int):
                    num_vars = max(num_vars, feature + 1)

            for cat in rhs:
                for feature in cat:
                    if isinstance(feature, int):
                        num_vars = max(num_vars, feature + 1)

            self.bindings = tuple(['*' for x in range(num_vars)])

    def __repr__(self):
        return str(self.lhs) + " -> " + " ".join([str(cat) for cat in self.rhs])

class Grammar:
    def __init__(self, file_name):
        self.file_name = file_name
        self.exps = Index()
        self.conts = Index()

        self.load()

    def load(self):
        self.lexicon = Lexicon(self.file_name + ".lex")
        self.exps = Index()
        self.conts = Index()

        grammar = open(self.file_name + ".g", "r")
        lines = grammar.readlines()

        for line in lines:
            if line == "\n" or line[0] == '#':
                lines.remove(line)

        for line in lines:
            if line == "\n" or line[0] == '#':
                continue

            parts = line.split()
            
            if parts[1] != "->":
                print("Error in read line")
                exit()

            t = {}
            for i in range(len(parts)):
                if i != 1:
                    parts[i] = parse_category(parts[i],t)
            
            assert(isinstance(parts[0], Category))
            self.exps.add(parts[0][0], Rule(parts[0], parts[2:]))
            assert(isinstance(parts[2], Category))
            self.conts.add(parts[2][0], Rule(parts[0], tuple(parts[2:])))

        self.start = parse_category(lines[0].split()[0])

        # print("\n")

        grammar.close()

    def expansions(self, part):
        return self.exps[part]

    def continuations(self, part):
        return self.conts[part]

    def isterm(self, part):
        return self.exps[part] == []

class Edge:
    def __init__(self, rule, expansion, bindings):
        self.rule = rule
        self.expansion = expansion
        self.bindings = bindings

    def __repr__(self):
        return "<Edge " + self.__str__() + ">"

    def __str__(self):
        string = str(self.rule.lhs) + " -> "
        for node in self.expansion:
            # print (self.expansion)
            string += "[" + " ".join([str(node.i), str(node.cat), str(node.j)]) + "] "
        string += "* "

        for part in self.rule.rhs[len(self.expansion):]:
            string += str(part) + " "
            
        string += ": " + " ".join([feature for feature in self.bindings])
        return string
    
    def __add__(self, rhs):
        assert(isinstance(rhs, Node))
        new = Edge(self.rule, self.expansion + [rhs], self.rule.bindings)
        assert(isinstance(new, Edge))
        return new

    def cat(self):
        return self.rule.lhs

    def start(self):
        return self.expansion[0].i

    def end(self):
        return self.expansion[-1].j

    def afterdot(self):
        dot_pos = len(self.expansion)
        if dot_pos >= len(self.rule.rhs):
            return None
        else:
            return self.rule.rhs[dot_pos]

class Parser():
    def __init__(self, grammar):
        self.grammar = grammar
        self.chart = {}
        self.edges = Index()
        self.todo = []
        self.words = None

    def reset(self, words):
        self.chart = {}
        self.edges = Index()
        self.todo = []
        self.words = words

    def __call__(self, words):
        self.reset(words)

        #Main Loop
        for j in range(1, len(words) + 1):           
            self.shift(j)
            while self.todo:
                self.step()

        if (self.grammar.start, 0, len(self.words)) in self.chart:
            node = self.chart[(self.grammar.start, 0, len(self.words))]

            # print (node)

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
            self.start(node)
            self.combine(node)

    def AddEdge(self, edge):
        afterdot = edge.afterdot()
        if afterdot:
            j = edge.end()
            self.edges.add((j, afterdot[0]), edge)
        else:
            assert(len(edge.expansion) == len(edge.rule.rhs))
            self.complete(edge)   
            
    def shift(self, j):
        word = self.words[j - 1]
        parts = self.grammar.lexicon.parts(word)
        for pos in parts:
            self.ToAdd(("node", pos, word, j-1, j))

    def start(self, node):
        assert(isinstance(node.cat[0], str))
        for rule in self.grammar.continuations(node.cat[0]):

            query = unify(rule.rhs[0], node.cat, rule.bindings)
            
            if query != None:
                self.ToAdd(("edge", Edge(rule, [node], query)))

    def combine(self, node):
        edges = self.edges[(node.i, node.cat[0])]
        for edge in edges:
            if edge.afterdot()[0] == node.cat[0] and edge.end() == node.i:
                query = unify(edge.afterdot(), node.cat, edge.bindings)
                edge = edge + node
                if query != None:
                    edge.bindings = query
                    self.ToAdd(("edge", edge))
                
                assert(isinstance(edge, Edge))
                
    def complete(self,e):
        assert(isinstance(e, Edge))
        cat = subst(e.bindings, e.rule.lhs)
        i = e.expansion[0].i
        j = e.expansion[-1].j
        self.ToAdd(("node", cat, e.expansion, i, j))

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


class Node:
    def __init__(self, cat, item, i, j):
        self.cat = cat
        self.i = i
        self.j = j
        self.expansions = [item]

    def add(self, expansion):
        if not(expansion in self.expansions):
            self.expansions.append(expansion)

    def trees(self):
        return list(self.itertrees())

    def itertrees(self):
        for e in self.expansions:
            if isinstance(e, str):
                yield Tree(self.cat, word=e)
            else:
                for childlist in tree_expansions(e):
                    yield Tree(self.cat, childlist)

    def __repr__(self):
        return '<Node ' + " ".join([str(self.cat), str(self.i), str(self.j)]) + '>'

    def __str__(self):
        return '[' + " ".join([str(self.i), str(self.cat), str(self.j)]) + ']'


x = Category(["V", 0, 'i', '0'])
print(x)

y = tokenize("V.$f.i.0")
print(y)

y = "V.$f.i.0".split('.')
print(y)

z = parse_category("V.$f.i.0")
print(z)

t = {}
z = parse_category("V.$f.i.$x", t)
print(z)

print(t)


if meet("a", "*") != "a":
    print ("Error. Expected \"a\". Got:" + meet("a", "*"))

if meet("*", "b") != "b":
    print ("Error. Expected \"b\". Got:" + meet("*", "b"))

if meet("*", "*") != "*":
    print ("Error. Expected \"*\". Got:" + meet("*", "*"))

if meet("a", "b") != None:
    print ("Error. Expected \"None\". Got:" + meet("a", "*"))


# Test Parse
# t={}
# rhs = (parse_category('V.$f.i.$p', t), parse_category('PP.$p', t))
# ccats = (parse_category('V.sg.i.*'), parse_category('PP.to'))
# b = ['*', '*']
# b2 = unify(rhs[0], ccats[0], b)
# print (b2)
# b3 = unify(rhs[1], ccats[1], b2)
# print (b3)

# lhs = parse_category('X.$p.i.$f', t)
# print (subst(b3, lhs))

# t = {}
# np = parse_category('NP.$n', t)
# det = parse_category('Det.$n', t)
# n = parse_category('N.$n', t)
# r = Rule(np, [det,n], ('*',))
# print (r)

# g = Grammar('fg0')

# print(g.continuations('V'))

# print (g.lexicon.parts('bark'))
# print (g.continuations('Det'))


# e = Edge(r, [Node(det, 'this', 0, 1)], ('sg',))
# print(e)

# lex = Lexicon('fg0.lex')
# print (lex.parts('barked'))


# print("\n\n")

# p = Parser(Grammar('fg1'))
# x = p('the dog barks'.split())
# print (x[0])

# # print(p.grammar.conts.map)

# # print(p.grammar.continuations('Root'))

# x = p('Tuna is a cat'.split())
# print (x[0])

