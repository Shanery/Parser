
import sys, os, runpy
from traceback import print_tb

# Usage: python3 -m test parser
#   -! causes stack trace to be printed for errors
#   parser_dir defaults to current directory
#   If GRAMMARS is set, will look for grammars there, otherwise in current directory

gdir = os.getenv('GRAMMARS') or os.getcwd()
parser_dir = os.getcwd()
show_traceback = False
ac = 1
if ac < len(sys.argv) and sys.argv[ac] == '-!':
    show_traceback = True
    ac += 1
if ac < len(sys.argv):
    parser_dir = sys.argv[ac]

fg0 = os.path.join(gdir, 'fg0')
fg1 = os.path.join(gdir, 'fg1')

for fn in (fg0 + '.g', fg0 + '.lex', fg1 + '.g', fg1 + '.lex', fg1 + '.sents'):
    if not os.path.exists(fn):
        raise Exception('Not found: %s' % fn)

sys.path = [parser_dir] + sys.path

def lst_word (lst):
    if len(lst) == 2 and isinstance(lst[1], str):
        return lst[1]

def tree_equal (t, lst):
    if t.cat != lst[0]:
        return False
    elif t.word:
        return t.word == lst_word(lst)
    elif lst_word(lst):
        return False
    elif len(t.children) != len(lst)-1:
        return False
    else:
        for (tc, lc) in zip(t.children, lst[1:]):
            if not tree_equal(tc, lc):
                return False
    return True

class Tester (object):
    
    def __init__ (self):
        self.count = 0
        self.npassed = 0

    def __enter__ (self):
        self.count += 1
        self.passed = True
        return self

    def __exit__ (self, t, v, tb):
        if t:
            print('** ERROR (%s):' % t.__name__, v)
            if show_traceback: print_tb(tb)
        elif self.passed:
            self.npassed += 1
        return True

    def __call__ (self, msg):
        print('>> Test', msg)
        return self

    def test (self, equal, value, ref):
        if not equal:
            self.passed = False
            print('** FAILURE')
            print('   Expected:', repr(ref))
            print('   Got:', repr(value))

    def eq (self, value, ref):
        test.test(value == ref, value, ref)

    def tree (self, value, ref):
        test.test(tree_equal(value, ref), value, ref)

    def __str__ (self):
        return 'Passed %d out of %d' % (self.npassed, self.count)

test = Tester()


#--  Tests  --------------------------------------------------------------------

with test('import parser'):
    import parser

with test('Category.__repr__'):
    cat = parser.Category(['X', 'y', 1, 0])
    test.eq(repr(cat), 'X.y.$1.$0')

with test('Category'): test.eq(cat[0], 'X')
with test('Category'): test.eq(cat[1], 'y')
with test('Category'): test.eq(cat[2], 1)
with test('Category'): test.eq(cat[3], 0)
with test('Category'): test.eq(len(cat), 4)
with test('Category'): test.eq(tuple(cat), ('X', 'y', 1, 0))

with test('parse_category cat'):
    symtab = {}
    cat = parser.parse_category('A.x.$x', symtab)
    test.eq(type(cat), parser.Category)
    test.eq(cat, ('A','x',0))

with test('parse_category symtab'):
    test.eq(sorted(symtab.items()), [('x', 0)])

with test('parse_category cat'):
    cat = parser.parse_category('B.$y.int.$x', symtab)
    test.eq(type(cat), parser.Category)
    test.eq(cat, ('B',1,'int',0))

with test('parse_category symtab'):
    test.eq(sorted(symtab.items()), [('x', 0), ('y', 1)])

with test('parse_category cat'):
    cat = parser.parse_category('C.$y', symtab)
    test.eq(type(cat), parser.Category)
    test.eq(cat, ('C',1))

with test('parse_category symtab'):
    test.eq(sorted(symtab.items()), [('x', 0), ('y', 1)])

with test('meet'): test.eq(parser.meet('b', 'c'), None)
with test('meet'): test.eq(parser.meet('c', 'c'), 'c')
with test('meet'): test.eq(parser.meet('c', '*'), 'c')
with test('meet'): test.eq(parser.meet('*', 'c'), 'c')
with test('meet'): test.eq(parser.meet('*c', 'c'), None)
with test('meet'): test.eq(parser.meet('*', '*'), '*')

