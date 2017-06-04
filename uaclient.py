#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import sys
import socket
import hashlib

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
    METHOD1 = sys.argv[2]
    METHOD = METHOD1.upper()
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
    PASSWORD = lista[0]['account']['password']
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
    Linea_sip = METHOD + ' sip:'    
    if METHOD == 'REGISTER':
        Linea = Linea_sip + USUARIO + ':' + REGPROXY_PUERTO
        Linea += ' SIP/2.0' + '\r\n' + 'EXPIRES: ' + OPTION + '\r\n'
    elif METHOD == 'INVITE':
        Linea = Linea_sip + USUARIO + 'SIP/2.0'
        Linea += '\r\n' + 'Content-Type: application/sdp' + '\r\n''\r\n' + 'v=0'
        Linea += '\r\n' + 'o=' + USUARIO + ' ' + UASERVER_IP + '\r\n'
        Linea += 's=misesion' + '\r\n' + 't=0'
        Linea += '\r\n' + 'm=audio ' + RTPAUDIO + ' RTP'
    elif METHOD == 'BYE':
        Linea = Linea_sip + OPTION + 'SIP/2.0'
    else:
        Linea = Linea_sip + OPTION + 'SIP/2.0'
      


    """Creamos el socket, lo configuramos y lo atamos a un servidor/puerto"""
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((REGPROXY_IP, int(REGPROXY_PUERTO)))

    print("Send: " + Linea)
    my_socket.send(bytes(Linea, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    data_decod = data.decode('utf-8')
    print('Recived -- ', data.decode('utf-8'))

    Via = 'Via: SIP/2.0/UDP branch=z9hG4bKnashds7'       
    lista = data_decod.split('\r\n' + Via + '\r\n')[0:-1]
    No_Autorizada = data_decod.split('\r\n')[0]
    Trying = 'SIP/2.0 100 Trying'
    Ring = 'SIP/2.0 180 Ring'
    OK = 'SIP/2.0 200 OK'
    if lista[0:3] == [Trying, Ring , OK]:
        LINEACK = 'ACK' + ' sip:' + OPTION + 'SIP/2.0' + b'\r\n'
        my_socket.send(bytes(LINEACK, 'utf-8') + b'\r\n')
        data = my_socket.recv(1024)
    elif No_Autorizada == 'SIP/2.0 401 Unauthorized':
        aleatorio = hashlib.md5()
        Nonce_salto_linea = data_decod.split('nonce="')[1]
        Nonce = Nonce_salto_linea = data_decod.split('"')[0]
        aleatorio.update(bytes(PASSWORD + Nonce, 'utf-8'))
        RESPONSE = aleatorio.hexdigest()
        LINE_REGIST = Linea_sip + USUARIO + ":" + UASERVER_PUERTO
        LINE_REGIST += " SIP/2.0\r\n" + "Expires: " + OPTION + "\r\n"
        LINE_REGIST += 'Authorization: Digest response="' + RESPONSE
        LINE_REGIST += '"\r\n'
        
        my_socket.send(bytes(LINE_REGIST, 'utf-8') + b'\r\n')
        data = my_socket.recv(1024)


    """Cerramos todo."""
    print("finish socket...")
    my_socket.close()
    print("Fin.")
    
       
