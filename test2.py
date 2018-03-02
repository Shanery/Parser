
tmpfn = 'tmp-98vgi823sfsl'

import os, sys
import hw1, hw2

with open(tmpfn + '.g', 'w') as f:
    print('S -> NP VP', file=f)
    print('NP -> NP PP', file=f)
    print('NP -> Det N', file=f)
    print('PP -> P NP', file=f)
    print('VP -> VP PP', file=f)
    print('VP -> V NP', file=f)
    print('VP -> V', file=f)

with open(tmpfn + '.lex', 'w') as f:
    print('the Det', file=f)
    print('dog N', file=f)
    print('books N V', file=f)
    print('barks V', file=f)
    print('chases V', file=f)
    print('in P', file=f)
    print('park N', file=f)

g = hw1.Grammar(tmpfn)
parser = hw2.Parser(g)

s = 'the dog books the books in the park'.split()
trees = parser(s)
print('#parses', len(trees))

def tree_to_list (t):
    if t.children:
        return (t.cat, [tree_to_list(child) for child in t.children])
    else:
        return (t.cat, t.word)

trees = sorted(trees, key=tree_to_list)

def print_tree (t):
    _print_tree(t, 0)
    print()

def _print_tree (t, indent):
    f = sys.stdout
    for _ in range(indent):
        f.write(' ')
    f.write('[')
    f.write(t.cat)
    if t.children:
        for child in t.children:
            f.write('\n')
            _print_tree(child, indent+2)
    else:
        f.write(' ')
        f.write(t.word)
    f.write(']')

print_tree(trees[0])
print_tree(trees[1])

print()

vp = parser.chart['VP', 2, 8]
print('vp', type(vp), vp.cat, vp.i, vp.j)
print(len(vp.expansions))
for expansion in vp.expansions:
    print([(type(child), child.cat, child.i, child.j)
           for child in expansion])

print()

v = parser.chart['V', 2, 3]
print('v', type(v), v.cat, v.i, v.j)
print(len(v.expansions))
w = v.expansions[0]
print(type(w), repr(w))

print()

edges = parser.edges[5, 'PP']

def expansion_to_list (exp):
    if isinstance(exp, str):
        return exp
    else:
        return [(node.cat, node.i, node.j) for node in exp]

def edge_to_list (e):
    return (e.rule.lhs, e.rule.rhs, expansion_to_list(e.expansion))

def print_edge_detail (e):
    print('Edge')
    print('  rule:', type(e.rule), 'lhs=', repr(e.rule.lhs), 'rhs=', repr(e.rule.rhs))
    print('  exp:', type(e.expansion))
    if isinstance(e.expansion, str):
        print('    ', type(e.expansion), repr(e.expansion))
    else:
        for node in e.expansion:
            print('    ', type(node), node.cat, node.i, node.j)

for edge in sorted(edges, key=edge_to_list):
    print_edge_detail(edge)

with open(tmpfn + '.g', 'w') as f:
    print('''Root -> S
Root -> Wh VP
S -> NP VP
NP -> Name
NP -> NP RC
RC -> RP VP
NP -> Det N1
N1 -> Adj N1
N1 -> N
VP -> V
VP -> V NP
VP -> V NP PP
PP -> P NP''', file=f)

with open(tmpfn + '.lex', 'w') as f:
    print('''a Det
barks V
big Adj
blue Adj
cat N
chases V
dog N
Fido Name
gives V
green Adj
likes V
little Adj
Max Name
present N
Spot Name
the Det
to P
who Wh RP''', file=f)

parser = hw2.Parser(hw1.Grammar(tmpfn))

for sent in ('the dog barks',
             'Spot chases the cat',
             'a big blue dog chases the little green cat',
             'Max gives a present to Fido',
             'who chases the dog',
             'the big cat who chases Fido likes Spot'):
    print()
    for tree in parser(sent.split()):
        print(tree_to_list(tree))

os.unlink(tmpfn + '.g')
os.unlink(tmpfn + '.lex')
