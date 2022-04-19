from _Database import gpy
from dreamtools.gamY import Precompiler
from _MixTools import OrdSet
import regex_gms

# Four main types of methods: 
#	0. Default options e.g. for options, root components, and gamY functions.
#	1. write_gpy: A method that writes gams-like text from gpy symbols.
# 	2. write_from_db: A method that declares and read in sets, parameters, variables by reading a database.
# 	3. 	Default components: methods for writing a number of standad components used in GmsModels.
# 		3.1. write_root: Root file.
#		3.2. write_functions: gamY functions and macros.
#		3.3. Declare gams symbols and groups.
#		3.4. Load group variables.
#		4.5. Declare gams blocks/models.
# 		3.6. Solve statements.
# 		3.7. Fix/Unfix gamY statements.

# -------------------------------------- 0: OrdSet -------------------------------------- #

default_user_functions = """
# User defined functions:
$FUNCTION load_level({group}, {gdx}):
  $offlisting
  $GROUP __load_group {group};
  $LOOP __load_group:
    parameter load_{name}{sets} "";
    load_{name}{sets}$({conditions}) = 0;
  $ENDLOOP
  execute_load {gdx} $LOOP __load_group: load_{name}={name}.l $ENDLOOP;
  $LOOP __load_group:
    {name}.l{sets}$({conditions}) = load_{name}{sets};
  $ENDLOOP
  $onlisting
$ENDFUNCTION
$FUNCTION load_fixed({group}, {gdx}):
  $offlisting
  $GROUP __load_group {group};
  $LOOP __load_group:
    parameter load_{name}{sets} "";
    load_{name}{sets}$({conditions}) = 0;
  $ENDLOOP
  execute_load {gdx} $LOOP __load_group: load_{name}={name}.l $ENDLOOP;
  $LOOP __load_group:
    {name}.fx{sets}$({conditions}) = load_{name}{sets};
  $ENDLOOP
  $onlisting
$ENDFUNCTION
"""

_GmsWriteFromDB = {'sets': ('sets','alias','sets_other','sets_load','par','par_load'),
					'declarevars': ('sets','alias','sets_other','sets_load','par','par_load','var'),
					'vars':  ('sets','alias','sets_other','sets_load','par','par_load','var','var_load')}
default_options_root = {'SYSOUT': 'OFF', 'SOLPRINT': 'OFF', 'LIMROW': '0', 'LIMCOL': '0', 'DECIMALS': '6'}


# -------------------------------------- 2 : write_gpy -------------------------------------- #


def write_gpy(s=None,c=None,alias={}, lag = {},l="",**kwargs):
	if s.type == 'set':
		return s.name+condition(c=c) if s.name not in alias else alias[s.name]+condition(c=c)
	elif s.type in ('subset','mapping'):
		return s.name+gmsdomains(s,alias=alias,lag=lag)+condition(c=c)
	elif s.type =='variable':
		return s.name+l+gmsdomains(s,alias=alias,lag=lag)+condition(c=c)
	elif s.type == 'scalar_variable':
		return s.name+l+condition(c=c)
	elif s.type == 'parameter':
		return s.name+gmsdomains(s,alias=alias,lag=lag)+condition(c=c)
	elif s.type == 'scalar_parameter':
		return s.name+condition(c=c)

def condition(c=None):
	return '' if c is None else f"$({point(c)})"

def point(vi):
	if isinstance(vi, gpy):
		return write_gpy(vi)
	elif isinstance(vi,dict):
		return write_gpy(**vi)
	elif isinstance(vi,tuple):
		return write_tuple(vi)
	elif isinstance(vi,str):
		return vi

def write_tuple(tup):
	if tup[0] == 'not':
		return f"( not ({point(tup[1])}))"
	else:
		return f"({f' {tup[0]} '.join([point(vi) for vi in tup[1]])})"

