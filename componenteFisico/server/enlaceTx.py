#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Camada de Enlace
####################################################

# Importa pacote de tempo
import time

# Threads
import threading

# Class
class TX(object):
 
    def __init__(self, fisica):
        self.fisica      = fisica
        self.buffer      = bytes(bytearray())
        self.transLen    = 0
        self.empty       = True
        self.threadMutex = False               
        self.threadStop  = False


    def thread(self):
        while not self.threadStop:
            if(self.threadMutex):             # Ativado caso chamado o sendBuffer
                self.transLen    = self.fisica.write(self.buffer)      
                self.threadMutex = False

    def threadStart(self):
        self.thread = threading.Thread(target=self.thread, args=())   # Recebe e envia dados simultaneamente?
        self.thread.start()

    def threadKill(self):
        self.threadStop = True

    def threadPause(self):
        self.threadMutex = False

    def threadResume(self):
        self.threadMutex = True

    def sendBuffer(self, data):
        self.transLen   = 0             
        self.buffer = data
        #print(f'Buffer Tx transmissao : {self.buffer}')
        self.threadMutex  = True  

    def getBufferLen(self):
        return(len(self.buffer))

    def getStatus(self):
        return(self.transLen)
        

    def getIsBussy(self):
        return(self.threadMutex)

