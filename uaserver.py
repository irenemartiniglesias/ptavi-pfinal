#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import sys


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


if __name__ == "__main__":

    if PORT < 1024:
        sys.exit('PORT INCORRET, please enter a port bigger than 1024')
    if len(sys.argv) != 4:
        sys.exit('Usage: python client.py method receiver@IP:SIPport')

    """Creamos servidor de eco y escuchamos"""
    serv = socketserver.UDPServer((SERVER, PORT), EchoHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
