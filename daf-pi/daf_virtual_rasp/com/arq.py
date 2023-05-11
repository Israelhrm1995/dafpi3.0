import time
from daf_virtual_rasp.com.arq_enum import ESTADO_t, CONTROLE_t
from daf_virtual_rasp.com.layer import Layer
import sys
from daf_virtual_rasp.com.enq_enum import TIPO_t
from typing import Union

class Arq(Layer):

    def __init__(self, max_tentativas:int, timeout:int):
        self.seq_rx = 0    # Sequência de recepção
        self.seq_tx = 0    # Sequência de transmissão
        self.tipo = 0       # Tipo da mensagem atribuída no Enquadramento
        self.limite_tentativas = max_tentativas
        self.tentativas = 0  # Número de tentativas
        self.tout = timeout
        self.estado = ESTADO_t.IDLE.value        # Estado inicial da FSM
        self.msg = bytearray()
        self.superior = None    # Camada API-PAF
        self.inferior = None    # Camada Enquadramento
        self.campo_dados = bytearray()
        self.comando = None

        Layer.__init__(self, None, timeout)

        self.enable()
        self.disable_timeout()          # Desativa o Timeout

    def handle_fsm(self, campo_controle:int, campo_dados:Union[bytes, int]):
        """ Máquina de estado que trata o envio e recepção de mensagens

        Args:
            campo_dados (bytes, int): mensagem recebida.
            campo_controle (int): campo controle a ser verificado.
        """
       
        self.campo_dados = campo_dados
        if self.estado == ESTADO_t.IDLE.value:
            self.__idle(campo_controle, campo_dados)
        else:
            self.__wait(campo_controle, campo_dados)

    def __idle(self, campo_controle:int, campo_dados:bytes):
        """ Estado inicial da camada Garantia de Entrega.

        Args:
            campo_controle (int): conteúdo do campo Controle
            campo_dados (int, bytes): conteúdo do campo Dados
        """
        
        # Caso tenha recebido dados da camada superior envia uma nova mensagem
        if campo_controle is None:
            if (self.seq_tx == 1):
                campo_controle = CONTROLE_t.DATA_1.value
            else:
                campo_controle = CONTROLE_t.DATA_0.value

            self.monta_quadro(campo_controle, campo_dados)
            self.superior.disable_all_superior()
            print("DAF enviando:", self.msg, "\n")
            self.inferior.envia(self.msg, self.tipo)  # Envia para a subcamada inferior (Enquadramento)
            self.tentativas = 0
            self.recarrega_timeout(self.tout)
            self.estado = ESTADO_t.WAIT.value
        else:
            # Recebe uma nova mensagem e envia um ACK
            if ((self.seq_rx == 1) and (campo_controle == CONTROLE_t.DATA_1.value)) or ((self.seq_rx == 0) and (campo_controle == CONTROLE_t.DATA_0.value)):
                self.estado = ESTADO_t.IDLE.value
              
                self.__ack(False)
                if self.inferior.is_ping():
                    if (self.seq_tx == 1):
                        campo_controle = CONTROLE_t.DATA_1.value
                    else:
                        campo_controle = CONTROLE_t.DATA_0.value
                    self.monta_quadro(campo_controle, self.campo_dados)
                    self.estado = ESTADO_t.WAIT.value
                    self.inferior.envia(self.msg, TIPO_t.PING.value) 
                else:
                    print("Recebido pelo DAF:", self.campo_dados, "\n")
                    self.superior.notifica(self.comando, self.campo_dados) 

            # Recebe uma mensagem já recebida e reenvia um ACK
            elif ((self.seq_rx == 0) and (campo_controle == CONTROLE_t.DATA_1.value)) or ((self.seq_rx == 1) and (campo_controle == CONTROLE_t.DATA_0.value)):
                self.estado = ESTADO_t.IDLE.value
                self.__ack(True)

    def __wait(self, campo_controle:int, campo_dados:bytes):
        """ Estado onde é aguardado a chegada de um ACK.

        Args:
            campo_controle (int): conteúdo do campo Controle
            campo_dados (int, bytes): conteúdo do campo Dados
        """
        if campo_controle is not None:
            # Se recebeu o ACK correto, está apto a enviar uma nova mensagem
            if((self.seq_tx == 1) and (campo_controle == CONTROLE_t.ACK_1.value)) or ((self.seq_tx == 0) and (campo_controle == CONTROLE_t.ACK_0.value)):
                self.seq_tx = not self.seq_tx
                self.estado = ESTADO_t.IDLE.value
                self.disable_timeout()

            # Recebe uma nova mensagem e envia um ACK
            elif ((self.seq_rx == 1) and (campo_controle == CONTROLE_t.DATA_1.value)) or ((self.seq_rx == 0) and (campo_controle == CONTROLE_t.DATA_0.value)):
                 self.estado = ESTADO_t.WAIT.value
                 self.__ack(False)
                 print("Recebido pelo DAF:", self.campo_dados, "\n")
                 self.superior.notifica(self.comando, self.campo_dados)

            # Recebe uma mensagem já recebida e reenvia um ACK
            elif ((self.seq_rx == 0) and (campo_controle == CONTROLE_t.DATA_1.value)) or ((self.seq_rx == 1) and (campo_controle == CONTROLE_t.DATA_0.value)):
                self.estado = ESTADO_t.WAIT.value
                print("Recebido pelo DAF:", self.campo_dados, "\n")
                self.__ack(True)

            # Recebeu o ACK errado, reenvia a mensagem
            elif((self.seq_tx == 1) and (campo_controle == CONTROLE_t.ACK_0.value)) or ((self.seq_tx == 0) and (campo_controle == CONTROLE_t.ACK_1.value)):
                if (self.tentativas == self.limite_tentativas):
                    self.tentativas = 0
                    self.estado = ESTADO_t.IDLE.value
                    self.disable_timeout()
                else:
                    self.__reenvia()             

    def monta_quadro(self, campo_controle:int, campo_dados:Union[int, bytes]):
        """ Monta o quadro com as características do ARQ_MAC.

        Args:
            campo_controle (int): conteúdo do campo Controle
            campo_dados (int, bytes): conteúdo do campo Dados
        """
        self.msg.clear()
        self.msg.append(campo_controle)
        self.msg = self.msg + campo_dados
    
    def __ack(self, reenvio:bool):
        """ Define o cabeçalho de controle para o ACK.

        Args:
            reenvio (bool): garante que o ACK correto seja enviado,
                            se é um reenvio ou não.
        """
        ack = bytearray()
        seq_envio = self.seq_rx

        # Corrige o número de sequência para o reenvio de ACK
        if(reenvio):
            seq_envio = not self.seq_rx

        if (seq_envio == 1):
            controle = CONTROLE_t.ACK_1.value
        else:
            controle = CONTROLE_t.ACK_0.value
        ack.append(controle)

        # Altera o número de sequência de rx quando não for um reenvio de ACK
        if (not reenvio):
            self.seq_rx = not self.seq_rx
        self.inferior.envia(ack, TIPO_t.ENVIARMSG.value) # Envia para a subcamada inferior (Enquadramento)

    def __reenvia(self):
        '''
        Realiza o reenvio da mensagem em caso
        de Timeout ou de ACK incorreto
        '''
        print("DAF reenviando:", self.msg, "\n")
        self.inferior.envia(self.msg, self.tipo)
        self.tentativas += 1
        self.recarrega_timeout(self.tout)

    def handle(self):
        pass

    def handle_timeout(self):
        """ Monitora o timeout e reenvia a mensagem quando necessário.
        """
        if self.estado == ESTADO_t.WAIT.value:
             # Caso atinja o limite de tentativas de reenvio, declara ERRO FATAL
            if (self.tentativas == self.limite_tentativas):
                self.tentativas = 0
                self.disable_timeout()
                self.estado = ESTADO_t.IDLE.value
            else:
                self.estado = ESTADO_t.WAIT.value
                self.__reenvia()

    def recarrega_timeout(self, timeout:int):
        """ Define um novo valor de timeout e o recarrega

        Args:
            timeout (int): tempo de espera.
        """
        self.timeout = timeout
        self.enable_timeout()
        self.reload_timeout()

    def envia(self, data:Union[bytes, int], tipo:int):
        """ Trata mensagens vindas da subcamada superior (API-DAF).

        Args:
            data (bytes, int): mensagem a ser enviada.
            tipo (int): tipo da mensagem a ser enviada.
        """
        self.tipo = tipo
        self.handle_fsm(None, data)

    def notifica(self,  campo_controle:int, campo_dados:Union[bytes, int], campo_tipo):
        """ Trata mensagens vindas da subcamada inferior (Enquadramento)

        Args:
            campo_controle (int): byte de controle
            campo_dados (int): dados da mensagem
            tipo (int): campo tipo
        """
        self.comando = campo_tipo
        self.handle_fsm(campo_controle, campo_dados)
    
    def retorna_dados(self):
        return self.campo_dados