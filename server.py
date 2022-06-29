#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 

from componenteFisico.server.enlace import *
import time
import numpy as np

from interface.display import *
from data_struc.data_server import *
from log import *

class Server():

    def __init__(self, id_servidor, serial_name, path_arquivo):
        
        # Configurações iniciais
        self.serial_name = serial_name
        self.id = id_servidor
        self.path_arquivo = path_arquivo
        
        self.ocioso = True
        self.encerrar_conexao = False

        # Objeto enlace:
        self.com  = None

        # Instanciando Datagrama
        self.datagrama = DataServer()

        # Controle de Time Out
        self.flagTimer20 = True
        self.timer20 = None

        # Recebido pelo servidor
        self.num_pck_recebido = 0
        self.tam_payload = 0
        self.payload_recebido = 0

        self.msm_recebida = b''
        self.count = 0
        self.total_pacotes = 0

        # Para escrever em arquivo txt
        # Preenchido e instanciado pós handshake com a opção escolhida
        self.opcao = None
        self.doc = None   

        # Instancia Interface Gráfica:
        self.gui = Display(name="SERVER")
        
        # Tenta contorna problemas no inicio:
        self.passouhandShake = False

        # Verificação CRC:
        self.crc_okay = False
        self.crc = None

    def start(self):
        '''
            Função principal de estado. Encadeia as ações realizadas pelo servidor.
        '''

        try:
            self.conecta()
            self.handShake()
            self.recebe_transmissao()
            self.constroi_msm_recebida()
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
            Função que espera primeira comunicação do cliente (HandShake).
            Flag Time Out desativada até a realização do HandShake.
        '''

        while self.ocioso:
            
            header, _ = self.com.getData(self.datagrama.tam_header, timer20=-1, passouHandShake=self.passouhandShake)    # Timer = -1 impede o timeout no handshake pelo servidor.
            self.acknowledge_notacknowlwdge(header)
        
        self.gui.HandShake()
        # Envia resposta HandShake:
        self.com.sendData(np.array(self.datagrama.resposta_handshake()))
        self.count = 1

        # Escreve na documentação
        self.doc.escreve_log(tipo= "HANDSHAKE" ,acao = "[ENVIA]", protocolo=2,
                             pacote_enviado = "-", tam_bytes=0, total_pacotes= self.total_pacotes)

    def recebe_transmissao(self):
        '''
            Função que recebe mensagem do cliente , tratando e enviando uma resposta.
        '''
        self.gui.recebe_transmissao()

        while(self.count<=self.total_pacotes and not self.encerrar_conexao):

            # Set timer
            self.setTimer20()

            if(self.count>=1):
                # Impedindo o envio de EM ESPERA até o handshake ser finalizado.
                self.passouhandShake = True    
            
            #  Provocar Error 4 #
            if(self.opcao == 4 and self.count == 9):
                self.encerrar_conexao = True
                break
            else:
                header , _ = self.com.getData(self.datagrama.tam_header, timer20=self.timer20)
                
                self.crc = header[-2:]
                print(f"\n CRC RECEBIDO: {self.crc}")

                self.acknowledge_notacknowlwdge(header)
            ####################


    def constroi_msm_recebida(self):
        '''
            Função que escreve mensagem final formada pela junção de todos os pacotes enviados.
        '''

        imageW = self.path_arquivo
        f = open(imageW, 'wb')
        f.write(self.msm_recebida)
        f.close()

    def encerrar_transmissao(self):
        '''
            Função responsável por encerrar a comunicação. Seja ela forçada ou não.
        '''

        self.com.disable()
        self.gui.encerra_conexao()

    ##################################################### FUNCOES AUXILIARES ##################################################################

    def setTimer20(self):
        '''
            Atualiza tempo para contagem de 20 segundos (time out) , caso a flag seja verdadeira.
        '''

        if(self.flagTimer20):
            self.timer20 = time.time()

    def  acknowledge_notacknowlwdge(self, header):
        
        '''
            Classifica respostas obtidas do cliente
            Opcoes: 
                1  - HandShake
                3  - Recebe dado.
                5  - TIME OUT
                -1 - Passaram-se 2 segundos / Avisa que está em espera.
                -2 - Passaram-se 20 segundos / Encerrar transmissão.
        '''

        if(header[0] == 1 and header[4] == self.id):                           

            # Confere posição EOP:
            EOP, _ = self.com.getData(self.datagrama.tam_EOP, timer20=-1)

            if(EOP == self.datagrama.cria_EOP()):

                self.ocioso = False
                self.total_pacotes = header[3]                                 # Total de pacotes que serão enviados.

                # Opcao Selecionada pelo cliente: Necessário para a contrucao do Log correto
                self.opcao = header[1]
                self.doc = Log(nome = 'server' , opcao = self.opcao)
                ############################################################################

                self.flagTimer20 = True
                time.sleep(1)

                # Escreve na documentação
                self.doc.escreve_log(tipo= "HANDSHAKE" ,acao = "[RECEBE]", protocolo=1,
                                    pacote_enviado = "-", tam_bytes=0, total_pacotes= self.total_pacotes)
                
            else:
                self.gui.error_nao_tratado()
                self.com.rx.clearBuffer()
                # Handshake será reenviado

            if(self.ocioso):
                self.gui.esperando()
            
        elif(header[0] == 3):

                self.num_pck_recebido = header[4]
                self.tam_payload = header[5]
                self.payload_recebido , _ = self.com.getData(self.tam_payload, timer20=self.timer20)

                # Escreve na documentação
                self.doc.escreve_log(tipo= "DADO" ,acao = "[RECEBE]", protocolo=3,
                                    pacote_enviado = str(self.num_pck_recebido), tam_bytes=0, total_pacotes= self.total_pacotes)

                self.verifica_informacao()

        elif(header[0] == 5):         # Msm de Time out enviada pelo cliente.
            
            # self.gui.encerra_conexao()
            self.encerrar_conexao = True

            # Escreve na documentação
            self.doc.escreve_log(tipo= "TIME OUT" ,acao = "[RECEBE]", protocolo=5,
                                    pacote_enviado = "-", tam_bytes=0, total_pacotes= self.total_pacotes)
            
        elif(header[0] == -2):

            self.ocioso = True
            self.encerrar_conexao = True

            self.com.sendData(np.asarray(self.datagrama.msm_time_out()))

            # Escreve na documentação
            self.doc.escreve_log(tipo= "TIME OUT" ,acao = "[ENVIA]", protocolo=5,
                                    pacote_enviado = "-", tam_bytes=0, total_pacotes= self.total_pacotes)
            
        elif(header[0] == -1 and self.passouhandShake):

            self.gui.esperando()
            self.flagTimer20  = False  

            self.com.sendData(np.asanyarray(self.datagrama.tudo_okay(ultimo_pck_correto=self.count)))  

            # Escreve na documentação
            self.doc.escreve_log(tipo= "EM ESPERA" ,acao = "[ENVIA]", protocolo=4,
                                    pacote_enviado = str(self.count), tam_bytes=0, total_pacotes= self.total_pacotes)

        else:
            self.gui.error_nao_tratado()
            # Tranforma pacote recebido como sendo o count do servidor, para reenvio. Necessário para reaproveitar função msm_error. 
            # ACIONADO EM ERROR NA INTERFACE ... NAO FUNCIONAL AINDA :(
            self.num_pck_recebido = self.count
            self.com.rx.clearBuffer()
            self.envia_msm_error()

    def verifica_informacao(self):
        '''
            Verifica se a informação de dado recebida está com o número do pacote esperado pelo servidor
            e se o EOP está na posição correta (caso nao esteja, error no tamanho do Payload)
        '''
        
        if(self.num_pck_recebido == self.count):
            # Verifica se EOP está na posição correta
            self.verifica_EOPeCRC()
        else:
            # Error no número do pacote recebido
            self.error_num_pacote()
    
    def verifica_EOPeCRC(self):
        '''
            Função que verifica a posição do EOP, levantando um erro caso não esteja na posição esperada.
            Inicializa flagTimer20.
        '''

        # Verificando EOP na posição correta:
        EOP , _ = self.com.getData(self.datagrama.tam_EOP, timer20=self.timer20)
        
        # Verificação CRC:
        self.crc_okay = self.datagrama.verifica_crc(self.crc, self.payload_recebido)

        if(EOP == self.datagrama.cria_EOP() and self.crc_okay):

            # Envia msm de tudo certo
            self.com.sendData(np.asanyarray(self.datagrama.tudo_okay(ultimo_pck_correto=self.count)))

            # Escreve na documentação
            self.doc.escreve_log(tipo= "OK" , acao = "[ENVIA]", protocolo=4,
                                pacote_enviado = str(self.count), tam_bytes=0, total_pacotes= self.total_pacotes)

            self.count+=1
            self.flagTimer20 = True
            self.msm_recebida+=self.payload_recebido

        else:
            self.envia_msm_error()

    def error_num_pacote(self):

        '''
            Função chamada quando o número do pacote indicado pelo header não é o esperado pelo servidor.
        '''
       
        EOP , _ = self.com.getData(self.datagrama.tam_EOP, timer20=self.timer20)
        
        # Envia mensagem de error:
        self.envia_msm_error()

    def envia_msm_error(self):
        
        '''
            Função que envia mensagem de error (tipo 6).
            Inicializa flagTimer20.
        '''

        self.com.sendData(np.asarray(self.datagrama.error(num_error=self.num_pck_recebido, num_ultimo_correto=self.count)))   
        self.com.rx.clearBuffer()
        time.sleep(0.5)
        self.flagTimer20  =True

        self.gui.error(num_atual = self.count, num_pacote_de_reenvio = self.count, num_pck_error = self.num_pck_recebido, CRC = self.crc_okay)
        
        # Escreve na documentação
        self.doc.escreve_log(tipo= "ERROR" ,acao = "[ENVIA]", protocolo=6,
                            pacote_enviado = str(self.num_pck_recebido), tam_bytes=0, total_pacotes= self.total_pacotes)

if __name__ == "__main__":
    
    serialName = "COM6"  
    id =  80
    path_arquivo = "arquivos/recebido/recebidaCopia.png"

    servidor = Server(id_servidor = id, serial_name = serialName, path_arquivo = path_arquivo)
    servidor.start()