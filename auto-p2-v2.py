#!/usr/bin/env python

from lib_mv import MV
import logging, sys

def init_log():
    # Creacion y configuracion del logger
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('auto_p2')
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.propagate = False

def pause():
    programPause = input("Press the <ENTER> key to continue...")

# Main
init_log()
print('CDPS - mensaje info1')

# Ejemplo de creacion de una maquina virtual
s1 = MV('s1')
pause()
s1.crear_mv('cdps-vm.qcow2', 'if1', False )
pause()
s1.arrancar_mv()
pause()
s1.parar_mv()
pause()
s1.liberar_mv()