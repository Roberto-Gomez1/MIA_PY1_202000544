from Sintactico import *
def main():
    #while True:
        #opcion = input("Ingrese su comando: ")
        opcion = 'execute -path= prueba.txt'
        if opcion[:13] == 'execute -path':
            archivo_path = opcion[15:]
            try:
                with open(archivo_path, 'r') as archivo:
                    contenido = archivo.read()  # Leer contenido completo del archivo
                    archivo.close()
                    parse(contenido)
            except FileNotFoundError:
                print("Archivo no encontrado:", archivo_path)
        else:
            print("Ruta incorrecta")
            #break

if __name__ == '__main__':
    main()