import logging, sys
from lib_mv import MV, Red

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

def main():
    orden = sys.argv[1]

    # Crear las clases MV
    s1 = MV("s1")
    s2 = MV("s2")
    s3 = MV("s3")
    c1 = MV("c1")
    host = MV("host")
    lb = MV("lb")
    red = Red("red")

    if orden == "crear":
        # Realizar operaciones relacionadas con la creación de máquinas virtuales y redes
        red.crear_red()
        s1.crear_mv("cdps-vm-base-pc1.qcow2", "LAN2", False)
        s2.crear_mv("cdps-vm-base-pc1.qcow2", "LAN2", False)
        s3.crear_mv("cdps-vm-base-pc1.qcow2", "LAN2", False)
        c1.crear_mv("cdps-vm-base-pc1.qcow2", "LAN1", False)
        host.crear_mv("cdps-vm-base-pc1.qcow2", "LAN1", False)
        lb.crear_mv("cdps-vm-base-pc1.qcow2", "null", True)

    elif orden == "arrancar":
        if len(sys.argv) < 3:
            # Realizar operaciones relacionadas con el arranque de máquinas virtuales
            s1.arrancar_mv()
            s2.arrancar_mv()
            s3.arrancar_mv()
            c1.arrancar_mv()
            host.arrancar_mv()
            lb.arrancar_mv()
            return
        else:
            nombre_mv = sys.argv[2]
            mv = MV(nombre_mv)
            mv.arrancar_mv()

    elif orden == "parar":
        if len(sys.argv) < 3:
            # Realizar operaciones relacionadas con el paro de máquinas virtuales
            s1.parar_mv()
            s2.parar_mv()
            s3.parar_mv()
            c1.parar_mv()
            host.parar_mv()
            lb.parar_mv()
            return
        else:
            nombre_mv = sys.argv[2]
            mv = MV(nombre_mv)
            mv.parar_mv()

    elif orden == "liberar":
        # Realizar operaciones relacionadas con la liberación de recursos
        s1.liberar_mv()
        s2.liberar_mv()
        s3.liberar_mv()
        c1.liberar_mv()
        host.liberar_mv()
        lb.liberar_mv()
        red.liberar_red()
        
    else:
        print(f"Orden no reconocida: {orden}")

if __name__ == "__main__":
    main()