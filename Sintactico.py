import ply.yacc as yacc
from lexer import *
from Comands.command import *

precedence = ()


def p_init(t):
    'init : list_commands'
    t[0] = t[1]


# gramatica
def p_list_commands(t):
    '''list_commands : list_commands commands
                    | commands'''
    if len(t) != 2:
        t[1].append(t[2])
        t[0] = t[1]
    else:
        t[0] = [t[1]]
    
def p_commands(t):
    '''commands : command_execute 
                | command_mkdisk
                | command_rmdisk
                | command_fdisk
                | command_mount
                | command_unmount
                | command_mkfs
                | command_login
                | command_logout
                | command_mkgrp
                | command_rmgrp
                | command_mkusr
                | command_rmusr
                | command_mkfile
                | command_cat'''
    t[0] = t[1]

def p_command_execute(t):
    '''command_execute : EXECUTE GUION PATH IGUAL CADENA'''
    print(t[1],t[5])
    t[0] = t[1]

def p_command_mkdisk(t):
    '''command_mkdisk : MKDISK parameters_mkdisk'''
    var_size, var_path, var_unit, var_fit = None, None, None, None
    for dict in t[2]:
        if 'size' in dict:
            var_size = dict['size']
        elif 'path' in dict:
            var_path = dict['path']
        elif 'unit' in dict:
            var_unit = dict['unit']
        elif 'fitcad' in dict:
            var_fit = dict['fitcad']

    var_unit = var_unit if var_unit != None else 'M'
    var_fit = var_fit if var_fit != None else 'FF'
    Disk.command_mkdisk(var_size, var_path, var_unit, var_fit)
    t[0] = t[1]
    
def p_parameters_mkdisk(t):
    '''parameters_mkdisk : parameters_mkdisk parameter_mkdisk
                        | parameter_mkdisk'''
    if len(t) == 3:
        t[0] = t[1]+ [t[2]]
    else:
        t[0] = [t[1]]

def p_parameter_mkdisk(t):
    '''parameter_mkdisk : param_size
                | param_path
                | param_unit
                | param_fit'''
    t[0] = t[1]

def p_param_size(t):
    'param_size : GUION SIZE IGUAL ENTERO'
    t[0] = {'size' : t[4] }

def p_param_path(t):
    'param_path : GUION PATH IGUAL CADENA'
    t[0] = {'path' : t[4] }

def p_param_unit(t):
    'param_unit : GUION UNIT IGUAL UNIDAD_CADENA'
    t[0] = {'unit' : t[4] }

def p_param_fit(t):
    'param_fit : GUION FIT IGUAL FIT_CADENA'
    t[0] = {'fitcad' : t[4] }

def p_command_rmdisk(t):
    '''command_rmdisk : RMDISK GUION PATH IGUAL CADENA'''
    Disk.command_rmdisk(t[5])
    t[0] = t[1]

def p_command_fdisk(t):
    '''command_fdisk : FDISK parameters_fdisk'''
    var_size, var_path, var_unit, var_fit,var_type,var_delete,var_add,var_name = None, None, None, None, None, None, None, None
    for dict in t[2]:
        if 'size' in dict:
            var_size = dict['size']
        elif 'path' in dict:
            var_path = dict['path']
        elif 'unit' in dict:
            var_unit = dict['unit']
        elif 'fitcad' in dict:
            var_fit = dict['fitcad']
        elif 'type' in dict:
            var_type = dict['type']
        elif 'delete' in dict:
            var_delete = dict['delete']
        elif 'add' in dict:
            var_add = dict['add']
        elif 'name' in dict:
            var_name = dict['name']

    var_unit = var_unit if var_unit != None else 'K'
    var_type = var_type if var_type != None else 'P'
    var_fit = var_fit if var_fit != None else 'WF'
    if (var_delete == None & var_add == None):
        print(var_size, var_path, var_unit, var_fit,var_type,var_delete,var_add,var_name)
        #Disk.command_fdisk(var_size, var_path, var_unit, var_fit,var_type,var_delete,var_add,var_name)
    elif (var_delete is not None and var_add is None):
        print("delete")
    elif (var_delete is None and var_add is not None):
        print("add")
    t[0] = t[1]