def gmsdomains(s,alias={},lag={}):
	return list2string([alias.get(item,item)+str(lag.get(item,'')) for item in s.domains])

def list2string(list_):
	return '[{x}]'.format(x=','.join(list_)) if list_ else ''



# -------------------------------------- 3 : Write_from_db -------------------------------------- #

def write_from_db(db,types=('sets','alias','sets_other','sets_load','par','par_load','var','var_load'),exceptions=OrdSet(),exceptions_load=OrdSet(),gdx=None,onmulti=True):
	alltypes = {'sets': write_sets(db,exceptions=exceptions), 'alias': write_aliased_sets(db,exceptions=exceptions),'sets_other': write_sets_other(db,exceptions=exceptions), 'sets_load': write_sets_load(db,gdx,onmulti=onmulti,exceptions_load=exceptions_load),
				'par': write_parameters(db,exceptions), 'par_load': write_parameters_load(db,gdx,onmulti=onmulti,exceptions_load=exceptions_load),
				'var': write_variables(db,exceptions), 'var_load': write_variables_load(db,gdx,onmulti=onmulti,exceptions_load=exceptions_load)}
	return {k:v for k,v in alltypes.items() if k in types}

def writeAux(start,end,itersym,joinby='\n\t'):
	return start+'\n\t'+joinby.join(itersym)+'\n'+end+'\n\n' if bool(itersym) else ''

def write_sets(db,exceptions=OrdSet()):
	return writeAux('sets',';',[write_gpy(s=db[s]) for s in (OrdSet(db.gettypes('set'))-OrdSet(db.get('alias_map2'))-exceptions)])

def write_aliased_sets(db,exceptions=OrdSet()):
	out_str = ''
	for k,v in db.alias_dict.items():
		if k not in exceptions:
			out_str += 'alias({x},{y});\n'.format(x=k, y=','.join(list(v)))
	return out_str+'\n'

def write_sets_other(db,exceptions=OrdSet()):
	return writeAux('sets',';',[write_gpy(s=db[s]) for s in (OrdSet(db.gettypes(('subset','mapping')))-exceptions)])

def write_sets_load(db,gdx,onmulti=True,exceptions_load=OrdSet()):
	itersym = ['$load '+s for s in (OrdSet(db.gettypes(['set']))-OrdSet(db.get('alias_map2'))-exceptions_load)]+['$load '+s for s in (OrdSet(db.gettypes(['subset','mapping']))-exceptions_load)];
	start = '$GDXIN '+gdx+'\n'+'$onMulti\n' if onmulti else '$GDXIN '+gdx+'\n'
	end   = '$GDXIN\n' +'$offMulti;' if onmulti else '$GDXIN;'
	return writeAux(start,end,itersym)

def write_parameters(db,exceptions=OrdSet()):
	return writeAux('parameters',';',[write_gpy(s=db[s]) for s in (OrdSet(db.gettypes(('scalar_parameter','parameter')))-exceptions)])

def write_parameters_load(db,gdx,onmulti=True,exceptions_load=OrdSet()):
	itersym = ['$load '+s for s in (OrdSet(db.gettypes(('scalar_parameter','parameter')))-exceptions_load)];
	start = '$GDXIN '+gdx+'\n'+'$onMulti\n' if onmulti else '$GDXIN '+gdx+'\n'
	end   = '$GDXIN\n' +'$offMulti;' if onmulti else '$GDXIN;'
	return writeAux(start,end,itersym)	

def write_variables(db,exceptions=OrdSet()):
	return writeAux('variables',';',[write_gpy(s=db[s]) for s in (OrdSet(db.gettypes(('scalar_variable','variable')))-exceptions)])

