# import ply
import ply.lex as lex
# Lista de errores
errors = []

# palabras reservadas
reserved_words = {
    'execute' : 'EXECUTE',
    'mkdisk' : 'MKDISK', # es por convencion 
    'rmdisk' : 'RMDISK',
    'fdisk' : 'FDISK',
    'mount' : 'MOUNT',
    'unmount' : 'UNMOUNT',
    'mkfs' : 'MKFS',
    'login' : 'LOGIN',
    'logout' : 'LOGOUT',
    'mkgrp' : 'MKGRP',
    'rmgrp' : 'RMGRP',
    'mkusr' : 'MKUSR',
    'rmusr' : 'RMUSR',
    'mkfile' : 'MKFILE',
    'cat' : 'CAT',
    # Comand
    'size': 'SIZE',
    'path': 'PATH',
    'unit': 'UNIT',
    'fit': 'FIT',
    'type': 'TYPE',
    'delete': 'DELETE',
    'add': 'ADD',
    'name': 'NAME',
    'id': 'ID_UNMOUNT',
    'fs': 'FS',
    'full': 'FULL',
    'user': 'USER',
    'pass': 'PASS',
    'grp': 'GRP',
    'r': 'R',
    'cont': 'CONT',
    'file': 'FILEN',
    #Valores
}

# Lista de tokens GLOBAL tokens es una palabra del analizador
tokens = [
    'FS_CADENA',
    'ENTERO',
    'FIT_CADENA',
    'UNIDAD_CADENA',
    'TYPE_CADENA',
    'CADENA',
    'ID',
    'IGUAL',
    'GUION'
] + list(reserved_words.values())


# Expresiones regulares para tokens simples
t_IGUAL = r'\=' 
t_GUION = r'\-'

def t_FS_CADENA(t):
    r'2fs|3fs'
    t.value = t.value.upper()
    return t

# Expresiones regulares con acciones de codigo 55 
# todo ingresa como un string  "55" int(55) 
def t_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

#  Cadena 
def t_CADENA(t):
    r'\"(.|\n)*?\"'
    t.value = t.value[1:-1] # remuevo las comillas
    return t

#Fit
def t_FIT_CADENA(t):
    r'BF|FF|WF'
    t.value = t.value.upper()
    return t

#Unidad K|M|B
def t_UNIDAD_CADENA(t):
    r'K|M|B'
    t.value = t.value.upper()
    return t

#Type
def t_TYPE_CADENA(t):
    r'P|E|L'
    t.value = t.value.upper()
    return t

#  ID mkdir -> ID mkdisk
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved_words.get(t.value.lower(), 'ID')
    return t

# New line
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

#  Caracteres ignorados
t_ignore = ' \t'

def t_error(t):
    errors.append(t.value[0])
    print(f'Caracter no reconocido: {t.value[0]} en la linea {t.lexer.lineno}')
    t.lexer.skip(1)

def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

lexer = lex.lex()