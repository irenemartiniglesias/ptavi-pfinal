#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import sys
import socketserver

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
     

     
if __name__ == "__main__":
    #Sacamos los datos del XML 
    CONFIG = sys.argv[1]
    parser = make_parser()
    cHandler = ReadXmlProxy()
    parser.setContentHandler(cHandler)
    parser.parse(open(CONFIG)) 
    lista = cHandler.coger_etiquetas()


    IP = lista[0]['server']['ip']
    PUERTO = lista[0]['server']['puerto']
    
