#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import sys
import socketserver
import random 
import os 
import json
import hashlib


class ReadXmlProxy(ContentHandler):
    """Clase para leer el xml pr.xml"""
    def __init__(self):
        """Coge los atributos del xml y los amacena en un diccionario"""
        self.lista = []
        self.dicc = {'server' : ['name', 'ip', 'puerto'],
        'database' : ['path', 'passwdpath'],
        'log' : ['path']}

    def startElement(self, name, atrrs):
        """Coge la etiqueta y almacena su contenido"""
        if name in self.dicc:
            dicc_atributos = {}
            for valor in self.dicc[name]:
                dicc_atributos[valor] = atrrs.get(valor, "")
            dicc_tags = {name : dicc_atributos}
            self.lista.append(dicc_tags)

    def coger_etiquetas(self):
        """Devuelve las etiquetas y sus valores en forma de lista"""
        return self.lista

def CrearSocket( IP, PUERTO, LINE):
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP, int(PUERTO)))
    my_socket.send(LINE)

def comprobar_registro(dicc_client, Client):
	if Client not in dicc_client.keys():
		datos = '0'
	else:
	    datos = dicc_client[Client]
	return datos

     
class EchoProxyHandler(socketserver.DatagramRequestHandler):


    dicc_client = {}
    # Variable aleatoria NONCE
    NONCE = random.getrandbits(100)

    def handle(self):

        #self.txt_registro_seguro(DATABASE_PATH)
        # Actualizamos el diccionario de clientes por si ha caducado el Espires
        # de algún cliente
        #Time_Caduced(self.dicc_client)

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            line_decod = line.decode('utf-8')
            METHOD = line_decod.split(' ')[0].upper()
            # Métodos permitidos
            METHODS = ['REGISTER', 'INVITE', 'BYE', 'ACK']
            # La IP y el Puerto de quien recibimos el mensaje
            Ip = self.client_address[0]
            Puerto = self.client_address[1]
            if line_decod != '':
                print("Recibimos:\r\n" + line_decod)
                # Escribimos mensages de recepción en el fichero de log
                Evento = ' Received from '
                #Datos_Log(PATH_LOG, Evento, Ip, Puerto, line_decod)
            if len(line_decod) >= 2:
                if METHOD == 'REGISTER':
                    list = line_decod.split('\r\n')
                    Client = list[0].split(':')[1]
                    list0 = list[0].split(':')[2]
                    Port_UA = list0.split(' ')[0]
                    if len(list) == 4:
                        mssg = 'SIP/2.0 401 Unauthorized\r\n'
                        mssg += 'Via: SIP/2.0/UDP branch=z9hG4bKnashds7\r\n'
                        mssg += 'WWW Authenticate: Digest nonce="'
                        mssg += str(self.NONCE) + '"\r\n\r\n'
                        # Enviamos el mensaje de respuesta al REGISTER sin
                        # Autenticación
                        self.wfile.write(bytes(mssg, 'utf-8'))
                        # Escribimos los mensages de envio en el log
                        Event = ' Send to '
                        #Datos_Log(PATH_LOG, Event, Ip, Port_UA, mssg)
                    elif len(lista) == 5:
                        Psswd_Salto_Linea = lista[2].split('response="')[1]
                        Psswd = Psswd_Salto_Linea.split('"')[0]
                        Found = self.CheckPsswd(DATA_PASSWDPATH, Psswd, Client,
                                                Ip, Puerto)
                        if Found == 'True':
                            try:
                                Expires = lista[1].split(' ')[1]
                                if Expires == '0':
                                    del self.dicc_client[Client]
                                    Event = ' Borrando ' + Client
                                    Datos_Log(PATH_LOG, Event, '', '', '')
                                else:
                                    Now = time.time()
                                    Exp = int(Expires)
                                    Time_Sum = float(Exp) + Now
                                    cliente = [Ip, Port_UA, Exp, Time_Sum]
                                    self.dicc_client[Client] = cliente
                                messg = 'SIP/2.0 200 OK\r\n'
                                messg += 'Via: SIP/2.0/UDP '
                                messg += 'branch=z9hG4bKnashds7\r\n\r\n'
                                self.wfile.write(bytes(messg, 'utf-8'))

                            except:
                                messg = "Expires no es un entero\r\n"
                                messg += 'Via: SIP/2.0/UDP '
                                messg += 'branch=z9hG4bKnashds7\r\n\r\n'
                                self.wfile.write(bytes(messg, 'utf-8'))
                                # Escribimos el mensage de envio en el log
                                Event = ' Send to '
                                Datos_Log(PATH_LOG, Event, Ip, Puerto, messg)
                                break

                elif METHOD == 'INVITE':
                    Sip_direccion = line_decod.split(' ')[1]
                    UA = Sip_direccion.split(':')[1]
                    # Comprobación de si el usuario está registrado o no
                    Usuario_Regist = comprobar_registro(self.dicc_client, UA)
                    # En función de si está registrado o no actuamos de
                    # diferente forma
                    if Usuario_Regist == '0':
                        mssg = "SIP/2.0 404 User Not Found\r\n"
                        mssg += "Via: SIP/2.0/UDP "
                        mssg += "branch=z9hG4bKnashds7\r\n\r\n"
                        # Ecribimos los datos que se envian en el log
                        Event = ' Send to '
                        #Datos_Log(PATH_LOG, Event, Ip, Puerto, mssg)
                        self.wfile.write(bytes(mssg, 'utf-8'))
                    else:
                        # Datos de la ip y puerto del usuario registrado
                        Ip_Regist = Usuario_Regist[0]
                        Port_Regist = Usuario_Regist[1]
                        # Miramos que la conexión sea segura y se envían datos
                        # o se hace sys.exit en función de la conexión
                        Linea = Añadir_Cabecera_Proxy(line_decod)
                        self.Conexion_Segura(PATH_LOG, Port_Regist, Ip_Regist,
                                             Linea)

                elif METHOD == 'ACK':
                    Sip_direccion = line_decod.split(' ')[1]
                    UA = Sip_direccion.split(':')[1]
                    # Comprobación de si el usuario está registrado o no
                    Usuario_Regist = comprobar_registro(self.dicc_client, UA)
                    if Usuario_Regist == '0':
                        mssg = "SIP/2.0 404 User Not Found\r\n\r\n"
                        mssg += "Via: SIP/2.0/UDP "
                        mssg += "branch=z9hG4bKnashds7\r\n\r\n"
                        # Ecribimos los datos que se envian en el log
                        Event = ' Send to '
                        Datos_Log(Path, Event, Ip, Puerto, mssg)
                        self.wfile.write(bytes(mssg, 'utf-8'))
                    else:
                        # Datos de la ip y puerto del usuario registrado
                        Ip_Regist = Usuario_Regist[0]
                        Port_Regist = int(Usuario_Regist[1])

                        # Abrimos un socket y enviamos
                        Linea = Añadir_Cabecera_Proxy(line_decod)
                        Open_Socket(PATH_LOG, Ip_Regist, Port_Regist, Linea)

                elif METHOD == 'BYE':
                    Sip_direccion = line_decod.split(' ')[1]
                    UA = Sip_direccion.split(':')[1]
                    # Comprobación de si el usuario está registrado o no
                    Usuario_Regist = comprobar_registro(self.dicc_client, UA)
                    if Usuario_Regist == '0':
                        mssg = "SIP/2.0 404 User Not Found\r\n\r\n"
                        mssg += "Via: SIP/2.0/UDP "
                        mssg += "branch=z9hG4bKnashds7\r\n\r\n"
                        # Ecribimos los datos que se envian en el log
                        Event = ' Send to '
                        Datos_Log(PATH_LOG, Event, Ip, Puerto, mssg)
                        self.wfile.write(bytes(mssg, 'utf-8'))
                    else:
                        # Datos de la ip y puerto del usuario registrado
                        Ip_Regist = Usuario_Regist[0]
                        Port_Regist = int(Usuario_Regist[1])
                        # Miramos que la conexión sea segura y se envían datos
                        # o se hace sys.exit en función de la conexión
                        Linea = Añadir_Cabecera_Proxy(line_decod)
                        self.Conexion_Segura(PATH_LOG, Port_Regist, Ip_Regist,
                                             Linea)

                elif METHOD not in METHODS:
                    mssg_send = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                    mssg_send += 'Via: SIP/2.0/UDP '
                    mssg_send += 'branch=z9hG4bKnashds7\r\n\r\n'
                    self.wfile.write(bytes(mssg_send, 'utf-8'))
                    # Escribimos en el log el mensaje de envío 405
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, Ip, Puerto, mssg_send)
                else:
                    # Respuesta mal formada
                    mssg_send = 'SIP/2.0 400 Bad Request\r\n\r\n'
                    mssg_send += 'Via: SIP/2.0/UDP '
                    mssg_send += 'branch=z9hG4bKnashds7\r\n\r\n'
                    self.wfile.write(bytes(mssg_send, 'utf-8'))
                    # Escribimos en el log el mensaje de envío 405
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, Ip, Puerto, mssg_send)

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

     

     
if __name__ == "__main__":
    #Sacamos los datos del XML 
    CONFIG = sys.argv[1]
    parser = make_parser()
    cHandler = ReadXmlProxy()
    parser.setContentHandler(cHandler)
    parser.parse(open(CONFIG)) 
    lista = cHandler.coger_etiquetas()

    
    PROXY_SERVER = lista[0]['server']['ip']
    PROXY_PUERTO = lista[0]['server']['puerto']
	 
    serv = socketserver.UDPServer((PROXY_SERVER, int(PROXY_PUERTO)), EchoProxyHandler)
    print("Listening...")
    
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
    
