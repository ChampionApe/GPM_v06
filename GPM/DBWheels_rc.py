import pandas as pd
from _Database import gpy

rctree_admissable_types = (gpy,pd.Index, pd.Series, pd.DataFrame)
def tryint(x):
    try:
        return int(x)
    except ValueError:
        return x

def rc_AdjGpy(s, c = None, alias = {}, lag = {}, pm = False, **kwargs):
	if c:
		copy = s.copy()
		copy.vals = rctree_pd(s=s,c=c,alias=alias,lag=lag,pm=pm)
		return copy
	else:
		return AdjGpy(s,alias=alias, lag = lag)

def AdjGpy(symbol, alias = {}, lag = {}):
	copy = symbol.copy()
	copy.vals = rc_AdjPd(symbol.vals, alias=alias, lag = lag)
	return copy

def rc_AdjPd(symbol, alias = {}, lag = {}):
	if isinstance(symbol, pd.Index):
		return AdjAliasInd(AdjLagInd(symbol, lag=lag), alias = alias)
	elif isinstance(symbol, pd.Series):
		return symbol.to_frame().set_index(AdjAliasInd(AdjLagInd(symbol.index, lag=lag), alias=alias),verify_integrity=False).iloc[:,0]
	elif isinstance(symbol, pd.DataFrame):
		return symbol.set_index(AdjAliasInd(AdjLagInd(symbol.index, lag=lag), alias=alias),verify_integrity=False)
	elif isinstance(symbol,gpy):
		return rc_AdjPd(symbol.vals, alias = alias, lag = lag)
	else:
		raise TypeError(f"rc_AdjPd only uses instances {rctree_admissable_types} (and no scalars). Input was type {type(symbol)}")

def AdjLagInd(index_,lag={}):
	if lag:
		if isinstance(index_,pd.MultiIndex):
			return index_.set_levels([index_.levels[index_.names.index(k)]+tryint(v) for k,v in lag.items()], level=lag.keys())
		elif list(index_.domains)==list(lag.keys()):
			return index_+list(lag.values())[0]
	else:
		return index_

def AdjAliasInd(index_,alias={}):
	return index_.set_names([x if x not in alias.keys() else alias[x] for x in index_.names])

# Subsetting methods:
def rctree_pd(s=None,c=None,alias={},lag ={},pm = False, **kwargs):
	adj = rc_AdjPd(s,alias=alias,lag=lag)
	if not pm:
		return getvalues(adj)[point(getindex(adj) ,c)]
	else:
		return getvalues(adj)[point_pm(getindex(adj), c)]

def point_pm(pdObj,vi):
	if isinstance(vi,rctree_admissable_types):
		return bool_ss_pm(pdObj,getindex(vi))
	elif isinstance(vi,dict):
		return bool_ss_pm(pdObj,getindex(rctree_pd(**vi)))
	elif isinstance(vi,tuple):
		return rctree_tuple_pm(pdObj,vi)
	elif vi is None:
		return pdObj == pdObj

def point(pdObj, vi):
	if isinstance(vi, rctree_admissable_types):
		return bool_ss(pdObj,getindex(vi))
	elif isinstance(vi,dict):
		return bool_ss(pdObj,getindex(rctree_pd(**vi)))
	elif isinstance(vi,tuple):
		return rctree_tuple(pdObj,vi)
	elif vi is None:
		return pdObj == pdObj

def rctree_tuple(pdObj,tup):
	if tup[0]=='not':
		return translate_k2pd(point(pdObj,tup[1]),tup[0])
	else:
		return translate_k2pd([point(pdObj,vi) for vi in tup[1]],tup[0])

def rctree_tuple_pm(pdObj,tup):
	if tup[0]=='not':
		return translate_k2pd(point_pm(pdObj,tup[1],tup[0]))
	else:
		return translate_k2pd([point_pm(pdObj,vi) for vi in tup[1]],tup[0])

def bool_ss(pdObjIndex,ssIndex):
	o,d = overlap_drop(pdObjIndex,ssIndex)
	return pdObjIndex.isin([]) if not o else pdObjIndex.droplevel(d).isin(reorder(ssIndex,o))

def bool_ss_pm(pdObjIndex,ssIndex):
	o = overlap_pm(pdObjIndex, ssIndex)
	if o:
		return pdObjIndex.droplevel([x for x in pdObjIndex.names if x not in o]).isin(reorder(ssIndex.droplevel([x for x in ssIndex.names if x not in o]),o))
	else:
		return pdObjIndex.isin([])

def overlap_drop(pdObjIndex,index_):
	return [x for x in pdObjIndex.names if x in index_.names],[x for x in pdObjIndex.names if x not in index_.names]

def overlap_pm(pdObjIndex,index_):
	return [x for x in pdObjIndex.names if x in index_.names]

def reorder(index_,o):
	return index_ if len(o)==1 else index_.reorder_levels(o)

def getindex(pdObj):
	if isinstance(pdObj,(gpy,pd.Series,pd.DataFrame)):
		return pdObj.index
	elif isinstance(pdObj, pd.Index):
		return pdObj

def getvalues(symbol):
	if isinstance(symbol, gpy):
		return symbol.vals
	elif isinstance(symbol,(pd.Series,pd.DataFrame,pd.Index)):
		return symbol

def translate_k2pd(l,k):
	if k == 'and':
		return sum(l)==len(l)
	elif k == 'or':
		return sum(l)>0
	elif k == 'not' and isinstance(l,(list,set)):
		return ~l[0]
	elif k == 'not':
		return ~l
