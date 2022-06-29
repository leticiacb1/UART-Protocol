from crccheck.crc import Crc16

class Datagrama():

    def __init__(self):

        # Configurações iniciais.
        self.tam_header = 10
        self.tam_EOP = 4

    def cria_header(self, tipo=0 , total_pacotes = 0 ,  
                    num_pacote = 0, h5 = 0, 
                    num_error=0 , num_ultimo = 0 , opcao = 0, data_crc = None, crc_error = False):
    
        header = b''
        header += (tipo).to_bytes(1, byteorder='big')                    # (0) Indicar tipo    (1,2,3,4,5,6)                                   
        header += (int(opcao)).to_bytes(1,byteorder='big')               # (1) UTILIZADO APENAS PARA INDICAR OPCAO SELECIONADA PELO CLIENT NO HANDSHAKE
        header += (0).to_bytes(1, byteorder='big')                       # (2) 
        header += (total_pacotes).to_bytes(1, byteorder='big')           # (3) Total de Pacotes
        header += (num_pacote).to_bytes(1, byteorder='big')              # (4) Numero do pacote sendo enviado   ou  ID do Servidor (HandShake) .                           
        header += (h5).to_bytes(1, byteorder='big')                      # (5) handshake - (ID) ou  Dados - (TamPayload)
        header += (num_error).to_bytes(1, byteorder='big')               # (6) Pacote solicitado para recomeço quando há error no envio.
        header += (num_ultimo).to_bytes(1,byteorder='big')               # (7) Numero do ultimo pacote enviado correto.
        
        # Acrescentando CRC - PROJETO 5
        if(crc_error):
            # Provocando error no CRC
            header += (2).to_bytes(2, byteorder='big')

        elif(data_crc != None):
            header += self.calcula_crc(data_crc)   
        else:
            header += (0).to_bytes(2, byteorder='big')

        return header

    def cria_payload(self, vazio =False, num_pacote = None, 
                    pacote_Resto = False , arquivo_de_envio = None):
    
        if(vazio):
            payload = b''                                                                    # PayLoad de HandShake ou de resposta do servidor
        else:
            if(not pacote_Resto):
                # Cortando msm para envio:
                payload = arquivo_de_envio[(num_pacote-1)*114:114*(num_pacote)]              # Payload de envio de dados
            else:
                payload = arquivo_de_envio[(num_pacote-1)*114:]                              # Payload do pacote resto.
        
        return payload

    def calcula_crc(self, data_crc):
        crc = Crc16.calc(data_crc)
        return  (crc).to_bytes(2, byteorder='big') 

    def cria_EOP(self):
        EOP = (0xAA).to_bytes(1, byteorder = 'big') + (0xBB).to_bytes(1, byteorder = 'big') + (0xCC).to_bytes(1, byteorder = 'big') +  (0xDD).to_bytes(1, byteorder = 'big')
        return EOP

    
    def handShake(self, total_pacotes, id_arquivo , id , opcao):
        return self.cria_header(tipo = 1, total_pacotes = total_pacotes , num_pacote = id ,h5 = id_arquivo , opcao= opcao) + self.cria_payload(vazio=True) + self.cria_EOP()

    def resposta_handshake(self):
        '''
        Resposta do Servidor ao HandShake.
        '''

        return self.cria_header(tipo=2) + self.cria_payload(vazio=True) + self.cria_EOP()
    
    def msm_time_out(self):

        return self.cria_header(tipo=5) + self.cria_payload(vazio=True) + self.cria_EOP()