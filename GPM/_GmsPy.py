import os, pandas as pd, gams, pickle
from GmsWrite import OrdSet,write_gpy,write_from_db
from dreamtools.gamY import Precompiler

def d2t(x):
	return list(x.items())[0]

def arg2string(x,t):
	if t == 'file':
		with open(x,"r") as f:
			return f.read()
	elif isinstance(t,Precompiler):
		return t(as_string=x) if isinstance(x,str) else t(**x)
	elif t == 'gamY':
		return Precompiler(x)()
	elif isinstance(x,str):
		return x

class Compile:
	def __init__(self,groups,db):
		self.declared = OrdSet()
		self.groups = groups
		self.db = db

	def declareGroupText(self,g,db):
		return "\n".join([f"{g.gtype} {write_gpy(db[var])};" for var in g.conditions if var not in self.declared])

	def fixGroupText(self,g,db):
		return "\n".join([f"{write_gpy(db[k],c=v,l='.fx')} = {write_gpy(db[k],l='.l')};" for k,v in g.conditions.items()])

	def unfixGroupText(self,g,db):
		return "\n".join([f"{write_gpy(db[k],c=v,l='.lo')} = -inf;\n{write_gpy(db[k],c=v,l='.up')} = inf;" for k,v in g.conditions.items()])

class Group:
	def __init__(self,name,v=[],g=[],neg_v=[],neg_g=[],out={},out_neg={},gtype = 'variable'):
		self.name = name
		self.v = v
		self.g = OrdSet(g)
		self.neg_v = neg_v
		self.neg_g = OrdSet(neg_g)
		self.out = {}
		self.out_neg = {}
		self.gtype = gtype # should be either variable or parameter to indicate the type of symbol group.

	def c_var(self,name):
		return ('or', self.out[name]) if len(self.out[name])>1 else self.out[name][0]
	def c_var_neg(self,name):
		if len(self.out_neg[name])==1:
			return ('not', self.out_neg[name][0])
		else:
			return ('not', ('or',[self.out_neg[name]]))
	def conditions_var(self,name):
		return ('and', [self.c_var(name), self.c_var_neg(name)]) if name in self.out_neg else self.c_var(name)
	@property
	def conditions(self):
		return {name: self.conditions_var(name) for name in self.out}

	def compile(self,groups={}):
		[self.Add(t[0],t[1]) for t in self.v];
		[self.AddGroup(g,groups) for g in self.g];
		[self.AddNeg(t[0],t[1]) for t in self.neg_v];
		[self.AddGroupNeg(g,groups) for g in self.neg_g];
		[self.RemoveIte(name,conds) for name,conds in self.out_neg.items()];
		self.clean_out()
		return self

	def clean_out(self):
		[self.out.__delitem__(k) for k,v in list(self.out.items()) if not v];
		[self.out_neg.__delitem__(k) for k,v in list(self.out_neg.items()) if not v];

	def AddGroup(self,g,groups):
		[self.AddIte(k,v) for k,v in groups[g].out.items()];
		[self.AddIteNeg(k,v) for k,v in groups[g].out_neg.items()];

	def AddGroupNeg(self,g,groups):
		c = groups[g].conditions
		[self.cond_or_out(groups[g],c,name) for name in groups[g].out];

	def cond_or_out(self,g,c,name):
		if name in g.out_neg:
			self.AddIteNeg(name,c[name])
		else: 
			self.AddIteNeg(name,g.out[name])

	def Add(self,name,cond):
		if name not in self.out:
			self.out[name] = [cond]
		elif cond not in self.out[name]:
			self.out[name] += [cond]

	def AddNeg(self,name,cond):
		if name not in self.out_neg:
			self.out_neg[name] = [cond]
		elif cond not in self.out_neg[name]:
			self.out_neg[name] += [cond]

	def AddIte(self,name,conds):
		""" For the variable 'name', add all conditions 'conds' to self.out """
		if name not in self.out:
			self.out[name] = conds
		else:
			self.out[name] += [c for c in conds if c not in self.out[name]]

	def AddIteNeg(self,name,conds):
		if name not in self.out_neg:
			self.out_neg[name] = conds
		else:
			self.out_neg[name] += [c for c in conds if c not in self.out_neg[name]]

	def RemoveIte(self,name,conds):
		""" For the variable 'name', remove all conditions 'conds' from self.out """
		if name in self.out:
			condition_overlap = [c for c in conds if c in self.out[name]]
			self.out[name] = [c for c in self.out[name] if c not in condition_overlap]
			self.out_neg[name] = [c for c in self.out_neg[name] if c not in condition_overlap]