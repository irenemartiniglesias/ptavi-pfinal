#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import sys
import socketserver
from proxy_registrar import Datos_Log
import os

class ReadXML(ContentHandler):
    """ Clase para manejar el xml ua1 """

    def __init__ (self):
        self.lista = []
        self.diccionario = {'account' : ['username', 'password'],
        'uaserver' : ['ip', 'puerto'], 'rtpaudio' : ['puerto'],
        'regproxy' : ['ip', 'puerto'], 'log' : ['path'], 'audio' : ['path']}
        
    def startElement (self, name, atrrs):
        """ Metodo para abrir etiqueta y almacenar su contenido """
        if name in self.diccionario:
            diccionario_atributos = {}
            for valor in self.diccionario[name]:
                diccionario_atributos[valor] = atrrs.get(valor, "")
            diccionario_etiquetas = {name : diccionario_atributos}
            self.lista.append(diccionario_etiquetas)

    def coger_etiquetas(self):
        return self.lista

class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    def handle(self):
        """Escribe dirección y puerto del cliente (de tupla client_address)."""
        #lee la línea del cliente que envia, la decodifica y la guarda en una 
        #variable para despues quedarnos con lo que nos interesa de ella
        linea = self.rfile.read()
        linea_decod = linea.decode('utf-8')
        #metodos validos
        METHOD = linea_decod.split(' ')[0].upper()
        METHODS = ['INVITE', 'BYE', 'ACK']
        #Escribimos en el log lo que recibimos
        Recibido = 'Recived to '
        Datos_Log(LOG, Recibido, REGPROXY_IP, REGPROXY_PUERTO, linea_decod)
        if len(linea_decod) >= 2:
            if METHOD == 'INVITE':
                msj = 'Via: SIP/2.0/UDP branch=z9hG4bKnashds7\r\n'
                msj += 'SIP/2.0 100 Trying \r\n'
                msj += 'SIP/2.0 180 Ring \r\n'
                msj += 'SIP/2.0 200 OK \r\n'
                msj += 'Content-Type: application/sdp \r\n'
                msj += 'v=0 \r\n'
                msj += 'o=' + USUARIO + ' ' + UASERVER_IP + '\r\n'
                msj += 's=misesion \r\n'
                msj += 't=0 \r\n' + 'm=audio' +' ' + RTPAUDIO + ' RTP'
                #Enviamos la respuesta al cliente
                self.wfile.write(bytes(msj,('utf-8')))
                #Escribimos lo que nos manda el cliente
                print('EL cliente nos manda: ' + linea_decod)
                #escribimos lo que se nos manda en el Log
                Evento = 'Send to '
                Datos_Log(LOG, Evento, REGPROXY_IP, REGPROXY_PUERTO, msj)
            elif METHOD == 'BYE':
                messj = 'SIP/2.0 200 OK \r\n'
                self.wfile.write(bytes(msj,('utf-8')))
                print("El cliente nos manda " + linea_decod)
                #ecribimos mensaje recibido en el log
                Evento = 'Send to '
                Datos_Log(LOG, Evento, REGPROXY_IP, REGPROXY_PUERTO, messj)
            elif METHOD == 'ACK':
                aEjecutar = './mp32rtp -i ' + UASERVER_IP + ' -p' + RTPAUDIO
                aEjecutar += '<' + AUDIO
                os.system(aEjecutar)
                print("El cliente nos manda " + linea_decod)
                #ecribimos mensaje recibido en el log
                Evento = 'Send to '
                Datos_Log(LOG, Evento, REGPROXY_IP, REGPROXY_PUERTO, aEjecutar)
            elif METHOD not in METHODS:
                mesj = 'SIP/2.0 405 Method Not Allowed \r\n'
                self.wfile.write(bytes(msj,('utf-8')))
                print("El cliente nos manda " + linea_decod)
                #ecribimos mensaje recibido en el log
                Evento = 'Send to '
                Datos_Log(LOG, Evento, REGPROXY_IP, REGPROXY_PUERTO, mesj)
        else:
            self.wfile.write('b"SIP/2.0 400 Bad Request\r\n')
            print("El cliente nos manda " + linea_decod)
            #ecribimos mensaje recibido en el log
            Evento = 'Send to '
            Datos_Log(LOG, Evento, REGPROXY_IP, REGPROXY_PUERTO, linea_decod)
    
        
        

if __name__ == "__main__":
    
    CONFIG = sys.argv[1]
    
    #Sacamos los datos del XML 
    parser = make_parser()
    cHandler = ReadXML()
    parser.setContentHandler(cHandler)
    parser.parse(open(CONFIG)) 
    lista = cHandler.coger_etiquetas()
    
    #guardamos los datos sacados en variables 
    USUARIO = lista[0]['account']['username']
    PASSSWORD = lista[0]['account']['password']
    UASERVER_IP = lista[1]['uaserver']['ip']
    UASERVER_PUERTO = lista[1]['uaserver']['puerto']
    RTPAUDIO = lista[2]['rtpaudio']['puerto']
    REGPROXY_IP = lista[3]['regproxy']['ip']
    REGPROXY_PUERTO = lista[3]['regproxy']['puerto']
    LOG = lista[4]['log']['path']
    AUDIO = lista[5]['audio']['path']

    if int(UASERVER_PUERTO) < 1024:
        sys.exit('PORT INCORRET, please enter a port bigger than 1024')
    if len(sys.argv) != 2:
        sys.exit('Usage: python client.py method receiver@IP:SIPport')

    """Creamos servidor de eco y escuchamos"""
    serv = socketserver.UDPServer((UASERVER_IP, int(UASERVER_PUERTO)), EchoHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