with test('symtab'):
    t = {}
    C = parser.parse_category
    rhs = (C('V.$f.i.$p', t), C('PP.$p', t))
    chcats = (C('V.sg.i.*'), C('PP.to'))
    
    test.eq(len(t), 2)

with test('unify'):
    b0 = ('*', '*')
    b1 = parser.unify(rhs[0], chcats[0], b0)
    b2 = parser.unify(rhs[1], chcats[1], b1)
    
    test.eq(b1, ('sg', '*'))

with test('unify'):
    test.eq(b2, ('sg', 'to'))

with test('unify'):
    b3 = parser.unify(rhs[0], chcats[0], ('pl', '*'))
    test.eq(b3, None)

with test('unify exception'):
    # should throw an exception if the second category contains variables
    try:
        parser.unify(rhs[0], rhs[0], b0)
        exception = False
    except:
        exception = True
    test.eq(exception, True)

with test('subst'):
    lhs = C('X.$p.bar.$f', t)
    cat = parser.subst(b2, lhs)
    test.eq(cat, C('X.to.bar.sg'))

with test('subst'):
    cat = parser.subst(b1, lhs)
    test.eq(cat, C('X.*.bar.sg'))

with test('parts'):
    lex = parser.Lexicon(fg0 + '.lex')
    test.eq(lex.parts('barked'), [C('V.*.i.0')])

with test('parts'):
    test.eq(sorted(lex.parts('bark')), [C('N.sg'), C('V.pl.i.0')])

with test('rule'):
    t = {}
    lhs = C('VP.$f', t)
    rhs = [C('V.$f.t.$p', t), C('NP.*', t), C('PP.$p', t)]
    rule = parser.Rule(lhs, rhs, ('*', '*'))
    test.eq(rule.lhs, ('VP',0))

with test('rule'):
    test.eq(rule.rhs, [('V',0,'t',1), ('NP','*'), ('PP',1)])

with test('rule.__repr__'):
    test.eq(repr(rule), 'VP.$0 -> V.$0.t.$1 NP.* PP.$1')

with test('continuations'):
    g0 = parser.Grammar(fg0)
    test.eq([repr(r) for r in g0.continuations('V')], ['VP.$0 -> V.$0.i.0'])

with test('load grammar'):
    g1 = parser.Grammar(fg1)
    
with test('continuations'):
    test.eq(sorted(repr(r) for r in g1.continuations('Aux')),
            ['Root -> Aux.$0.$1 NP.$0 VP.$1.-',
             'VP.$0.$1 -> Aux.$0.$2 VP.$2.$1',
             'VP.$0.- -> Aux.$0.pred AdjP',
             'VP.$0.- -> Aux.$0.pred NP.*'])

with test('g1.lexicon.parts'):
    test.eq(sorted(str(pos) for pos in g1.lexicon.parts('be')),
            ['Aux.base.enp', 'Aux.base.ing', 'Aux.base.pred'])

with test('Node'):
    if hasattr(parser, 'Node'): from parser import Node
    v = Node(C('V.sg.t.*'), 'chases', 2, 3)
    test.eq(v.cat, ('V','sg','t','*'))
    test.eq(v.i, 2)
    test.eq(v.j, 3)

with test('e.__str__'):
    e = parser.Edge(rule, [v], ('sg', '*'))
    test.eq(str(e), 'VP.$0 -> [2 V.sg.t.* 3] * NP.* PP.$1 : sg *')

with test('e.__repr__'):
    test.eq(repr(e), '<Edge VP.$0 -> [2 V.sg.t.* 3] * NP.* PP.$1 : sg *>')

with test('p.reset'):
    p = parser.Parser(g0)
    p.reset('this dog barks'.split())
    test.eq(p.chart, {})

with test('p.reset'):
    test.eq(p.edges[1, 'N'], [])

with test('p.reset'):
    test.eq(list(p.todo), [])