def p_parameters_fdisk(t):
    '''parameters_fdisk : parameters_fdisk parameter_fdisk
                        | parameter_fdisk'''
    if len(t) == 3:
        t[0] = t[1]+ [t[2]]
    else:
        t[0] = [t[1]]

def p_parameter_fdisk(t):
    '''parameter_fdisk : param_size
                | param_path
                | param_unit
                | param_fit
                | param_type
                | param_delete
                | param_name
                | param_add'''
    t[0] = t[1]

def p_param_type(t):
    '''param_type : GUION TYPE IGUAL TYPE_CADENA
                    | GUION TYPE IGUAL FULL'''
    t[0] = {'type' : t[4] }

def p_param_delete(t):
    'param_delete : GUION DELETE IGUAL FULL'
    t[0] = {'delete' : t[4] }

def p_param_add(t):
    'param_add : GUION ADD IGUAL ENTERO'
    t[0] = {'add' : t[4] }

def p_param_name(t):
    'param_name : GUION NAME IGUAL CADENA'
    t[0] = {'name' : t[4] }

def p_command_mount(t):
    '''command_mount : MOUNT parameters_mount'''
    var_path, var_name = None, None
    for dict in t[2]:
        if 'path' in dict:
            var_path = dict['path']
        elif 'name' in dict:
            var_name = dict['name']
    print(var_path, var_name)
    t[0] = t[1]

def p_parameters_mount(t):
    '''parameters_mount : parameters_mount parameter_mount
                        | parameter_mount'''
    if len(t) == 3:
        t[0] = t[1]+ [t[2]]
    else:
        t[0] = [t[1]]

def p_parameter_mount(t):
    '''parameter_mount : param_path
                    | param_name'''
    t[0] = t[1]

def p_command_unmount(t):
    '''command_unmount : UNMOUNT GUION ID_UNMOUNT IGUAL CADENA'''
    print(t[5])
    t[0] = t[1]

def p_command_mkfs(t):
    '''command_mkfs : MKFS parameters_mkfs'''
    var_id, var_type,var_fs = None, None, None
    for dict in t[2]:
        if 'id' in dict:
            var_id = dict['id']
        elif 'type' in dict:
            var_type = dict['type']
        elif 'fs' in dict:
            var_fs = dict['fs']

    
    print(var_id, var_type,var_fs)
    t[0] = t[1]

def p_parameters_mkfs(t):
    '''parameters_mkfs : parameters_mkfs parameter_mkfs
                        | parameter_mkfs'''
    if len(t) == 3:
        t[0] = t[1]+ [t[2]]
    else:
        t[0] = [t[1]]

def p_parameter_mkfs(t):
    '''parameter_mkfs : param_id
                    | param_type
                    | param_fs'''
    t[0] = t[1]

def p_param_id(t):
    'param_id : GUION ID_UNMOUNT IGUAL CADENA'
    t[0] = {'id' : t[4] }

def p_param_fs(t):
    'param_fs : GUION FS IGUAL FS_CADENA'
    t[0] = {'fs' : t[4] }
    
def p_command_login(t):
    '''command_login : LOGIN parameters_login'''
    var_user, var_pass, var_id = None, None, None
    for dict in t[2]:
        if 'user' in dict:
            var_user = dict['user']
        elif 'pass' in dict:
            var_pass = dict['pass']
        elif 'id' in dict:
            var_id = dict['id']

    print(var_user, var_pass, var_id)
    t[0] = t[1]

def p_parameters_login(t):
    '''parameters_login : parameters_login parameter_login
                        | parameter_login'''
    if len(t) == 3:
        t[0] = t[1]+ [t[2]]
    else:
        t[0] = [t[1]]

