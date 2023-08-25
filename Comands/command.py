from datetime import datetime
import random 
import struct
import os
def command_mkdisk(file, size, unit, fit):
    if unit == 'K':
        total_size = 1024 * size
    elif unit == 'M':
        total_size = 1024 * 1024 * size
    else:
        print("Error: Unidad no válida")
        return
    
    directory = os.path.dirname(file)

    if not os.path.exists(directory):
        os.makedirs(directory)

    if size > 0:
        with open(file, 'wb') as fe:
            id = random.randint(1, 1000000) 
            fecha = datetime.now() 
            data = struct.pack('QI', int(fecha.timestamp()), id)
            fe.write(data + b'\x00' * (total_size - len(data))) 
    else: 
        print("Error: El tamaño debe ser mayor a 0")
    print("Se ha creado el disco en la ruta: ", file, "con el tamaño de: ", size, "con la unidad: ", unit)

def command_fdisk(file, size, particion,unit):
    if unit == 'B':
        total_size = size
    elif unit == 'K':
        total_size = 1024 * size
    elif unit == 'M':
        total_size = 1024 * 1024 * size
    else:
        print("Error: Unidad no válida")
        return
    
    if size > 0:
        print("Se ha creado la particion en la ruta: ", file, "con el tamaño de: ", size, "con el nombre: ", particion, "con la unidad: ", unit)
    else: 
        print("Error: El tamaño debe ser mayor a 0")

def command_rep():
    print("MBR | Particion1 | Particion2 | Particion3 | Particion4")