with test('p.reset'):
    p.chart['Det', 0, 1] = 42
    p.edges.add((1,'N'), 42)
    p.todo.append(42)
    p.reset('this dog barks'.split())
    test.eq(p.chart, {})

with test('p.reset'): test.eq(p.edges[1, 'N'], [])
with test('p.reset'): test.eq(list(p.todo), [])

with test('parts'):
    DetSg = C('Det.sg')

    test.eq(p.grammar.lexicon.parts('this'), [DetSg])

with test('shift'):
    p.shift(1)
    test.eq(list(p.todo), [('node', DetSg, 'this', 0, 1)])

with test('chart'):
    p.step()
    test.eq(str(p.chart[DetSg, 0, 1]), '[0 Det.sg 1]')

with test('step 1'):
    test.eq([repr(spec) for spec in p.todo],
            ["('edge', <Edge NP.$0 -> [0 Det.sg 1] * N.$0 : sg>)"])

with test('step 2; edges'):
    p.step()
    test.eq([repr(e) for e in p.edges[1, 'N']],
            ['<Edge NP.$0 -> [0 Det.sg 1] * N.$0 : sg>'])

with test('todo'):
    test.eq([repr(spec) for spec in p.todo],
            [])

with test('shift; todo'):
    p.shift(2)
    test.eq([repr(spec) for spec in p.todo],
            ["('node', N.sg, 'dog', 1, 2)"])

with test('step 3; chart'):
    p.step()
    node = p.chart[C('N.sg'), 1, 2]
    test.eq(str(node), '[1 N.sg 2]')

with test('node.expansions'): test.eq(str(node.expansions), "['dog']")

with test('todo'):
    test.eq([repr(spec) for spec in p.todo],
            ["('edge', <Edge NP.$0 -> [0 Det.sg 1] [1 N.sg 2] * : sg>)"])

with test('step 4; todo'):
    p.step()
    test.eq([repr(spec) for spec in p.todo],
            ["('node', NP.sg, [<Node Det.sg 0 1>, <Node N.sg 1 2>], 0, 2)"])

with test('step 5; chart'):
    p.step()
    node = p.chart[C('NP.sg'), 0, 2]
    test.eq(str(node), '[0 NP.sg 2]')

with test('node.expansions'):
    test.eq(repr(node.expansions), '[[<Node Det.sg 0 1>, <Node N.sg 1 2>]]')

with test('todo'):
    test.eq([repr(spec) for spec in p.todo],
            ["('edge', <Edge S -> [0 NP.sg 2] * VP.$0 : sg>)"])

with test('step 6; edges'):
    p.step()
    test.eq([repr(e) for e in p.edges[2, 'VP']],
            ['<Edge S -> [0 NP.sg 2] * VP.$0 : sg>'])

with test('todo'):
    test.eq(list(p.todo), [])

with test('start symbol'):
    p.shift(3)
    while p.todo:
        p.step()
    
    start = p.grammar.start
    test.eq(start, C('S'))

with test('chart'):
    node = p.chart[start, 0, 3]
    test.eq(str(node), '[0 S 3]')

with test('trees'):
    ts = node.trees()
    test.eq(len(ts), 1)

with test('trees'):
    test.tree(ts[0], [('S',),
                      [('NP','sg'),
                       [('Det','sg'), 'this'],
                       [('N','sg'), 'dog']],
                      [('VP','sg'),
                       [('V','sg','i','0'), 'barks']]])

with test('call'):
    ts = p('these dogs bark'.split())
    test.eq(len(ts), 1)

with test('call'):
    test.tree(ts[0], [('S',),
                      [('NP','pl'),
                       [('Det','pl'), 'these'],
                       [('N','pl'), 'dogs']],
                      [('VP','pl'),
                       [('V','pl','i','0'), 'bark']]])

with test('create parser'):
    p = parser.Parser(parser.Grammar(fg1))

with open(fg1 + '.sents') as f:
    for (i, line) in enumerate(f):

        with test('sent %d' % i):
            trees = p(line.split())
            test.eq(len(trees), 1)


#--  End  ----------------------------------------------------------------------

print(test)