def p_parameter_login(t):
    '''parameter_login : param_user
                    | param_pass
                    | param_id'''
    t[0] = t[1]

def p_param_user(t):
    'param_user : GUION USER IGUAL CADENA'
    t[0] = {'user' : t[4] }

def p_param_pass(t):
    'param_pass : GUION PASS IGUAL CADENA'
    t[0] = {'pass' : t[4] }

def p_command_logout(t):
    '''command_logout : LOGOUT'''
    print(t[1])
    t[0] = t[1]

def p_command_mkgrp(t):
    'command_mkgrp : MKGRP GUION NAME IGUAL CADENA'
    print(t[5])
    t[0] = t[1]

def p_command_rmgrp(t):
    'command_rmgrp : RMGRP GUION NAME IGUAL CADENA'
    print(t[5])
    t[0] = t[1]

def p_command_mkusr(t):
    '''command_mkusr : MKUSR parameters_mkusr'''
    var_user, var_pass, var_grp = None, None, None
    for dict in t[2]:
        if 'user' in dict:
            var_user = dict['user']
        elif 'pass' in dict:
            var_pass = dict['pass']
        elif 'grp' in dict:
            var_grp = dict['grp']

    print(var_user, var_pass, var_grp)
    t[0] = t[1]

def p_parameters_mkusr(t):
    '''parameters_mkusr : parameters_mkusr parameter_mkusr
                        | parameter_mkusr'''
    if len(t) == 3:
        t[0] = t[1]+ [t[2]]
    else:
        t[0] = [t[1]]

def p_parameter_mkusr(t):
    '''parameter_mkusr : param_user
                    | param_pass
                    | param_grp'''
    t[0] = t[1]

def p_param_grp(t):
    'param_grp : GUION GRP IGUAL CADENA'
    t[0] = {'grp' : t[4] }

def p_command_rmusr(t):
    '''command_rmusr : RMUSR GUION USER IGUAL CADENA'''
    print(t[5])
    t[0] = t[1]

def p_command_mkfile(t):
    '''command_mkfile : MKFILE parameters_mkfile'''
    var_path, var_r, var_size, var_cont = None, None, None, None
    for dict in t[2]:
        if 'path' in dict:
            var_path = dict['path']
        elif 'p' in dict:
            var_r = dict['r']
        elif 'size' in dict:
            var_size = dict['size']
        elif 'cont' in dict:
            var_cont = dict['cont']

    print(var_path, var_r, var_size, var_cont)
    t[0] = t[1]

def p_parameters_mkfile(t):
    '''parameters_mkfile : parameters_mkfile parameter_mkfile
                        | parameter_mkfile'''
    if len(t) == 3:
        t[0] = t[1]+ [t[2]]
    else:
        t[0] = [t[1]]

def p_parameter_mkfile(t):
    '''parameter_mkfile : param_path
                    | param_r
                    | param_size
                    | param_cont'''
    t[0] = t[1]

def p_param_r(t):
    'param_r : GUION R'
    t[0] = {'r' : True }

def p_param_cont(t):
    'param_cont : GUION CONT IGUAL CADENA'
    t[0] = {'cont' : t[4] }

def p_command_cat(t):
    '''command_cat : CAT parameters_cat'''
    var_file = None
    for dict in t[2]:
        if 'file' in dict:
            var_file = dict['file']

    print(var_file)
    t[0] = t[1]

def p_parameters_cat(t):
    '''parameters_cat : parameters_cat parameter_cat
                        | parameter_cat'''
    if len(t) == 3:
        t[0] = t[1]+ [t[2]]
    else:
        t[0] = [t[1]]

def p_parameter_cat(t):
    '''parameter_cat : param_file'''
    t[0] = t[1]

def p_param_file(t):
    'param_file : GUION FILEN ENTERO IGUAL CADENA'
    t[0] = {'file' : t[5] }

# llevarla al main
def parse(input):
    global errores
    global parser
    parser = yacc.yacc()
    lexer.lineno = 1
    return parser.parse(input)
