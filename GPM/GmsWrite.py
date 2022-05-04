from _GmsWrite import *
from DBWheels_mi import gridDB

def standardArgs(settings, db, gdx, blocks = None, functions = None, run = True, prefix = '', prefix_run = '', options = None):
	""" Returns the 'standard' components. Use GmsPy.Groups to handle grouping of variables. """
	args = {'root': write_root(**NoneInit(options,{})), prefix+'functions': args_functions(f=functions), prefix+'declare': write_declare(db, gdx, from_db=settings.from_db), 
			prefix+'blocks': blocks}
	args = {k:v for k,v in args.items() if v}
	return args | standardRun(settings,db,prefix=prefix_run) if run else args

def standardArgs_gamY(settings,db,gdx, blocks = None, functions = None, declare_groups = '', run = True, prefix = '', prefix_run='', options=None):
	args = {'root': write_root(**NoneInit(options,{})), prefix+'functions': args_functions(f=functions), prefix+'declare': write_declare(db, gdx, from_db='sets'), 
			prefix+'declare_groups': args_declare_groups(settings.Precompiler,declare_groups), prefix+'load_groups': write_loadgroups_gamY(settings.Precompiler.groups,g_endo=settings['g_endo'],gdx=gdx),
			prefix+'blocks': blocks}
	args = {k:v for k,v in args.items() if v}
	return args | standardRun_gamY(settings,prefix=prefix_run) if run else args

def standardRun(settings,db,prefix=''):
	return {prefix+'fix': settings.Compile.fixGroupsText(db,settings['g_exo']), prefix+'unfix': settings.Compile.unfixGroupsText(db,settings['g_endo']), 
			prefix+'model': args_model(settings['name'], settings['blocks']), prefix+'solve': write_solve(solve=settings['solve'],name=settings['name'])}

def standardRun_gamY(settings,prefix=''):
	return {prefix+'fix': args_fix_gamY(settings['g_exo']), prefix+'unfix': args_unfix_gamY(settings['g_endo']), 
			prefix+'model': args_model(settings['name'], settings['blocks']), prefix+'solve': write_solve(solve=settings['solve'],name=settings['name'])}

def SolveLoop(settings, dbT, name ='shock', db0 = None, subsetDB = True, extractSol = None, loop = 'l1', solve=None, model=None, **kwargs):
	if subsetDB:
		db = settings.partition_db(db=targetDB)
		targetDB.series.database = (db['non_var'] | db['var_exo'])
	db0 = settings.db if db is None else db0
	shock_db = gridDB(db0,dbT,name,extractSol=extractSol,loop=loop,**kwargs)
	updateDict = {k: shock_db[k+'_'+name+'_ss'] for k in dbT.gettypes(('variable','scalar_variable'))}
	updateSolDict = {'_'.join(['sol',k,shock]): v for k,v in NoneInit(extractSol,{}).items()}
	text = declareAndLoop(write_gpy(shock_db[loop]), name, db0, shock_db, updateDict = updateDict, updateSolDict=updateSolDict, solve=NoneInit(solve,settings['solve']), model = NoneInit(model, settings['name']))
	return text, shock_db