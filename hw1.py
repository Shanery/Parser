import random

class Tree:
    def __init__(self, category, children=None, word=None):
        self.cat = category
        self.word = word
        self.children = children

        if word == None:
            self.terminal = None

    def __str__(self):
        return self.NodeString(self, 0)

    def NodeString(self, node, indent):
        string = ""
        for i in range(indent):
            string += ' '

        string += '(' + str(node.cat)

        if isleaf(node):
            print (node.word)
            string += ' ' + node.word + ')'
            return string
        else:
            string += ("\n")
            for child in node.children:
                string += self.NodeString(child, indent + 2)
                if child != node.children[-1]: string += "\n"

        string += (')')
        return string


def isleaf(node):
    if node.word != None:
        return True
    else:
        return False


def isinterior(node):
    if node.children != None:
        return True
    else:
        return False


def parse_tree(string):
    parts = string.split()
    if parts[0][0] != "(":
        print("Error. First Character was not (")

    pointer = { "node": 0 }
    return parse_subtree(parts, pointer)

def parse_subtree(parts, pointer):
    cat = parts[pointer["node"]][1:]

    pointer["node"] += 1
    if parts[pointer["node"]][0] == "(":
        children = []
        while parts[pointer["node"]][0] == "(":
            current = pointer["node"]
            children.append(parse_subtree(parts, pointer))
            if pointer["node"] == len(parts) - 1 or parts[current + 1][-2] == ")": 
                break
            else:
                pointer["node"] += 1
                if pointer["node"] >= len(parts): break

        return Tree(cat, children=children)
    else:
        word = parts[pointer["node"]]
        word = word[:word.find(")")]
        return Tree(cat, word=word)


def terminal_string(tree):
    words = [] 

    def find_words(node, words):
        if isleaf(node):
            words.append(node.word)
        else:
            for child in node.children:
                find_words(child, words)

    find_words(tree, words)

    return " ".join(words)


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
                self.prts.add(word, part)
                self.wrds.add(part, word)

        file.close()

    def parts(self, word):
        return self.prts[word]

    def words(self, part):
        return self.wrds[part]


class Rule:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return self.lhs + " -> " + " ".join(self.rhs)


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
            parts = line.split()

            if parts[1] != "->":
                print("Error in read line")
                exit()

            self.exps.add(parts[0][0], Rule(parts[0], parts[2:]))
            self.conts.add(parts[2][0], Rule(parts[0], parts[2:]))

        self.start = lines[0].split()[0]

        grammar.close()

    def expansions(self, part):
        return self.exps[part]

    def continuations(self, part):
        return self.conts[part]

    def isterm(self, part):
        return self.exps[part] == []

    def generate(self):
        def generate_from(cat):
            if self.isterm(cat):
                return Tree(cat, word=random.choice(self.lexicon.words(cat)))
            else: 
                # rule = random.choice(self.expansions(cat))
                rule = self.expansions(cat)[0]
                children = []
                for part in rule.rhs:
                    children.append(generate_from(part))
                return Tree(cat, children=children)

        return generate_from(self.start)

# d = Tree("Det", word="the")
# np = Tree("NP", [d, Tree("N", word="dog")])
# vp = Tree("VP", [Tree("V", word="barks")])
# s = Tree("S", [np, vp, Tree("Adv", word="loudly")])

# print(s)

# x = parse_tree("(S\n (NP\n (Det the)\n (N dog))\n (VP\n (V barks))\n (Adv loudly))")
# print (x)

# print(terminal_string(s))


# idx = Index()
# idx.add('foo', 10)
# idx.add('bar', 12)
# idx.add('foo', 20)

# print(idx['foo'])
# print(idx['bar'])
# print(idx['hi'])

# lex = Lexicon('g0.lex')
# print(lex.parts('book'))
# print(lex.words('N'))

# r = Rule('S', ['NP', 'VP'])
# print(r.lhs)
# print(r.rhs)
# print(r)

# g = Grammar('g0')
# print(g.lexicon.parts('book'))
# print(g.lexicon.words('N'))

# print(g.expansions("VP"))
# print(g.continuations("NP"))

# print(g.isterm("NP"))
# print(g.isterm("N"))
# print(g.isterm("V"))

# print(g.generate())

# print(g.start)

# print(g.expansions("S")[0])
# print(g.continuations("VP")[0])