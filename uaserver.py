#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import sys
import socketserver

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
        #coge el método de la posición en la que se encuentra y cada metodo
        #tiene sus codigos de respuesta
        METHOD = linea_decod.split(' ')[0].upper()
        METHODS = ['INVITE', 'BYE', 'ACK']
        if len(linea_decod) >= 2:
            if METHOD == 'INVITE':
                msj = 'SIP/2.0 100 Trying \r\n\r\n'
                msj += 'SIP/2.0 180 Ring \r\n\r\n'
                msj += 'SIP/2.0 200 OK \r\n\r\n'
                msj += 'Content-Type: application/sdp \r\n\r\n'
                msj += 'v=0 \r\n\r\n'
                msj += 'o=' + USUARIO + ' ' + UASERVER_IP + '\r\n\r\n'
                msj += 's=misesion \r\n\r\n'
                msj += 't=0 \r\n\r\n' + 'm=audio' +' ' + RTPAUDIO + ' RTP'
                #Enviamos la respuesta al cliente
                self.wfile.write(bytes(msj,('utf-8')))
                #Escribimos lo que nos manda el cliente
                print('EL cliente nos manda: ' + linea_decod)
            elif METHOD == 'BYE':
                msj = 'SIP/2.0 200 OK \r\n\r\n'
                self.wfile.write(bytes(msj,('utf-8')))
                print("El cliente nos manda " + linea_decod)
            elif METHOD == 'ACK':
                aEjecutar = './mp32rtp -i ' + UASERVER_IP + ' -p' + RTPAUDIO
                aEjecutar += '<' + AUDIO
                os.system(aEjecutar)
                print("El cliente nos manda " + linea_decod)
            elif METHOD not in METHODS:
                msj = 'SIP/2.0 405 Method Not Allowed \r\n\r\n'
                self.wfile.write(bytes(msj,('utf-8')))
                print("El cliente nos manda " + linea_decod)
        else:
            self.wfile.write('b"SIP/2.0 400 Bad Request\r\n\r\n')
            print("El cliente nos manda " + linea_decod)
    
        
        

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
