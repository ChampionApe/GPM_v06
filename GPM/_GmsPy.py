import os, gams, pickle
from copy import deepcopy
from _MixTools import OrdSet, dictInit, NoneInit
from GmsWrite import write_gpy
from dreamtools.gamY import Precompiler

def d2t(x):
	return list(x.items())[0]

def arg2string(x,t=None):
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
	def __init__(self,groups=None):
		self.declared = OrdSet()
		self.groups = NoneInit(groups,{})

	@property
	def groupsCopy(self):
		return {k: deepcopy(v) for k,v in self.groups.items()}

	def run(self):
		for g in self.groups.values():
			g.compile(self.groups)

	def metaGroup(self,db,gs='all'):
		if isinstance(gs,Group):
			return gs
		elif gs == 'all':
			metagroup = Group('metagroup',g=self.groups.keys())
			metagroup.compile(groups=self.groupsCopy)
			return metagroup
		else:
			metagroup = Group('metagroup',g=gs)
			metagroup.compile(groups=self.groupsCopy)
			return metagroup

	def declareGroupsText(self,db,gs='all'):
		metagroup = self.metaGroup(db,gs=gs)
		if bool(set(metagroup.conditions)-set(self.declared.v)):
			out = "Variables \n\t"+"\n\t".join([write_gpy(s=db[var])+"\t\""+db[var].text+"\"" for var in metagroup.conditions if var not in self.declared])+"\n;"
			self.declared += OrdSet(metagroup.conditions)
			return out
		else:
			return ""

	def declareGroupText(self,db,g):
		return "\n".join([f"{g.gtype} {write_gpy(db[var])};" for var in g.conditions if var not in self.declared])

	def fixGroupsText(self,db,gs):
		metagroup = self.metaGroup(db,gs=gs)
		return self.fixGroupText(db,metagroup)

	def fixGroupText(self,db,g):
		return "\n".join([f"{write_gpy(db[k],c=v,l='.fx')} = {write_gpy(db[k],l='.l')};" for k,v in g.conditions.items()])

	def unfixGroupsText(self,db,gs):
		metagroup = self.metaGroup(db,gs=gs)
		return self.unfixGroupText(db,metagroup)

	def unfixGroupText(self,db,g):
		return "\n".join([f"{write_gpy(db[k],c=v,l='.lo')} = -inf;\n{write_gpy(db[k],c=v,l='.up')} = inf;" for k,v in g.conditions.items()])

class Group:
	def __init__(self,name,v=None,g=None,neg_v=None,neg_g=None,out=None,out_neg=None,gtype='variable'):
		self.name = name
		self.v = NoneInit(v,[])
		self.g = OrdSet(NoneInit(g,[]))
		self.neg_v = NoneInit(neg_v,[])
		self.neg_g = OrdSet(NoneInit(neg_g,[]))
		self.out = NoneInit(out,{})
		self.out_neg = NoneInit(out_neg,{})
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

	def compile(self,groups=None):
		groups = NoneInit(groups,{})
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
		[self.AddIte(k,[v]) for k,v in groups[g].conditions.items()];

	def AddGroup_ItemForItem(self,g,groups):
		[self.AddIte(k,v) for k,v in groups[g].out.items()];
		[self.AddIteNeg(k,v) for k,v in groups[g].out_neg.items()];

	def AddGroupNeg(self,g,groups):
		c = groups[g].conditions
		[self.cond_or_out(groups[g],c,name) for name in c];

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