def write_variables_load(db,gdx,onmulti=True,exceptions_load=OrdSet()):
	itersym = ['$load '+s for s in (OrdSet(db.gettypes(('scalar_variable','variable')))-exceptions_load)];
	start = '$GDXIN '+gdx+'\n'+'$onMulti\n' if onmulti else '$GDXIN '+gdx+'\n'
	end   = '$GDXIN\n' +'$offMulti;' if onmulti else '$GDXIN;'
	return writeAux(start,end,itersym)

# -------------------------------------- 3: Default components -------------------------------------- #

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

# -------------------------------------- 3.1: Root -------------------------------------- #
def auxdict2equal(k,v):
	return k+'='+v

def write_root(**kwargs):
	return f"""$ONEOLCOM
$EOLCOM #
$SETLOCAL qmark ";
OPTION {', '.join([auxdict2equal(k,v) for k,v in (default_options_root | kwargs).items()])};
"""

# -------------------------------------- 3.2: Functions -------------------------------------- #

def args_functions(f=None):
	return default_user_functions if f is None else f

def write_functions(precompiler,macros,f=None):
	f = default_user_functions if f is None else f
	funcs = {k:v for k,v in regex_gms.functions_from_str(f).items() if k not in precompiler.user_functions}
	macrs = {k:v for k,v in regex_gms.macros_from_str(f).items() if k not in macros}
	return arg2string({'as_string': '\n'.join([v for v in list(funcs.values())+list(macrs.values())])},t=precompiler)

# -------------------------------------- 3.3: Declare -------------------------------------- #

def write_declare(db,gdx,from_db='vars',**kwargs):
	return ''.join(write_from_db(db,types= _GmsWriteFromDB[from_db],gdx=gdx,**kwargs).values())

def args_declare_groups(precompiler,declare):
	arg2string(declare,precompiler)
	return declare

def write_declare_groups(precompiler,declare_text='',from_db='vars'):
	if from_db in ('declarevars','vars'):
		arg2string(declare_text,precompiler)
		return ''
	else:
		return arg2string(declare_text,precompiler)

# -------------------------------------- 3.4: Load groups -------------------------------------- #

def write_load_groups(groups=None,g_endo=None,gdx=None,from_db='vars',precompiler=None):
	return '' if from_db in ('declarevars','vars') else arg2string(write_loadgroups_gamY(groups,g_endo=g_endo,gdx=gdx),precompiler)

def write_loadgroups_gamY(groups,g_endo=None,gdx=None):
	endo =  ''.join([write_loadgroup_gamY(group,gdx,level='level') for group in g_endo])
	return endo+''.join([write_loadgroup_gamY(group,gdx,level='fixed') for group in (OrdSet(groups.keys())-g_endo)])

def write_loadgroup_gamY(group,gdx,level='fixed'):
	if level=='fixed':
		out_str = '@load_fixed({group},%qmark%{gdx}");\n'.format(group=group,gdx=gdx)
	elif level=='level':
		out_str = '@load_level({group},%qmark%{gdx}");\n'.format(group=group,gdx=gdx)
	return out_str

# -------------------------------------- 3.5: Read and declare model -------------------------------------- #

def args_model(name,blocks):
	return f"$Model {name} {', '.join(blocks)};\n" if blocks else ""

def write_model(name,blocks,precompiler):
	return arg2string(args_model(name,blocks),precompiler)

# -------------------------------------- 3.6: Solve statement -------------------------------------- #

def write_solve(solve=None,name=None):
	return f"""solve {name} using CNS;""" if solve is None else solve

# -------------------------------------- 3.7: Fix/unfix statements -------------------------------------- #

def args_fix_gamY(g_exo):
	return f"$FIX {', '.join(g_exo)};\n" if g_exo else ''
def args_unfix_gamY(g_endo):
	return f"$UNFIX {', '.join(g_endo)};\n"

def write_fix_gamY(precompiler,g_exo):
	return arg2string(args_fix_gamY(g_exo),precompiler)

def write_unfix_gamY(precompiler,g_endo):
	return arg2string(args_unfix_gamY(g_endo),precompiler)
