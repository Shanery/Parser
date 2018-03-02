
Start -> Root
Start -> NP.*
Start -> PP.*

# Verb complements
VP.$f.- -> V.$f.i.0
VP.$f.- -> V.$f.t.0 NP.*
VP.$f.+ -> V.$f.t.0
VP.$f.- -> V.$f.t.np NP.* NP.*
VP.$f.+ -> V.$f.t.np NP.*
VP.$f.- -> V.$f.i.$p PP.$p
VP.$f.- -> V.$f.t.$p NP.* PP.$p
VP.$f.+ -> V.$f.t.$p PP.$p
VP.$f.$g -> V.$f.i.$c SC.$c.$g
VP.$f.$g -> V.$f.t.$c NP.* SC.$c.$g

VP.$f.$g -> Aux.$f.$v VP.$v.$g
VP.$f.- -> Aux.$f.pred AdjP
VP.$f.- -> Aux.$f.pred NP.*

# Adjuncts
# VP.$f.$g -> VP.$f.$g PP.*
# VP.$f.$g -> VP.$f.$g AdvP
# VP.$f.$g -> VP.$f.$g SC.*

# NP
NP.sg -> Names
Names -> Name Names
Names -> Name
NP.$n -> Pron.$n
NP.$n -> Pron.$n RC.$n
NP.$n -> Det.$n Q.$n N2.$n
NP.$n -> Det.$n N2.$n
NP.pl -> Q.pl N2.pl
NP.$n -> Det.$n Q.$n
NP.pl -> N2.pl
N2.$n -> N2.$n PP.loc
N2.$n -> N2.$n AdjP
N2.$n -> N2.$n RC.$n
N2.$n -> N1.$n
N1.$n -> Adj N1.$n
N1.$n -> N.$n PP.of
N1.$n -> N.$n

# WhNP
WhNP.$n -> WhPron.$n

# PP
PP.$p -> P.$p NP.*

# Q
Q.$n -> Num.$n

# AdjP
AdjP -> Adj
AdjP -> Deg Adj

# Clauses
Root -> S.-
Root -> Aux.$n.$v NP.$n VP.$v.-
Root -> WhNP.* Aux.$n.$v NP.$n VP.$v.+
Root -> WhNP.$n VP.$n.-
S.$g -> NP.$n VP.$n.$g
RC.$n -> RelPron VP.$n.-
RC.* -> RelPron NP.$n VP.$n.+

S.- -> S.- Conj.* S.-
S.- -> Preconj.$t S.- Conj.$t S.-
