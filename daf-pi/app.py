from daf_virtual_rasp.com.enquadramento import Enquadramento
from daf_virtual_rasp.com.arq import Arq
from daf_virtual_rasp.com.poller import Poller
from daf_virtual_rasp.com.enq_enum import TIPO_t
from daf_virtual_rasp.daf.daf import DAF
import sys, time, os
import serial


# define parametros das camadas ARQ e Enquadramento
max_tentativas_arq = 3
timeout_enq = 0.5
timeout_arq = 2

# obtém porta serial 
ser = serial.Serial(
            port='/dev/pts/0',
            baudrate = 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout= None
        )

ser.flush()


# cria os objetos das camadas ARQ, Enquadramento e DAF
e = Enquadramento(ser, timeout_enq)
a = Arq(max_tentativas_arq, timeout_arq)
daf = DAF()

# define organização das subcamadas
daf.set_inferior(a)
a.set_superior(daf)
a.set_inferior(e)
e.set_superior(a)

# despacha as camadas
pol = Poller()
pol.adiciona(daf)
pol.adiciona(e)
pol.adiciona(a)
pol.despache()