#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import sys
import socket

class UaClient(ContentHandler):
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
        
try:
    CONFIG = sys.argv[1]
    METHOD = sys.argv[2]
    OPTION = sys.argv[3]
except:
    sys.exit('Usage: python3 uaclient.py config method option')
 
if __name__ == "__main__":
    """
    Programa principal
    """
    parser = make_parser()
    cHandler = UaClient()
    parser.setContentHandler(cHandler)
    parser.parse(open(archivo))
    print(cHandler.coger_etiquetas())        
