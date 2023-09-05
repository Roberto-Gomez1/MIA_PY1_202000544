import random 
import os
import time
import Struct.Structs


class Disk:
    def __init__(self):
        pass

    def command_mkdisk(size, path, unit, fit):
        disco = Struct.Structs.MBR()
        try:
            if unit == 'K':
                total_size = 1024 * size
            elif unit == 'M':
                total_size = 1024 * 1024 * size
            else:
                print("Error: Unidad no válida")
                return
            if size <= 0:
                print("Error: El parámetro size del comando MKDISK debe ser mayor a 0")
                return

            fit = fit[0].upper()
            disco.mbr_tamano = total_size
            disco.mbr_fecha_creacion = int(time.time())
            disco.disk_fit = fit
            disco.mbr_disk_signature = random.randint(100, 9999)

            if os.path.exists(path):
                print("Error: Disco ya existente en la ruta: "+path)
                return

            folder_path = os.path.dirname(path)
            os.makedirs(folder_path, exist_ok=True)

            disco.mbr_Partition_1 = Struct.Structs.Particion()
            disco.mbr_Partition_2 = Struct.Structs.Particion()
            disco.mbr_Partition_3 = Struct.Structs.Particion()
            disco.mbr_Partition_4 = Struct.Structs.Particion()

            if path.startswith("\""):
                path = path[1:-1]

            if not path.endswith(".dsk"):
                print("Error: Extensión de archivo no válida para la creación del Disco.")
                return

            try:
                with open(path, "w+b") as file:
                    file.write(b"\x00")
                    file.seek(total_size - 1)
                    file.write(b"\x00")
                    file.seek(0)
                    file.write(bytes(disco))
                print(">>>> MKDISK: Disco creado exitosamente <<<<")
            except Exception as e:
                print(e)
                print("Error: Error al crear el disco en la ruta: "+path)
        except ValueError:
            print("Error: El parámetro size del comando MKDISK debe ser un número entero")

    def command_rmdisk(path):
        if path.startswith("\"") and path.endswith("\""):
            path = path[1:-1]
        try:
            if os.path.isfile(path):
                if not path.endswith(".dsk"):
                    print("ERROR: Extensión de archivo no válida para la eliminación del Disco.") 
                opcion = input("\t¿Está seguro que desea eliminar el disco? (S/N): ").lower()
                if opcion == "s":
                    os.remove(path)
                    print(">>>> RMDISK: Disco eliminado exitosamente <<<<")
                else:
                    print(">>>> RMDISK: Eliminación del disco cancelada correctamente <<<<") 
            else:
                print("El disco no existe en la ruta indicada.") 
        except Exception as e:
            print("Error al intentar eliminar el disco: "+str(e)) 


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

    '''def rep(tokens):
        path = ""
        if len(tokens) == 0 or len(tokens) > 1:
            print("\tERROR: Se requiere parametro Path para el comando RMDISK")
            return
        
        for token in tokens:
            tk, _, token = token.partition("=")
            if main.Scanner.comparar(tk, "path"):
                path = token
            else:
                path = ""
                print("\tERROR: Parametro \""+tk+"\" no esperado en el comando RMDISK") 
                return

        if path:
            if path.startswith("\"") and path.endswith("\""):
                path = path[1:-1]

        try: 
            mbr_format = "<iiiiB"
            mbr_size = struct.calcsize(mbr_format)
            with open(path, "rb") as file:
                mbr_data = file.read(mbr_size)
                mbr = Structs.MBR()
                (mbr.mbr_tamano, mbr.mbr_fecha_creacion, mbr.mbr_disk_signature, disk_fit, *_) = struct.unpack(mbr_format, mbr_data)
                mbr.disk_fit = chr(disk_fit % 128) 

            print("\tMBR tamaño:", mbr.mbr_tamano)
            print("\tMBR fecha creación:", mbr.mbr_fecha_creacion)
            print("\tDisco fit:", mbr.disk_fit)
            print("\tMBR disk signature:", mbr.mbr_disk_signature)

        except Exception as e:
            print("\tERROR: No se pudo leer el disco en la ruta: " + path+", debido a: "+str(e))'''