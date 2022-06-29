import datetime

class Log():

    def __init__(self, nome, opcao):
        self.nome = nome   
        self.opcao = opcao
        self.log = ''

    def add_to_log(self, acao, tipo, tipo_msm, tam_bytes, pacote_enviado, total_pacotes):
        
        instante = datetime.datetime.now()
        
        self.log+="\n"
        self.log+= "----------- "+str(instante)
        self.log+=" - "
        self.log+=f"{acao} {tipo} -----------"
        self.log+= f"\nTipo: {str(tipo_msm)}\n"
        self.log+= f"Tamanho em bytes: {str(tam_bytes)}\n"
        self.log+=f"°N pacote: {str(pacote_enviado)}\n"
        self.log+=f"Total pacotes: {str(total_pacotes)}\n"
    
    def escreve_log(self, tipo , acao, protocolo, pacote_enviado, tam_bytes, total_pacotes):
        self.add_to_log(acao=acao, tipo = tipo, tipo_msm=protocolo,pacote_enviado=pacote_enviado, tam_bytes=tam_bytes, total_pacotes=total_pacotes)
        
    def cria_log(self):
        with open(f'arquivos/logs/{self.nome}/{self.nome + str(self.opcao)}.txt', 'w') as file:
            file.write(self.log)
        