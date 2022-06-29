from re import S
import sys

from colorama import  init, Fore, Style

class Display():

    def __init__(self, name):
        self.name = name
        init(convert=True)

    def start(self):
        print()
        print("--------------------------------------------------------")
        print('\n--------------- SELECIONE A ACAO DESEJADA --------------\n')
        print("--------------------------------------------------------")
        print()
        print('(1) - Transmissão sem intercorrência. \n')
        print('(2) - Error na ordem de envio no número de pacote. \n')
        print('(3) - Transmissao com ausencia de resposta de handShake. [TIME OUT - MANUAL]. \n')
        print('(4) - Transmissao com ausencia de resposta do pacote recebido pelo servidor. [TIME OUT] \n')
        print('(5) - Transmissao com retirada de fio [MANUAL] \n')
        print('(6) - Error CRC \n')
        opcao = input('\nOpção selecionada:\t')

        return opcao

    def conectado(self):

        print()
        print(Fore.GREEN+Style.BRIGHT+"--------------------------------------------------------")
        print("-------------CONEXAO REALIZADA COM SUCESSO!-------------")
        print("--------------------------------------------------------"+Style.RESET_ALL)
        print()

    def HandShake(self):
        print()
        print("--------------------------------------------------------")
        print("                       HANDSHAKE ...                    ") 
        print("--------------------------------------------------------")
        print()

    def inicia_envio(self , num_pacotes , tam_pacote_resto):
        
        print("\n>> [CLIENT] HANDSHAKE REALIZADO COM SUCESSO !\n")

        print(Fore.LIGHTBLUE_EX +Style.BRIGHT+"--------------------------------------------------------")
        print("               COMEÇANDO ENVIO DE PACOTES ...           ") 
        print("--------------------------------------------------------"+Style.RESET_ALL)

        print(f"\n>> [{self.name}] Total de pacotes que serão enviados: {num_pacotes}\n") 
        print(f"\n>> [{self.name}] Com {tam_pacote_resto} bytes no pacote resto.\n\n")

    def error(self, num_atual, num_pacote_de_reenvio, num_pck_error, CRC = True):

        if(not CRC):
            print()
            print(Fore.RED +Style.BRIGHT+"--------------------------------------------------------")
            print(f"              Pacote N° {num_pck_error} - ERROR CRC              ") 
            print("--------------------------------------------------------"+ Style.RESET_ALL)  
        else:
            print(Fore.RED +Style.BRIGHT+"\n\n--------------------------------------------------------")
            print(f"                    Pacote N° {num_pck_error} - ERROR            ") 
            print("--------------------------------------------------------"+Style.RESET_ALL)

        if(self.name == 'CLIENT'):
            print(f"\n>> [{self.name}] Pacote atual : {num_atual}°\n")

        print(f"\n>> [{self.name}] N° pacote de reenvio : {num_pacote_de_reenvio}°\n" )

    def error_nao_tratado(self):

        print(Fore.RED +Style.BRIGHT+"--------------------------------------------------------")
        print("                       ? ERROR ?                      ") 
        print("--------------------------------------------------------"+ Style.RESET_ALL)    

    def esperando(self):
        print()
        print(Fore.LIGHTBLUE_EX + Style.BRIGHT + "\n--------------- BUSCANDO RECONEXÃO ... -----------------\n"+Style.RESET_ALL)
        print()

    def indica_progresso(self):
        print()
        print("                      PROGRESSO                        \n")
        print()

    def recebe_transmissao(self):

        print(Fore.LIGHTBLUE_EX +Style.BRIGHT+"--------------------------------------------------------")
        print("                RECEBENDO MENSAGEM ...                 ") 
        print("--------------------------------------------------------"+ Style.RESET_ALL)

    def time_out(self):
        print()
        print(Fore.RED + Style.BRIGHT +"--------------------------------------------------------")
        print("                       TIME OUT                         ") 
        print("--------------------------------------------------------" + Style.RESET_ALL)
        print()


    def progress(self, count, total, suffix=''):

        sys.stdout.flush()

        bar_len = 50
        filled_len = int(round(bar_len * (count) / float(total)))

        percents = round(100.0 * (count-1) / float(total), 1)
        bar = '#' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))

    def encerra_conexao(self):
        print(Fore.GREEN+Style.BRIGHT+"\n\n--------------------------------------------------------")
        print("                 Comunicacao encerrada                  ")
        print("--------------------------------------------------------\n"+ Style.RESET_ALL)