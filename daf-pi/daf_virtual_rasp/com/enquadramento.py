import time
from daf_virtual_rasp.com.layer import Layer
from daf_virtual_rasp.com.enq_enum import ESTADO_t, TAMANHO_t, TIPO_t
import serial
from typing import Union

class Enquadramento(Layer):
    
    def __init__(self, fd, timeout):
        self.estado = ESTADO_t.IDLE.value        # Estado inicial da FSM
        self.msg = bytearray()

        self.tout = timeout
        self.superior = None        # Camada de Garantia de Entrega (ARQ)
        self.inferior = None
        self.ping_bool = False      # Identifica se comando recebido é do tipo Ping
        self.tamanho_comando = 0    # Quantidade de bytes do campo Tamanho
        self.valor_tamanho = 0      # Valor que o campo Tamanho representa

        self.campo_tamanho = bytearray()
        self.campo_tipo = 0
        self.campo_controle = 0
        self.campo_dados = bytearray()
        self.ser = fd

        Layer.__init__(self, fd, timeout)

        self.enable()                   # Ativa o monitoramento do objeto
        self.disable_timeout()          # Desativa o Timeout

    def handle(self):
        """ Monitora a serial.
        """
        byte_lido = self.ser.read(1)
        self.handle_fsm(byte_lido)

    def handle_timeout(self):
        self.__zera_variaveis()
        self.estado = ESTADO_t.IDLE.value
        self.disable_timeout()



    def handle_fsm(self, byte:bytes):
        """ Máquina de estado que trata um byte recebido.

        Args:
            byte (bytes): byte recebido a ser tratado.
        """
        if self.estado == ESTADO_t.IDLE.value:
            self.__idle(byte)
        elif self.estado == ESTADO_t.RX_TAMANHO.value:
            self.__rx_tamanho(byte)
        else:
            self.__rx_dado(byte)

    def __idle(self, byte:bytes):
        """ Estado inicial de transmissão e para recepção da Garantia de Entrega.

        Args:
            byte (bytes): byte a ser tratado.
        """
        if byte == TIPO_t.ENVIARMSG.value:
            self.campo_tipo = byte
            self.tamanho_comando = TAMANHO_t.TAM_2.value
            self.recarrega_timeout(self.tout)
            self.estado = ESTADO_t.RX_TAMANHO.value
        elif byte == TIPO_t.ENVIARBINARIO.value:
            self.campo_tipo = byte
            self.tamanho_comando = TAMANHO_t.TAM_4.value
            self.recarrega_timeout(self.tout)
            self.estado = ESTADO_t.RX_TAMANHO.value
        elif byte == TIPO_t.PING.value:
            self.campo_tipo = byte
            self.tamanho_comando = TAMANHO_t.TAM_2.value
            self.recarrega_timeout(self.tout)
            self.ping_bool = True
            self.estado = ESTADO_t.RX_TAMANHO.value
        else:
            pass

    def __rx_tamanho(self, byte:bytes):
        """ Estado de recepção do campo Tamanho

        Args:
            byte (bytes): byte a ser tratado.
        """

        if len(self.campo_tamanho) < self.tamanho_comando -1:
            self.campo_tamanho += byte
            self.estado = ESTADO_t.RX_TAMANHO.value
            self.recarrega_timeout(self.tout)

        elif len(self.campo_tamanho) == self.tamanho_comando -1:
            self.campo_tamanho += byte
            self.valor_tamanho = self.__extrai_tamanho(self.campo_tamanho)
            self.estado = ESTADO_t.RX_DADO.value
            self.recarrega_timeout(self.tout)

    def __extrai_tamanho(self, tamanho:int):
        """ Extrai o valor do campo Tamanho

        Args:
            tamanho (int): campo Tamanho
        Returns:
            [int]: valor do campo Tamanho
        """
        return int.from_bytes(tamanho, "big")

    def __rx_dado(self, byte:bytes):
        """ Estado de recepção do campo Dados

        Args:
            byte (bytes): byte a ser tratado.
        """

        if len(self.campo_dados) < self.valor_tamanho - 1:
            self.campo_dados += byte
            self.recarrega_timeout(self.tout)
            self.estado = ESTADO_t.RX_DADO.value
        elif len(self.campo_dados) == self.valor_tamanho -1:
            self.campo_dados += byte
            self.estado = ESTADO_t.IDLE.value
            self.superior.notifica(self.campo_dados[0], self.campo_dados[1:],self.campo_tipo)
            self.disable_timeout()
            self.__zera_variaveis()


    def __zera_variaveis(self):
        """ Reincia algumas variáveis do protocolo.
        """
        self.tamanho_comando = 0
        self.valor_tamanho = 0

        self.campo_tamanho.clear()
        self.campo_controle = 0
        self.campo_dados.clear()

    def __enviar_mensagem(self, dados:str):
        """ Cria e envia um comando do tipo enviarMensagem pela serial

        Args:
            dados (bytes): campo Dados do comando
        """
        #dados = dados.encode()
        quadro = self.__monta_quadro(TIPO_t.ENVIARMSG.value, TAMANHO_t.TAM_2.value, dados)
        self.__escreve_serial(quadro)
        self.utima_mensagem = quadro
        self.__reset_variaveis()
        return quadro

    def __enviar_binario(self, dados:bytes):
        """ Cria e envia um comando do tipo enviar_binario pela serial

        Args:
            dados (bytes): campo Dados do comando
        """
        quadro = self.__monta_quadro(TIPO_t.ENVIARBINARIO.value, TAMANHO_t.TAM_4.value, dados)
        self.__escreve_serial(quadro)
        self.utima_mensagem = quadro
        self.__reset_variaveis()
        return quadro

    def __ping(self, dados:bytes):
        """ Cria e envia um comando do tipo ping pela serial

        Args:
            dados (bytes): campo Dados do comando
        """
        quadro = self.__monta_quadro(TIPO_t.PING.value, TAMANHO_t.TAM_2.value, dados)
        self.__escreve_serial(quadro)
        self.utima_mensagem = quadro
        self.ping_bool = False
        self.__reset_variaveis()
        return quadro
    
    def __monta_quadro(self, tipo:int, id_tamanho:int, dados:Union[bytes,int]):
        """ Realiza a montagem de um quadro.

        Args:
            tipo (int): tipo do comando
            id_tamanho (int): tamanho do campo Dados
            dados (int, bytes): conteúdo do campo Dados
        
        Returns:
            [bytes]: retorna o quadro de um comando
        """
        quadro = bytearray()
        quadro += tipo
        # Verifica o tamanho dos Dados
        if type(dados) is int:
            tamanho_dados = (len(str(dados)))
        else: 
            tamanho_dados =  (len(dados))

        # Valida tamanho do campo Dados e o converte para o campo Tamanho
        if id_tamanho == TAMANHO_t.TAM_2.value and tamanho_dados <= 65535:
            tamanhoBytes = tamanho_dados.to_bytes(2, 'big')
            for i in tamanhoBytes:
                quadro.append(i)

        elif id_tamanho == TAMANHO_t.TAM_4.value and tamanho_dados <= 4294967295:
            tamanhoBytes = tamanho_dados.to_bytes(4, 'big')
            for i in tamanhoBytes:
                quadro.append(i)
        else:
            pass

        if type(dados) is int:
            quadro.append(dados)
        else: 
            for i in dados:
                quadro.append(i)
        return quadro

    def envia(self, data:Union[bytes, int], tipo:int):
        """ Trata mensagens vindas da subcamada superior (ARQ).

        Args:
            data (bytes, int): mensagem a ser enviada.
            tipo (int): tipo da mensagem a ser enviada.
        """
        if tipo == TIPO_t.ENVIARMSG.value:
            self.__enviar_mensagem(data)
        elif tipo == TIPO_t.ENVIARBINARIO.value:
            self.__enviar_binario(data)
        elif tipo == TIPO_t.PING.value:
            self.__ping(data)

    def notifica(self, data):
        pass

    def __escreve_serial(self, dados:bytes):
        """ Envia uma sequência de bytes pelo barramento serial.

        Args:
            dados (bytes): sequência de bytes que será enviada pelo barramento serial.
        """
       
        self.ser.write(dados)
    
    def __reset_variaveis(self):
        """ Restaura todas as variáveis utilizadas durante
        o procediemento de leitura do barramento serial.
        """
        self.tipo = 0
        self.tamanho = 0
        self.tamanho_id = 0
        self.is_erro = False
        self.mensagem = bytearray()
        #self.dados = bytearray()
        self.count = 0
    
    def recarrega_timeout(self, timeout:int):
        """ Define um novo valor de timeout e o recarrega

        Args:
            timeout (int): tempo de espera.
        """
        self.base_timeout = timeout
        self.enable_timeout()
        self.reload_timeout()

    def get_tipo(self):
        return self.campo_tipo
    
    def is_ping(self):
        return self.ping_bool