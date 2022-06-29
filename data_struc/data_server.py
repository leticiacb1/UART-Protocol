from data_struc.datagrama import *

class DataServer(Datagrama):

    def __init__(self):
        super().__init__()

    def verifica_crc(self, crc, data):
        
        crc_calculado = self.calcula_crc(data)
        
        if(crc_calculado != crc):
            return False
        
        return True

    def error(self, num_error,num_ultimo_correto):
        header = self.cria_header(tipo=6, num_error = num_error, num_ultimo=num_ultimo_correto)
        return header + self.cria_payload(vazio = True) + self.cria_EOP()

    def tudo_okay(self, ultimo_pck_correto):
        '''
        Resposta do Servirdor comunicando que não há erro de transmissão.
        '''
        header = self.cria_header(tipo=4 , num_ultimo=ultimo_pck_correto)
        payload = self.cria_payload(vazio=True)
        EOP = self.cria_EOP()

        return header + payload + EOP    