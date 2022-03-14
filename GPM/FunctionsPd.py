from _Equations import *

def fPointer(v,**kwargs):
	if isinstance(v,tuple):
		return v[0](v[1],**kwargs)
	elif isinstance(v, dict):
		return rc_pd(v)
	elif isinstance(v, (rctree_scalar_types,rctree_admissable_types)):
		return v

def adjustsparsedomains(v, bctype='infer',index = None, CheckDomains = False, **kwargs):
	if bctype != 'full':
		if CheckDomains or ((not isinstance(v, rctree_scalar_types)) and not (index.names == v.index.names)):
			return broadcast([v], **(kwargs | {'bctype':'full'}))
	else:
		return v

def fSum(args,bctype='infer',**kwargs):
	if not args:
		return broadcast(args, **(kwargs | {'bctype':'full'}))
	elif len(args)==1:
		return broadcast([fPointer(v,**kwargs) for v in args], **(kwargs | {'bctype':'full'}))[0]
	else:
		nd,oned,dom = broadcast2np([fPointer(v,**kwargs) for v in args],**kwargs)
		return adjustsparsedomains(pd.Series(nd.sum(axis=1)+oned.sum(),index=dom) if dom else oned.sum(),**kwargs)
