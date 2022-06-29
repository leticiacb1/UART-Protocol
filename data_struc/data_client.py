from data_struc.datagrama import *

class DataClient(Datagrama):

    def __init__(self):
        super().__init__()

    def numero_de_pacotes(self, total_bytes):
        ''' 
        Recorta mensagem que sera enviada pelo cliente. 
        Retornanodo quantidade de pacotes totais que serão enviados e a existencia ou não de um pacote "resto".
        '''
        if(total_bytes <= 114):
            return [1, 0]

        num_pacotes = total_bytes//114

        if(total_bytes%114 == 0):
            return [num_pacotes, 0]                           # num_pacotes , Sem pacote "RESTO"
        else: 
            return [num_pacotes + 1, total_bytes%114]         # num_pacotes , Tamanho do pacote "RESTO"

    def envia_dados(self, numero_pck, total_pacotes, tam_payload, resto, mensagem, crc_error):

        EOP = self.cria_EOP()
        payload = self.cria_payload(num_pacote = numero_pck,  arquivo_de_envio = mensagem, pacote_Resto= resto)
        header = self.cria_header(tipo=3, total_pacotes=total_pacotes, num_pacote=numero_pck, h5=tam_payload, data_crc = payload, crc_error = crc_error)
        
        return header + payload + EOP
