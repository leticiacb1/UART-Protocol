#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from componenteFisico.client.enlace import *
import time
import numpy as np

import random

from interface.display import *
from data_struc.data_client import *

from log import *

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
#serialName = "COM6"                  # Windows(variacao de)

class Client():

    def __init__(self,loc_arquivo, id_arquivo,num_server,serial_name, interface, opcao) -> None:

        # Cofnigurações iniciais
        self.serial_name = serial_name
        self.loc_arquivo = loc_arquivo
        self.id_arquivo = id_arquivo
        self.id_server = num_server

        # Instanciando Datagrama
        self.datagrama = DataClient()
        
        # Objeto enlace
        self.com = None

        self.inicia = False
        self.encerrar_conexao = False

        self.msm = None
        self.tam_msm = 0
        self.count = 0
        self.total_pacotes = 0
        self.tam_pacote_resto = 0
        self.tam_payload = 114
        self.resto = False

        # Controle de Time Out
        self.flagTimer20 = True
        self.timer20 = 0

        # Para escrever em arquivo txt
        self.opcao = opcao
        self.doc = Log(nome= 'client' , opcao = opcao)                ######### Filtrar de acordo com a opção de caso selecionada ! ###########

        # Instanciando interface gráfica:
        self.gui = interface

        # Variável para construir error:
        self.justOneTime = True
        self.crc_error = False
    
    def start(self):
        '''
            Função principal de estado. Encadeia as ações realizadas pelo cliente.
        '''

        try:
            self.conecta()
            self.ler_arquivo_e_separa_pacotes()
            self.handShake()
            self.transmissao_de_dados()
            self.doc.cria_log()
            self.encerrar_transmissao()

        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.com.disable()
    
    def conecta(self):
        '''
            Conecta porta e instancia objeto Enlace.
        '''
        
        self.com = enlace(self.serial_name)
        self.com.enable()

        self.gui.conectado()

    def handShake(self):
        '''
            Função que realiza o handshake e permanece esperando uma resposta enquanto o time out não for levantado.
        '''

        self.gui.HandShake()

        while (self.inicia == False and not self.encerrar_conexao):

            handshake = self.datagrama.handShake(total_pacotes = self.total_pacotes, id_arquivo =  self.id_arquivo , id = self.id_server , opcao=self.opcao)
            self.com.sendData(np.asarray(handshake))      

            # Escreve na documentação
            self.doc.escreve_log(acao="[ENVIA]", tipo = "HANDSHAKE", protocolo=1,
                                    pacote_enviado = "-" , tam_bytes = 0, total_pacotes = self.total_pacotes)

            # Pedido pelo diagrama do cliente
            time.sleep(5)

            # Set timer de 20 segundos:
            self.setTimer20()

            resposta, _ = self.com.getData(self.datagrama.tam_header+self.datagrama.tam_EOP, timer20 = self.timer20)
            self.acknowledge_notacknowlwdge(resposta, handshake=True)
    
    def transmissao_de_dados(self):
        '''
            Função que inicia transmissão dos pacotes.
        '''
        if(not self.encerrar_conexao):
            self.gui.indica_progresso()
        
        while(self.count<=self.total_pacotes and not self.encerrar_conexao):
                
            if(self.count == self.total_pacotes and self.tam_pacote_resto!= 0):  
                # Ajustando envio para o último pacote (Pacote Resto)
                self.tam_payload = self.tam_pacote_resto
                self.resto = True

            # PROVOCANDO ERROR 2 #
            if(self.count == 6 and self.justOneTime):
                if(self.opcao == '2'):
                    # Error da contagem de pacotes:
                    self.count = 9
                    self.justOneTime  = False

            # PROVOCANDO ERROR CRC #
            if(self.opcao == '6'):
                self.crc_error = False
                if(self.count == 6 and self.justOneTime):
                    self.crc_error = True
                    self.justOneTime  = False
                
            pacote = self.datagrama.envia_dados( 
                    numero_pck = self.count, total_pacotes = self.total_pacotes, tam_payload = self.tam_payload, 
                    resto = self.resto, mensagem = self.msm, crc_error = self.crc_error)

            self.com.sendData(np.asarray(pacote))
            # print(f"{self.count} - {pacote[10:]}")

            # Escreve na documentação.
            self.doc.escreve_log(tipo = "DADO", acao="[ENVIA]", protocolo=3,
                                    pacote_enviado = str(self.count) , tam_bytes = self.tam_payload, total_pacotes = self.total_pacotes)

            # Set timer de 20 segundos:
            self.setTimer20()

            resposta, _ =  self.com.getData(self.datagrama.tam_header + self.datagrama.tam_EOP, timer20 = self.timer20 )

            self.acknowledge_notacknowlwdge(resposta)

    def encerrar_transmissao(self):
        '''
            Função responsável por encerrar a comunicação. Seja ela forçada ou não.
        '''

        self.com.disable()
        self.gui.encerra_conexao()

    ##################################################### FUNCOES AUXILIARES ##################################################################

    def  acknowledge_notacknowlwdge(self, resposta, handshake = False):
        '''
            Classifica respostas obtidas do servidor
            Opcoes: 
                2  - Resposta HandShake
                4  - Tudo Okay com o pacote OU servidor em ESPERA
                5  - TIME OUT
                6  - ERROR de pacote ou no payload
                -1 - Passaram-se 5 segundos / Reeenvio de pacote
                -2 - Passaram-se 20 segundos / Encerrar transmissão.
        '''

        if(resposta[0] == 2):                                                                                            # Recebe msm tipo 2
            
            self.count+=1
            self.inicia = True
            self.flagTimer20 = True

            # Escreve na documentação
            self.doc.escreve_log(tipo= "HANDSHAKE" ,acao = "[RECEBEU]", protocolo=2,
                                    pacote_enviado = "-", tam_bytes=0, total_pacotes= self.total_pacotes)

            self.gui.inicia_envio(num_pacotes=self.total_pacotes, tam_pacote_resto=self.tam_pacote_resto)
            
        elif(resposta[0] == 4 and self.count == resposta[7]):

            self.count+=1 
            self.flagTimer20 = True

            # print("Proximo\n")
            self.gui.progress(count = self.count, total = self.total_pacotes)

            # Escreve na documentação
            self.doc.escreve_log(tipo = "OK", acao="[RECEBEU]", protocolo = 4,
                                 pacote_enviado = str(self.count-1), tam_bytes = 0, total_pacotes = self.total_pacotes)   # Tudo certo com o pacote número tal.
                                    
    
        elif(resposta[0] == 5):                                                                                         # Msm de Time out enviada pelo servidor.
            
            self.encerrar_conexao = True
            self.gui.time_out()
            
            # Escreve na documentação
            self.doc.escreve_log(tipo = "TIME OUT", acao = "[RECEBEU]", protocolo=5,
                                pacote_enviado = "-", tam_bytes = 0, total_pacotes = self.total_pacotes)

        elif(resposta[0] == 6):
            
            self.gui.error(num_atual=self.count, num_pacote_de_reenvio=resposta[7], num_pck_error=resposta[6], CRC = not self.crc_error)
            self.com.rx.clearBuffer()

            # Iniciando count a partir do ultimo pacote correto:
            self.count = resposta[7]
            self.flagTimer20 = True
            
            # Escreve na documentação
            self.doc.escreve_log(tipo = "ERROR", acao = "[RECEBEU]", protocolo=6,
                                pacote_enviado = str(resposta[7]) , tam_bytes = 0, total_pacotes = self.total_pacotes)   # Pacote enviado =  número do pacote com error.

            self.gui.indica_progresso()

        elif(resposta[0] == -2):
            
            self.encerrar_conexao = True
            self.gui.time_out()

            self.com.sendData(np.asarray(self.datagrama.msm_time_out()))

            # Escreve na documentação:
            self.doc.escreve_log(tipo = "TIME OUT", acao = "[ENVIA]", protocolo=5,
                                pacote_enviado = "-" , tam_bytes = 0, total_pacotes = self.total_pacotes)

        elif(resposta[0] == -1):

            # Passaram 5 segundos
            self.flagTimer20 = False
            if(handshake):
                self.inicia = False

            self.gui.esperando()

    def ler_arquivo_e_separa_pacotes(self):
        '''
            Lê arquivo que se deseja enviar e identifica a quantidade de pacotes que serão enviados.
        '''

        self.msm = mensagem = open(self.loc_arquivo , 'rb').read() 
        self.tam_msm = len(mensagem)

        self.total_pacotes , self.tam_pacote_resto = self.datagrama.numero_de_pacotes(self.tam_msm)
    
    def setTimer20(self):
        '''
            Atualiza tempo para contagem de 20 segundos (time out) , caso a flag seja verdadeira.
        '''

        if(self.flagTimer20):
            self.timer20 = time.time()
                        
if __name__ == "__main__":
    
    serialName = "COM4"
    id = 231
    server = 80

    interface = Display(name='CLIENT')
    opcao_selecionada = interface.start()

    cliente = Client(loc_arquivo = 'arquivos/enviado/image.png' , id_arquivo = id ,num_server = server,serial_name = serialName, interface = interface, opcao = opcao_selecionada)
    cliente.start()