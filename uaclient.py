#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import sys
import socket

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
        
try:
    CONFIG = sys.argv[1]
    METHOD = sys.argv[2]
    OPTION = sys.argv[3]
except:
    sys.exit('Usage: python3 uaclient.py config method option')

if len(sys.argv) != 4:
    sys.exit('Usage: python3 uaclient.py config method option')

if __name__ == "__main__":

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
    
    lista_metodos = ['REGISTER', 'INVITE', 'BYE']
    if METHOD not in lista_metodos:
        print("only methods: REGISTER, INVITE OR BYE")
        sys.exit("Usage: python uaclient.py config method option")

    """Contenido que vamos a enviar."""
    Linea_sip = ' sip:' + USUARIO + ' ' + UASERVER_IP + ' SIP/2.0\r\n'
    LINEA = METHOD + Linea_sip


    """Creamos el socket, lo configuramos y lo atamos a un servidor/puerto"""
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((UASERVER_IP, int(UASERVER_PUERTO)))

    print("Send: " + LINEA)
    my_socket.send(bytes(LINEA, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)

    print('Recived -- ', data.decode('utf-8'))
    print("finish socket...")

    lista = data.decode('utf-8').split('\r\n\r\n')[0:-1]
    if lista == ['SIP/2.0 100 Trying', 'SIP/2.0 180 Ring', 'SIP/2.0 200 OK']:
        LINEACK = 'ACK' + Linea_sip
        print ('Enviando: ' + LINEACK)
        my_socket.send(bytes(LINEACK, 'utf-8') + b'\r\n')
        data = my_socket.recv(1024)


    """Cerramos todo."""
    my_socket.close()
    print("Fin.")
    
       
