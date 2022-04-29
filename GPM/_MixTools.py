def IfInt(x):
	try:
		int(x)
		return True
	except ValueError:
		return False

def return_version(x,dict_):
	if x not in dict_:
		return x
	elif (x+'_0') not in dict_:
		return x+'_0'
	else:
		maxInt = max([int(y.split('_')[-1]) for y in dict_ if (y.rsplit('_',1)[0]==x and IfInt(y.split('_')[-1]))])
		return x+'_'+str(maxInt+1)

def dictInit(key,df_val,kwargs):
	return kwargs[key] if key in kwargs else df_val

def NoneInit(x,FallBackVal):
	return FallBackVal if x is None else x

class OrdSet:
	def __init__(self,i=None):
		self.v = list(dict.fromkeys(NoneInit(i,[])))

	def __iter__(self):
		return iter(self.v)

	def __len__(self):
		return len(self.v)

	def __getitem__(self,item):
		return self.v[item]

	def __setitem__(self,item,value):
		self.v[item] = value

	def __add__(self,o):
		return OrdSet(self.v+list(o))

	def __sub__(self,o):
		return OrdSet([x for x in self.v if x not in o])

	def union(self,*args):
		return OrdSet(self.__add__([x for l in args for x in l]))

	def intersection(self,*args):
		return OrdSet([x for l in self.union(args) for x in l if x in self.v])

	def update(self,*args):
		self.v = self.union(*args).v

	def copy(self):
		return OrdSet(self.v.copy())