import random
import os
import time
import struct
import sys
import Struct.Structs


class Disk:
    def __init__(self):
        pass

    def command_mkdisk(size, path, unit, fit):
        disco = Struct.Structs.MBR()
        try:
            if unit == "K":
                total_size = 1024 * size
            elif unit == "M":
                total_size = 1024 * 1024 * size
            else:
                print("Error: Unidad no válida")
                return
            if size <= 0:
                print("Error: El parámetro size del comando MKDISK debe ser mayor a 0")
                return

            fit = fit
            disco.mbr_tamano = total_size
            disco.mbr_fecha_creacion = int(time.time())
            disco.disk_fit = fit
            disco.mbr_disk_signature = random.randint(100, 9999)

            if os.path.exists(path):
                print("Error: Disco ya existente en la ruta: " + path)
                return

            folder_path = os.path.dirname(path)
            os.makedirs(folder_path, exist_ok=True)

            disco.mbr_Partition_1 = Struct.Structs.Particion()
            disco.mbr_Partition_2 = Struct.Structs.Particion()
            disco.mbr_Partition_3 = Struct.Structs.Particion()
            disco.mbr_Partition_4 = Struct.Structs.Particion()

            if path.startswith('"'):
                path = path[1:-1]

            if not path.endswith(".dsk"):
                print(
                    "Error: Extensión de archivo no válida para la creación del Disco."
                )
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
                print("Error: Error al crear el disco en la ruta: " + path)
        except ValueError:
            print(
                "Error: El parámetro size del comando MKDISK debe ser un número entero"
            )

    def command_rmdisk(path):
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        try:
            if os.path.isfile(path):
                if not path.endswith(".dsk"):
                    print(
                        "Error: Extensión de archivo no válida para la eliminación del Disco."
                    )
                opcion = input(
                    "\t¿Está seguro que desea eliminar el disco? (S/N): "
                ).lower()
                if opcion == "s":
                    os.remove(path)
                    print(">>>> RMDISK: Disco eliminado exitosamente <<<<")
                else:
                    print(
                        ">>>> RMDISK: Eliminación del disco cancelada correctamente <<<<"
                    )
            else:
                print("El disco no existe en la ruta indicada.")
        except Exception as e:
            print("Error al intentar eliminar el disco: " + str(e))

    def command_fdisk(size, path, unit, fit, tipo, name):
        try:
            if unit == "B":
                total_size = size
            elif unit == "K":
                total_size = 1024 * size
            elif unit == "M":
                total_size = 1024 * 1024 * size
            else:
                raise RuntimeError("-unit no contiene los valores esperados...")
                return

            if size <= 0:
                raise RuntimeError("-size debe de ser mayor que 0")
                return
        
            if fit.lower() != "bf" and fit.lower() != "ff" and fit.lower() != "wf":
                raise RuntimeError("-fit no contiene los valores esperados...")
                return
            
            if tipo.lower() != "p" and tipo.lower() != "e" and tipo.lower() != "l":
                raise RuntimeError("-type no contiene los valores esperados...")
                return
            if not os.path.exists(path):
                raise RuntimeError("Error: No existe el disco en la ruta: "+path)
                return
            try:
                mbr = Struct.Structs.MBR()
                with open(path, "rb") as file:
                    mbr_data = file.read()
                    mbr.mbr_tamano = struct.unpack("<i", mbr_data[:4])[0]
                    mbr.mbr_fecha_creacion = struct.unpack("<i", mbr_data[4:8])[0]
                    mbr.mbr_disk_signature = struct.unpack("<i", mbr_data[8:12])[0]
                    mbr.disk_fit = mbr_data[12:14].decode('utf-8')

                    partition_size = struct.calcsize("<iii16s")*4
                    partition_data = mbr_data[14:14 + partition_size]
                    mbr.mbr_Partition_1.__setstate__(partition_data[0:28]) 
                    mbr.mbr_Partition_2.__setstate__(partition_data[27:56]) 
                    mbr.mbr_Partition_3.__setstate__(partition_data[54:84]) 
                    mbr.mbr_Partition_4.__setstate__(partition_data[81:112])

            except Exception as e:
                print(e)

            
            partitions = [mbr.mbr_Partition_1, mbr.mbr_Partition_2, mbr.mbr_Partition_3, mbr.mbr_Partition_4]
            between = []
            used = 0
            ext = 0
            c = 1
            base = sys.getsizeof(mbr) 
            extended = Struct.Structs.Particion()
            for prttn in partitions:
                if prttn.part_status == '1':
                    trn = Struct.Structs.Transition()
                    trn.partition = c
                    trn.start = prttn.part_start
                    trn.end = prttn.part_start + prttn.part_size
                    trn.before = trn.start - base
                    base = trn.end
                    if used != 0:
                        between[used - 1].after = trn.start - (between[used - 1].end)
                    between.append(trn)
                    used += 1

                    if prttn.part_type.lower() == 'e':
                        ext += 1
                        extended = prttn
                else: 
                    partitions[c - 1] = Struct.Structs.Particion()

                if used == 4 and tipo.lower() != "l":
                    raise RuntimeError("Limite de particiones alcanzado")
                elif ext == 1 and tipo.lower() == "e":
                    raise RuntimeError("Solo se puede crear una particion Extendida.")

                mbr.mbr_Partition_1 = partitions[0]
                mbr.mbr_Partition_2 = partitions[1]
                mbr.mbr_Partition_3 = partitions[2]
                mbr.mbr_Partition_4 = partitions[3]
                
                c += 1
            
            if ext == 0 and tipo.lower() == "l":
                raise RuntimeError("No existe particion Extendida para crear la Logica")
            
            if used != 0:
                between[-1].after = mbr.mbr_tamano - between[-1].end
            
            try:
                Disk.buscarParticiones(mbr, name, path)
                print("FDISK", "El nombre: "+name+" ya existe en el disco")
                return
            except Exception as e:
                print(e)
            
            temporal = Struct.Structs.Particion()
            temporal.part_status = '1'
            temporal.part_size = total_size
            temporal.part_type = tipo[0].upper()
            temporal.part_fit = fit[0].upper()
            temporal.part_name = name
            
            if tipo.lower() == "l": 
                Disk.logica(temporal, extended, path)
                return
            
            mbr = Disk.ajustar(mbr, temporal, between, partitions, used)
            with open(path, "rb+") as bfile:
                bfile.write(mbr.__bytes__())
                if tipo.lower() == "e":
                    ebr = Struct.Structs.EBR()
                    ebr.part_start = startValue 
                    bfile.seek(startValue, 0)
                    bfile.write(ebr.__bytes__())
                    print("FDISK", "partición extendida:", name, "creada correctamente")
                    return
                print("FDISK", "partición primaria:", name, "creada correctamente")
        except ValueError as e: 
            print("FDISK", "-size debe ser un entero")
        except Exception as e: 
            print("FDISK", str(e))

    def get_particiones(disco):
        particiones = []
        particiones.append(disco.mbr_Partition_1)
        particiones.append(disco.mbr_Partition_2)
        particiones.append(disco.mbr_Partition_3)
        particiones.append(disco.mbr_Partition_4)
        return particiones

    def get_logicas(partition, p):
        ebrs = []

        with open(p, "rb+") as file:
            start_position = partition.part_start -1
            if start_position < 0:
                start_position = 0
                
            file.seek(start_position, 0)
            tmp_data = file.read(struct.calcsize("c2s3i3i16s"))

            while len(tmp_data) == struct.calcsize("c2s3i3i16s"):
                tmp = Struct.Structs.EBR()
                tmp.__setstate__(tmp_data)
                if tmp.part_next != -1 :
                    ebrs.append(tmp)
                    file.seek(tmp.part_next-1, 0)
                    tmp_data = file.read(struct.calcsize("c2s3i3i16s"))
                else:
                    break

        return ebrs

    def logica(partition, ep, p):
        nlogic = Struct.Structs.EBR()
        nlogic.part_status = '1'
        nlogic.part_fit = partition.part_fit
        nlogic.part_size = partition.part_size
        nlogic.part_next = -1
        nlogic.part_name = partition.part_name

        with open(p, "rb+") as file:
            file.seek(0)
            tmp = Struct.Structs.EBR()
            file.seek(ep.part_start -1)
            tmp_data = file.read(struct.calcsize("c2s3i3i16s"))
            tmp.__setstate__(tmp_data)
            size = 0
            while True:
                size += struct.calcsize("c2s3i3i16s") + tmp.part_size
                if (tmp.part_status == '0' or tmp.part_status == '\x00') and tmp.part_next == -1:
                    nlogic.part_start = tmp.part_start
                    nlogic.part_next = nlogic.part_start + nlogic.part_size + struct.calcsize("c2s3i3i16s")
                    if (ep.part_size - size) <= nlogic.part_size:
                        raise RuntimeError("no hay espacio para más particiones lógicas")
                    file.seek(nlogic.part_start-1) 
                    file.write(nlogic.__bytes__())
                    file.seek(nlogic.part_next)
                    addLogic = Struct.Structs.EBR()
                    addLogic.part_status = '0'
                    addLogic.part_next = -1
                    addLogic.part_start = nlogic.part_next
                    file.seek(addLogic.part_start)
                    file.write(addLogic.__bytes__())
                    name = nlogic.part_name
                    print(f"partición lógica: {name}, creada correctamente.")
                    return
                file.seek(tmp.part_next-1)
                tmp_data = file.read(struct.calcsize("c2s3i3i16s"))
                tmp.__setstate__(tmp_data)

    def ajustar(mbr, p, t, ps, u):
        if u == 0:
            p.part_start = sys.getsizeof(mbr) + struct.calcsize("<iii16s")*4
            startValue = p.part_start
            Disk.update_start_value(p.part_start)
            mbr.mbr_Partition_1 = p
            return mbr
        else:
            usar = Struct.Structs.Transition()
            c = 0
            for tr in t:
                if c == 0:
                    usar = tr
                    c += 1
                    continue

                if mbr.disk_fit[0].upper() == 'F':
                    if usar.before >= p.part_size or usar.after >= p.part_size:
                        break
                    usar = tr
                elif mbr.disk_fit[0].upper() == 'B':
                    if usar.before < p.part_size or usar.after < p.part_size:
                        usar = tr
                    else:
                        if tr.before >= p.part_size or tr.after >= p.part_size:
                            b1 = usar.before - p.part_size
                            a1 = usar.after - p.part_size
                            b2 = tr.before - p.part_size
                            a2 = tr.after - p.part_size

                            if (b1 < b2 and b1 < a2) or (a1 < b2 and a1 < a2):
                                c += 1
                                continue
                            usar = tr
                elif mbr.disk_fit[0].upper() == 'W':
                    if usar.before < p.part_size or usar.after < p.part_size:
                        usar = tr
                    else:
                        if tr.before >= p.part_size or tr.after >= p.part_size:
                            b1 = usar.before - p.part_size
                            a1 = usar.after - p.part_size
                            b2 = tr.before - p.part_size
                            a2 = tr.after - p.part_size
                            if (b1 > b2 and b1 > a2) or (a1 > b2 and a1 > a2):
                                c += 1
                                continue
                            usar = tr
                c += 1

            if usar.before >= p.part_size or usar.after >= p.part_size:
                if mbr.disk_fit[0].upper() == 'F':
                    if usar.before >= p.part_size:
                        p.part_start = (usar.start - usar.before)
                        startValue = p.part_start
                        Disk.update_start_value(p.part_start)
                    else:
                        p.part_start = usar.end
                        startValue = p.part_start
                        Disk.update_start_value(p.part_start)
                elif mbr.disk_fit[0].upper() == 'B':
                    b1 = usar.before - p.part_size
                    a1 = usar.after - p.part_size

                    if (usar.before >= p.part_size and b1 < a1) or usar.after < p.part_start:
                        p.part_start = (usar.start - usar.before)
                        startValue = p.part_start
                        Disk.update_start_value(p.part_start)
                    else:
                        p.part_start = usar.end
                        startValue = p.part_start
                        Disk.update_start_value(p.part_start)
                elif mbr.disk_fit[0].upper() == 'W':
                    b1 = usar.before - p.part_size
                    a1 = usar.after - p.part_size

                    if (usar.before >= p.part_size and b1 > a1) or usar.after < p.part_start:
                        p.part_start = (usar.start - usar.before)
                        startValue = p.part_start
                        Disk.update_start_value(p.part_start)
                    else:
                        p.part_start = usar.end
                        startValue = p.part_start
                        Disk.update_start_value(p.part_start)

                partitions = [Struct.Structs.Particion() for _ in range(4)]

                for i in range(len(ps)):
                    partitions[i] = ps[i]
                
                for i in range(len(partitions)):
                    if partitions[i].part_status == '0':
                        partitions[i] = p
                        break
                mbr.mbr_Partition_1 = partitions[0]
                mbr.mbr_Partition_2 = partitions[1]
                mbr.mbr_Partition_3 = partitions[2]
                mbr.mbr_Partition_4 = partitions[3]
                return mbr
            else:
                raise RuntimeError("no hay espacio suficiente")
            
    def buscarParticiones(mbr, name, path):
            partitions = [mbr.mbr_Partition_1, mbr.mbr_Partition_2, mbr.mbr_Partition_3, mbr.mbr_Partition_4]
            ext = False
            extended = Struct.Structs.Particion()

            for partition in partitions:
                if partition.part_status == '1':
                    if partition.part_name == name:
                        return partition
                    elif partition.part_type == 'E':
                        ext = True
                        extended = partition

            if ext:
                ebrs = Disk.get_logicas(extended, path)
                for ebr in ebrs:
                    if ebr.part_status == '1':
                        if ebr.part_name == name:
                            tmp = Struct.Structs.Particion()
                            tmp.part_status = '1'
                            tmp.part_type = 'L'
                            tmp.part_fit = ebr.part_fit
                            tmp.part_start = ebr.part_start
                            tmp.part_size = ebr.part_size
                            tmp.part_name = ebr.part_name
                            return tmp
            raise RuntimeError("Creando la partición: " + name + "...")
    
    def update_start_value(new_value):
        global startValue
        startValue = new_value

    def command_fdisk2(size, path, unit, fit, tipo, name):
        try:
            if unit == "B":
                total_size = size
            elif unit == "K":
                total_size = 1024 * size
            elif unit == "M":
                total_size = 1024 * 1024 * size
            else:
                raise RuntimeError("-unit no contiene los valores esperados...")
                return

            if size <= 0:
                raise RuntimeError("-size debe de ser mayor que 0")
                return
        
            if fit.lower() != "bf" and fit.lower() != "ff" and fit.lower() != "wf":
                raise RuntimeError("-fit no contiene los valores esperados...")
                return
            
            if tipo.lower() != "p" and tipo.lower() != "e" and tipo.lower() != "l":
                raise RuntimeError("-type no contiene los valores esperados...")
                return
            if not os.path.exists(path):
                raise RuntimeError("Error: No existe el disco en la ruta: "+path)
                return
            try:
                mbr = Struct.Structs.MBR()
                with open(path, "rb") as file:
                    mbr_data = file.read()
                    mbr.mbr_tamano = struct.unpack("<i", mbr_data[:4])[0]
                    mbr.mbr_fecha_creacion = struct.unpack("<i", mbr_data[4:8])[0]
                    mbr.mbr_disk_signature = struct.unpack("<i", mbr_data[8:12])[0]
                    mbr.disk_fit = mbr_data[12:14].decode('utf-8')
                    
                    partition_size = struct.calcsize("<iii16s")*4
                    partition_data = mbr_data[14:14 + partition_size]
                    mbr.mbr_Partition_1.__setstate__(partition_data[0:28]) 
                    mbr.mbr_Partition_2.__setstate__(partition_data[28:56]) 
                    mbr.mbr_Partition_3.__setstate__(partition_data[56:84]) 
                    mbr.mbr_Partition_4.__setstate__(partition_data[84:112])
            except Exception as e:
                print(e)

            partitions = [mbr.mbr_Partition_1, mbr.mbr_Partition_2, mbr.mbr_Partition_3, mbr.mbr_Partition_4]
            size_elim = []
            for particion in partitions:
                if(particion.part_status == "D"):
                    size_elim.append(particion.part_size)
            for particion in partitions:
                if(particion.part_type == "E" and tipo == "E"):
                    raise RuntimeError("Ya existe una particion extendida")
                    return
                elif(particion.part_type == "P" and tipo == "P"):
                    if(particion.part_name == name):
                        raise RuntimeError(f"Error: Particion Primaria con nombre "+name+" ya existente")
                        return
            mbr_size = 14 + struct.calcsize("<iii16s")*4
            if mbr.disk_fit == "FF":
                aux_size = mbr_size
                for particion in partitions:
                    if tipo == "P":
                        if particion.part_status == "1":
                            aux_size += particion.part_size
                        elif particion.part_status == "0":
                            particion.part_status = "1"
                            particion.part_type = tipo
                            particion.part_fit = fit
                            particion.part_size = total_size
                            particion.part_name = name
                            particion.part_start = aux_size
                            aux_size += total_size
                            break
                        elif particion.part_status == "D":
                            size_elim = size_elim[0]
                            if size_elim >= total_size:
                                particion.part_status = "1"
                                particion.part_type = tipo
                                particion.part_fit = fit
                                particion.part_size = total_size
                                particion.part_name = name
                                particion.part_start = aux_size
                                aux_size += total_size
                                break
                            else:
                                raise RuntimeError("Error: espacio insuficiente")
                                return
                    elif tipo == "E":
                        ebr = Struct.Structs.EBR()
                        if particion.part_status == "1":
                            aux_size += particion.part_size
                        elif particion.part_status == "0":
                            particion.part_status = "1"
                            particion.part_type = tipo
                            particion.part_fit = fit
                            particion.part_size = total_size
                            particion.part_name = name
                            particion.part_start = aux_size

                            ebr.part_status = "1"
                            ebr.part_fit = fit
                            ebr.part_size = total_size
                            ebr.part_name = name
                            ebr.part_start = aux_size
                            ebr.part_next = -1
                            aux_size += total_size
                            break
                        elif particion.part_status == "D":
                            size_elim = size_elim[0]
                            if size_elim >= total_size:
                                particion.part_status = "1"
                                particion.part_type = tipo
                                particion.part_fit = fit
                                particion.part_size = total_size
                                particion.part_name = name
                                particion.part_start = aux_size

                                ebr.part_status = "1"
                                ebr.part_fit = fit
                                ebr.part_size = total_size
                                ebr.part_name = name
                                ebr.part_start = aux_size
                                ebr.part_next = -1
                                aux_size += total_size

                                break
                            else:
                                raise RuntimeError("Error: espacio insuficiente")
                                return
                    elif tipo == "L":
                        for particion in partitions:
                            if particion.part_type == "E":
                                Disk.crearLogicas(particion.part_start, total_size, path, name, fit,particion.part_size)
                                return
                        
            elif mbr.disk_fit == "BF":
                aux_size = mbr_size
                for particion in partitions:
                    if tipo == "P":
                        if particion.part_status == "1":
                            aux_size += particion.part_size
                        elif particion.part_status == "0":
                            particion.part_status = "1"
                            particion.part_type = tipo
                            particion.part_fit = fit
                            particion.part_size = total_size
                            particion.part_name = name
                            particion.part_start = aux_size
                            aux_size += total_size
                            break
                        elif particion.part_status == "D":
                            size_elim.sort()
                            size_elim = size_elim[0]
                            if size_elim >= total_size:
                                particion.part_status = "1"
                                particion.part_type = tipo
                                particion.part_fit = fit
                                particion.part_size = total_size
                                particion.part_name = name
                                particion.part_start = aux_size
                                aux_size += total_size
                                break
                            else:
                                raise RuntimeError("Error: espacio insuficiente")
                                return
                    elif tipo == "E":
                        ebr = Struct.Structs.EBR()
                        if particion.part_status == "1":
                            aux_size += particion.part_size
                        elif particion.part_status == "0":
                            particion.part_status = "1"
                            particion.part_type = tipo
                            particion.part_fit = fit
                            particion.part_size = total_size
                            particion.part_name = name
                            particion.part_start = aux_size

                            ebr.part_status = "1"
                            ebr.part_fit = fit
                            ebr.part_size = total_size
                            ebr.part_name = name
                            ebr.part_start = aux_size
                            ebr.part_next = -1
                            aux_size += total_size
                            break
                        elif particion.part_status == "D":
                            size_elim.sort()
                            size_elim = size_elim[0]
                            if size_elim >= total_size:
                                particion.part_status = "1"
                                particion.part_type = tipo
                                particion.part_fit = fit
                                particion.part_size = total_size
                                particion.part_name = name
                                particion.part_start = aux_size
                                
                                ebr.part_status = "1"
                                ebr.part_fit = fit
                                ebr.part_size = total_size
                                ebr.part_name = name
                                ebr.part_start = aux_size
                                ebr.part_next = -1
                                aux_size += total_size
                                break
                            else:
                                raise RuntimeError("Error: espacio insuficiente")
                                return        
            elif mbr.disk_fit == "WF":
                ebr = Struct.Structs.EBR()
                aux_size = mbr_size
                for particion in partitions:
                    if tipo == "P":
                        if particion.part_status == "1":
                            aux_size += particion.part_size
                        elif particion.part_status == "0":
                            particion.part_status = "1"
                            particion.part_type = tipo
                            particion.part_fit = fit
                            particion.part_size = total_size
                            particion.part_name = name
                            particion.part_start = mbr_size + aux_size
                            aux_size += total_size
                            break
                        elif particion.part_status == "D":
                            size_elim.sort(reverse=True)
                            size_elim = size_elim[0]
                            if size_elim >= total_size:
                                particion.part_status = "1"
                                particion.part_type = tipo
                                particion.part_fit = fit
                                particion.part_size = total_size
                                particion.part_name = name
                                particion.part_start = mbr_size + aux_size
                                aux_size += total_size
                                break
                            else:
                                raise RuntimeError("Error: espacio insuficiente")
                                return    

                    if tipo == "E":
                        if particion.part_status == "1":
                            aux_size += particion.part_size
                        elif particion.part_status == "0":
                            particion.part_status = "1"
                            particion.part_type = tipo
                            particion.part_fit = fit
                            particion.part_size = total_size
                            particion.part_name = name
                            particion.part_start = mbr_size + aux_size

                            ebr.part_status = "1"
                            ebr.part_fit = fit
                            ebr.part_size = total_size
                            ebr.part_name = name
                            ebr.part_start = aux_size
                            ebr.part_next = -1
                            aux_size += total_size
                            break
                        elif particion.part_status == "D":
                            size_elim.sort(reverse=True)
                            size_elim = size_elim[0]
                            if size_elim >= total_size:
                                particion.part_status = "1"
                                particion.part_type = tipo
                                particion.part_fit = fit
                                particion.part_size = total_size
                                particion.part_name = name
                                particion.part_start = mbr_size + aux_size

                                ebr.part_status = "1"
                                ebr.part_fit = fit
                                ebr.part_size = total_size
                                ebr.part_name = name
                                ebr.part_start = aux_size
                                ebr.part_next = -1
                                aux_size += total_size
                                break
                            else:
                                raise RuntimeError("Error: espacio insuficiente")
                                return     
                            
            
            try:
                with open(path, "rb+") as bfile:
                    bfile.write(mbr.__bytes__())
                    if tipo.lower() == "p":
                        print("FDISK", "Particion primaria:",name,"creada correctamente")
                    elif tipo.lower() == "e":
                        bfile.seek(ebr.part_start, 0)
                        bfile.write(ebr.__bytes__())
                        print("FDISK", "partición extendida:", name, "creada correctamente")
                        return
            except Exception as e:
                print("Error: Error al crear el disco en la ruta: "+path)

        except ValueError as e: 
            print("FDISK", "-size debe ser un entero")
        except Exception as e: 
            print("FDISK", str(e))
        
    def crearLogicas(start, size, path, name, fit, size_elim):
        nlogicas= Struct.Structs.EBR()
        tmp= Struct.Structs.EBR()
        bandera= True
        try:
            with open(path, "rb") as file:
                while bandera:
                    file.seek(start)
                    ebr_data = file.read()
                    nlogicas.__setstate__(ebr_data)
                    if nlogicas.part_name == name:
                        print("Error: Ya existe una particion logica con el nombre",name)
                        return
                    if nlogicas.part_next == -1:
                        bandera = False
                    else:
                        start = nlogicas.part_next 
        except Exception as e:
            print("Ha ocurrido un error al crear la particion logica",e)
        nlogicas.part_status = '1'
        nlogicas.part_fit = fit
        nlogicas.part_start = start
        nlogicas.part_size = size
        nlogicas.part_next = start + size
        nlogicas.part_name = name

        tmp.part_status = '0'
        tmp.part_fit = 'WF'
        tmp.part_start = start + size
        tmp.part_size = 0
        tmp.part_next = -1
        tmp.part_name = ''
        try:
            with open(path, "rb+") as file:
                file.seek(start)
                file.write(nlogicas.__bytes__())
                file.seek(start + size)
                file.write(tmp.__bytes__())
                print(f"FDISK","Partición logica", name, "creada exitosamente")
        except Exception as e:
            print(e)
            print("Error: Error al crear la partición en el disco: "+path)

    def command_fdisk_delete(path, name):
        if not os.path.exists(path):
                raise RuntimeError("Error: No existe el disco en la ruta: "+path)
                return
        try:
            mbr = Struct.Structs.MBR()
            with open(path, "rb") as file:
                mbr_data = file.read()
                mbr.mbr_tamano = struct.unpack("<i", mbr_data[:4])[0]
                mbr.mbr_fecha_creacion = struct.unpack("<i", mbr_data[4:8])[0]
                mbr.mbr_disk_signature = struct.unpack("<i", mbr_data[8:12])[0]
                mbr.disk_fit = mbr_data[12:14].decode('utf-8')
                
                partition_size = struct.calcsize("<iii16s")*4
                partition_data = mbr_data[14:14 + partition_size]
                mbr.mbr_Partition_1.__setstate__(partition_data[0:28]) 
                mbr.mbr_Partition_2.__setstate__(partition_data[28:56]) 
                mbr.mbr_Partition_3.__setstate__(partition_data[56:84]) 
                mbr.mbr_Partition_4.__setstate__(partition_data[84:112])
        except Exception as e:
            print(e)

        partitions = [mbr.mbr_Partition_1, mbr.mbr_Partition_2, mbr.mbr_Partition_3, mbr.mbr_Partition_4]
        for particion in partitions:
            if(particion.part_type == "E"):
                if(particion.part_name== name):
                    with open(path, "rb+") as file:
                        file.seek(particion.part_start)
                        file.write(b'\x00'*particion.part_size)
                    particion.part_status = "D"
                    particion.part_fit = "WF"
                    particion.part_size = 0
                    particion.part_start = 0
                    particion.part_name = ""
                    particion.part_type = "P"
                    break
                start=particion.part_start
                nlogicas= Struct.Structs.EBR()
                bandera= True
                try:
                    with open(path, "rb+") as file:
                        while bandera:
                            file.seek(start)
                            ebr_data = file.read()
                            nlogicas.__setstate__(ebr_data)
                            if nlogicas.part_name == name:
                                principio = nlogicas.part_start
                                file.seek(start)
                                file.write(b'\x00'*nlogicas.part_size)
                                
                                start = nlogicas.part_next
                                nlogicas.part_status = 'D'
                                nlogicas.part_fit = 'WF'
                                nlogicas.part_start = 0
                                nlogicas.part_size = 0
                                nlogicas.part_next = -1
                                nlogicas.part_name = ''

                                file.seek(principio)
                                file.write(nlogicas.__bytes__())
                                print("FDISK","Particion logica",name,"eliminada exitosamente")
                                return
                            if nlogicas.part_next == -1:
                                bandera = False
                            else:
                                start = nlogicas.part_next 
                except Exception as e:
                    print("Ha ocurrido un error al eliminar la particion logica",e)
            elif(particion.part_type == 'P'):
                if(particion.part_name== name):
                    with open(path, "rb+") as file:
                        file.seek(particion.part_start)
                        file.write(b'\x00'*particion.part_size)
                    particion.part_status = "D"
                    particion.part_fit = "WF"
                    particion.part_size = 0
                    particion.part_start = 0
                    particion.part_name = ""
                    particion.part_type = "P"
        try:
            with open(path, "rb+") as file:
                file.write(mbr.__bytes__())
                print("FDISK","Particion",name,"eliminada exitosamente")
        except Exception as e:
            print("Error: Error al crear el disco en la ruta: "+path)

    def imp(path):
        try:
            mbr = Struct.Structs.MBR()
            with open(path, "rb") as file:
                mbr_data = file.read()
                mbr.mbr_tamano = struct.unpack("<i", mbr_data[:4])[0]
                mbr.mbr_fecha_creacion = struct.unpack("<i", mbr_data[4:8])[0]
                mbr.mbr_disk_signature = struct.unpack("<i", mbr_data[8:12])[0]
                mbr.disk_fit = mbr_data[12:14].decode('utf-8')
                    
                partition_size = struct.calcsize("<iii16s")*4
                partition_data = mbr_data[14:14 + partition_size]
                mbr.mbr_Partition_1.__setstate__(partition_data[0:28]) 
                mbr.mbr_Partition_2.__setstate__(partition_data[28:56]) 
                mbr.mbr_Partition_3.__setstate__(partition_data[56:84]) 
                mbr.mbr_Partition_4.__setstate__(partition_data[84:112])
                print("TamaÃ±o: "+str(mbr.mbr_tamano))
                print("Fecha: "+str(mbr.mbr_fecha_creacion))
                print("Signature: "+str(mbr.mbr_disk_signature))
                print("Fit: "+str(mbr.disk_fit))
                print("Particion 1:")
                print("\tStatus: "+str(mbr.mbr_Partition_1.part_status))
                print("\tType: "+str(mbr.mbr_Partition_1.part_type))
                print("\tFit: "+str(mbr.mbr_Partition_1.part_fit))
                print("\tStart: "+str(mbr.mbr_Partition_1.part_start))
                print("\tSize: "+str(mbr.mbr_Partition_1.part_size))
                print("\tName: "+str(mbr.mbr_Partition_1.part_name))
                print("Particion 2:")
                print("\tStatus: "+str(mbr.mbr_Partition_2.part_status))
                print("\tType: "+str(mbr.mbr_Partition_2.part_type))
                print("\tFit: "+str(mbr.mbr_Partition_2.part_fit))
                print("\tStart: "+str(mbr.mbr_Partition_2.part_start))
                print("\tSize: "+str(mbr.mbr_Partition_2.part_size))
                print("\tName: "+str(mbr.mbr_Partition_2.part_name))
                print("Particion 3:")
                print("\tStatus: "+str(mbr.mbr_Partition_3.part_status))
                print("\tType: "+str(mbr.mbr_Partition_3.part_type))
                print("\tFit: "+str(mbr.mbr_Partition_3.part_fit))
                print("\tStart: "+str(mbr.mbr_Partition_3.part_start))
                print("\tSize: "+str(mbr.mbr_Partition_3.part_size))
                print("\tName: "+str(mbr.mbr_Partition_3.part_name))
                print("Particion 4:")
                print("\tStatus: "+str(mbr.mbr_Partition_4.part_status))
                print("\tType: "+str(mbr.mbr_Partition_4.part_type))
                print("\tFit: "+str(mbr.mbr_Partition_4.part_fit))
                print("\tStart: "+str(mbr.mbr_Partition_4.part_start))
                print("\tSize: "+str(mbr.mbr_Partition_4.part_size))
                print("\tName: "+str(mbr.mbr_Partition_4.part_name))
        except Exception as e:
            print(e)

    """def rep(tokens):
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
            print("\tERROR: No se pudo leer el disco en la ruta: " + path+", debido a: "+str(e))"""
