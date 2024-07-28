#!/usr/bin/python

import SocketServer
import threading
from time import sleep
from datetime import datetime
from random import randint

import protocolo

# ========== REGLAS ==========
HOST = "localhost"
PUERTO = 8080
RANGO_MIN_ID = 1
RANGO_MAX_ID = 99999
USUARIOS = {"26759":26759}
BUZONES = "./buzones/"
# ============================

class MyUDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        datos = self.request[0].strip()
        sock = self.request[1]
        peticion = procesar(datos, sock, self.client_address)
        sleep(1)

class ThreadingUDPServer(SocketServer.ThreadingMixIn, SocketServer.ForkingUDPServer):
    pass

def cargarUsuarios():
    with open(BUZONES + "BUZONES", "r") as f:
        for line in f:
            buzon = line.rstrip("\r\n")
            USUARIOS[buzon] = int(buzon)
    return len(USUARIOS.keys())

def descargar(datos):
    peticion = list()
    if(datos["ID2"] in USUARIOS):    
        with open(BUZONES + datos["ID2"], "r") as f:
            for line in f:
                line = line.rstrip("\n")
                peticion.append(line)
            peticion.append("EOT")
        print "[O] Se decargaron los mensajes del buzon [%s]"%(datos["ID2"])
    else:
        peticion.append("[X] Error, el buzon no existe")
        peticion.append("EOT")
        print "[X] Error, se intentaron decargar los mensajes de un buzon inexistente (buzon=%s)"%(datos["ID2"])
    return peticion

def guardarMensaje(datos):
    if(datos["ID2"] in USUARIOS):
        with open(BUZONES + datos["ID2"], "a") as f: f.write(datos["mensaje"]+"\n")
        peticion = "\n[O] Se dejo un mensaje en el buzon [%s]"%(datos["ID2"])
        print "[O] Se dejo un mensaje en el buzon [%s]"%(datos["ID2"])
    else:
        peticion = "\n[X] Error, el buzon no existe"
        print "[X] Error, se intento dejar un mensaje en un buzon inexistente (buzon=%s)"%(datos["ID2"])
    return peticion

def crearID():
    global USUARIOS
    ID = str(randint(RANGO_MIN_ID, RANGO_MAX_ID))
    USUARIOS[ID] = int(ID)
    with open(BUZONES + ID, "w") as f: f.write("Bienvenido a Buzon 1.0\n")
    with open(BUZONES + "BUZONES", "a") as f: f.write(ID+"\n")
    print "[O] Nuevo buzon creado [id=%s]"%(ID)
    return ID

def acciones(datos):
    opcion = datos["accion"]
    
    if(opcion == 1):
        peticion = descargar(datos)
    if(opcion == 2):
        peticion = guardarMensaje(datos)
    if(opcion == 3):
        peticion = crearID()
    
    return peticion


def procesar(datos, sock, clientAddr):
    datos = protocolo.desempaquetar(datos)
    peticion = acciones(datos)
    if(type(peticion) is not list):
        try:
            peticion = protocolo.empaquetar(datos["accion"], datos["ID1"], datos["ID2"], peticion)
            sock.sendto(peticion, clientAddr)
        except Exception, e:
            respuesta = "[X] Error al enviar la peticion (error=%s)"%(e)
            error = True
    else:
        for a, p in enumerate(peticion):
            try:
                p = protocolo.empaquetar(datos["accion"], str(1), datos["ID2"], p)
                sock.sendto(p, clientAddr)
            except Exception, e:
                respuesta = "[X] Error al enviar la peticion (error=%s)"%(e)
                error = True
    sleep(0.5)
    return peticion

def main():
    global HOST, PUERTO
    socketServidor = ThreadingUDPServer((HOST, PUERTO), MyUDPHandler)
    server_thread = threading.Thread(target=socketServidor.serve_forever)
    server_thread.start()

    print "\n [>] Iniciando servidor, espere..."
    print "\n [>] Cargando base de datos, espere..."
    cantidad = cargarUsuarios()
    print "\n [O] Se cargaron [%d] buzones"%(cantidad)
    print "\n [O] Servidor listo"
    print " %s"%(str(datetime.now()))
    print "\n ============ LOG ============\n"
    

if(__name__=="__main__"):
    main()