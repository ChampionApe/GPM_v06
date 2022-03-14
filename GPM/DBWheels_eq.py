import pandas as pd, Database
from Database import gpy
from DBWheels_rc import rc_pd, rc_pdInd, rc_AdjGpy


def initindex_fromproduct(domains,db):
	if len(domains)>1:
		return pd.MultiIndex.from_product([db.get(s) for s in domains])
	else:
		return db.get(domains[0])


# Methods for working symbols defined over multiindex
class gpy_eq:
	def __init__(self,symbol=None,name=None,db=None,**kwargs):
		if isinstance(symbol,(gpy_eq,dict)):
			[setattr(self,key,value) for key,value in symbol.items() if key not in kwargs];
			[setattr(self,key,value) for key,value in kwargs.items()]
		else:
			self.name = name 
			self.type = Database.kw_df(kwargs,'type','e')
			self.text = Database.kw_df(kwargs,'text','')
			self.c = Database.kw_df(kwargs,'c',None)
			self.F = Database.kw_df(kwargs,'F',None)
			if ('domains' in kwargs) and kwargs['domains']:
				index = rc_pd(s = initindex_fromproduct(kwargs['domains'],db), c= self.c)
				self.diff = gpy(pd.Series(1, index = index, name = f"diff_{self.name}"))
			elif ('index' in kwargs) and kwargs['index']:
				self.diff = gpy(pd.Series(1, index = index, name = f"diff_{self.name}"))
			else:
				self.diff = gpy(1, **{'name': f"diff_{self.name}"})
	@property
	def vals(self):
		return self.diff.vals

	@property
	def index(self):
		if isinstance(self.vals, pd.Series):
			return self.vals.index
		else:
			return None
	@property
	def domains(self):
		return [] if self.index is None else self.index.names
	def __iter__(self):
		return iter(self.vals)
	def __len__(self):
		return len(self.vals)
	def items(self):
		return self.__dict__.items()

def broadcast(vlist, d=None, c = None, db = None, index=None, bc='sparse',bc_scalar=False):
	if bc == 'sparse':
		return broadcast_dul(vlist,d=d,c=c,db=db,index=index,bc_scalar=bc_scalar)
	elif bc == 'full':
		return broadcast_full(vlist,index=index,bc_scalar=bc_scalar)

def broadcast_dul(vlist,d=None,c=None,db=None,index=None,bc_scalar=False):
	if (not domains_vlist(vlist)) or (d is None):
		return [getvalues(vi) for vi in vlist] # assumes scalars if no domains
	else:
		sd = sparsedomain(vlist,d=d,c=c,db=db) if check_ul(d,vlist) else pd.Series(0,index=index)
		return [broadcast_vi(vi,sd,[x for x in d if x in sd.index.names]) for vi in vlist] if bc_scalar else [broadcast_vi_scalartest(vi,sd,[x for x in d if x in sd.index.names]) for vi in vlist]

def broadcast_full(vlist,index=None,bc_scalar=False):
	if index is None:
		return [getvalues(vi) for vi in vlist]
	else:
		sd = pd.Series(0, index = index)
		if vlist:
			return [broadcast_vi(vi,sd,index.names) for vi in vlist] if bc_scalar else [broadcast_vi_scalartest(vi,sd,index.names) for vi in vlist]
		else:
			return sd

def broadcast_vi(v,dom,names):
	return (dom+getvalues(v)).dropna().reorder_levels(names)

def broadcast_vi_scalartest(v,dom,names):
	return getvalues(v) if isscalar(v) else (dom+getvalues(v)).dropna().reorder_levels(names)

def sparsedomain(vlist, d=None, c=None, db = None):
	return pd.Series(0, index = rc_pdInd(initindex_fromproduct(domains_vlist(vlist),db), c))

def check_ul(domains, vlist):
	""" Returns true if there is an unused level in vlist compared to eq.domains """
	return bool(set(domains)-domains_vlist(vlist))

def domains_vlist(vlist):
	return set().union(*[set(getdomains(vi)) for vi in vlist])

def isscalar(sym):
	return not Database.is_iterable(sym) or (isinstance(sym,(gpy,Database.gpy)) and (sym.type in ('scalar_variable','scalar_parameter')))

def getdomains(sym):
	if isinstance(sym,(gpy, gpy_eq, Database.gpy)):
		return sym.domains
	elif isinstance(sym,(pd.Series,pd.DataFrame)):
		return sym.index.names
	elif isinstance(sym,pd.Index):
		return sym.names
def getvalues(sym):
	if isinstance(sym, (gpy, Database.gpy)):
		return sym.vals
	else:
		return sym

