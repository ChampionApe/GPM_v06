import pandas as pd, numpy as np, Database
from Database import gpy
from DBWheels_rc import rc_pd, rc_pdInd, rc_AdjGpy, rctree_admissable_types, rctree_scalar_types

def initindex_fromproduct(domains,db):
	if len(domains)>1:
		return pd.MultiIndex.from_product([db.get(s) for s in domains])
	else:
		return db.get(domains[0])

def IndexNpScalar(v):
	return (pd.Series(1, index = pd.Index([1 if isscalar(vi) else 0 for vi in v],name='l')).groupby('l').cumsum()-1).reset_index().values

def broadcast2np(vlist, c = None, db = None, index = None, bctype = 'infer', bc_scalar = False, sort = False, **kwargs):
	v,dom = broadcast_windex(vlist, c= c, db = db, index = index, bctype = bctype, bc_scalar=bc_scalar, sort = sort, **kwargs)
	return np.array([vi for vi in v if not isscalar(vi)]).T, np.array([vi for vi in v if isscalar(vi)]), dom

def broadcast(vlist, c= None, db = None, index = None, bctype = 'infer', bc_scalar=False, sort = False, **kwargs):
	if bctype == 'infer':
		return bc_inf_dom(vlist, c = c, db = db, bc_scalar = bc_scalar, sort=sort, **kwargs)
	elif bctype == 'sparse':
		return bc_sparse(vlist, c = c, db = db, index = index, bc_scalar = bc_scalar, sort = sort, **kwargs)
	elif bctype == 'full':
		return bc_full(vlist, index = index, bc_scalar = bc_scalar, sort = sort, **kwargs)

def broadcast_windex(vlist, c= None, db = None, index = None, bctype = 'infer', bc_scalar=False, sort = False, **kwargs):
	if bctype == 'infer':
		return bc_inf_dom_windex(vlist, c = c, db = db, bc_scalar = bc_scalar, sort=sort, **kwargs)
	elif bctype == 'sparse':
		return bc_sparse_windex(vlist, c = c, db = db, index = index, bc_scalar = bc_scalar, sort = sort, **kwargs)
	elif bctype == 'full':
		return bc_full(vlist, index = index, bc_scalar = bc_scalar, sort = sort, **kwargs),index

def bc_sparse_windex(vlist, c = None, db = None, index = None, bc_scalar=False,sort=False,**kwargs):
	if not (domains_vlist(vlist) or (index is None)):
		return [getvalues(vi) for vi in vlist],None
	else:
		sd = sparsedomain(vlist, c = c, db =db) if check_ul(index.names,vlist) else pd.Series(0, index = index)
		return bc_sort_sc(vlist, sd, bc_scalar,sort), sd.index

def bc_sparse(vlist, c = None, db = None, index = None, bc_scalar=False,sort=False,**kwargs):
	if not (domains_vlist(vlist) or (index is None)):
		return [getvalues(vi) for vi in vlist]
	else:
		sd = sparsedomain(vlist, c = c, db =db) if check_ul(index.names,vlist) else pd.Series(0, index = index)
		return bc_sort_sc(vlist, sd, bc_scalar,sort)

def bc_full(vlist, index = None, bc_scalar = False, sort = False, **kwargs):
	if index is None:
		return [getvalues(vi) for vi in vlist]
	else:
		sd = pd.Series(0, index = index)
		return bc_sort_sc(vlist,sd,bc_scalar,sort) if vlist else sd

def bc_inf_dom(vlist, c = None, db = None, bc_scalar = False, sort=False, **kwargs):
	if not domains_vlist(vlist):
		return [getvalues(vi) for vi in vlist]
	else:
		sd = sparsedomain(vlist, c = c, db = db)
		return bc_sort_sc(vlist,sd,bc_scalar,sort)

def bc_inf_dom_windex(vlist, c = None, db = None, bc_scalar = False, sort=False, **kwargs):
	if not domains_vlist(vlist):
		return [getvalues(vi) for vi in vlist],None
	else:
		sd = sparsedomain(vlist, c = c, db = db)
		return bc_sort_sc(vlist,sd,bc_scalar,sort),sd.index

def bc_sort_sc(vlist, sd, bc_scalar,sort):
	if bc_scalar:
		return [bc_from_dom_sort(vi,sd,sd.index.names) for vi in vlist] if sort else [bc_from_dom(vi,sd,sd.index.names) for vi in vlist]
	else:
		return [bc_from_dom_sort_sc(vi,sd,sd.index.names) for vi in vlist] if sort else [bc_from_dom_sc(vi,sd,sd.index.names) for vi in vlist]

def bc_from_dom_sc(v,dom,names):
	return getvalues(v) if isscalar(v) else bc_from_dom(v,dom,names)

def bc_from_dom_sort_sc(v,dom,names):
	return getvalues(v) if isscalar(v) else bc_from_dom_sort(v,dom,names)

def bc_from_dom(v,dom,names):
	return (dom+getvalues(v)).dropna().reorder_levels(names)

def bc_from_dom_sort(v,dom,names):
	return (dom+getvalues(v)).dropna().reorder_levels(names).sort_index()

def sparsedomain(vlist, c=None, db = None):
	return pd.Series(0, index = rc_pdInd(initindex_fromproduct(domains_vlist(vlist),db), c))

def check_ul(domains, vlist):
	""" Returns true if there is an unused level in vlist compared to eq.domains """
	return bool(set(domains)-domains_vlist(vlist))

def domains_vlist(vlist):
	return set().union(*[set(getdomains(vi)) for vi in vlist])

def isscalar(sym):
	return not Database.is_iterable(sym) or (isinstance(sym,(gpy,Database.gpy)) and (sym.type in ('scalar_variable','scalar_parameter')))

def getdomains(sym):
	if isinstance(sym,(gpy,Database.gpy)):
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

