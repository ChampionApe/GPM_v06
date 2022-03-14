from _Equations import *

# @jit
# def index_np_scalar(nd,oned,index,i):
# 	return nd[:,index[i,1]] if index[i,0]==0 else oned[index[i,1]]

def fSum(args, outer_scope = None, gb = None, bc = 'sparse', bc_scalar=False,jit=True):
	if not args:
		return broadcast(args,**outer_scope,bc='full')
	elif len(args)==1:
		return broadcast(args,**outer_scope,bc='full')
	else:
		nd,oned,dom,_ = broadcast2np(args,**outer_scope,bc=bc,bc_scalar=bc_scalar)
		return pd.Series(nd.sum(axis=1)+oned.sum(), index = dom),dom
