import logging, sys, subprocess, json
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

def load_configuration():
    # Cargar la configuración desde auto-p2.json
    with open('auto-p2.json') as config_file:
            config_data = json.load(config_file)
            return config_data["num_serv"]

def main():
    num_servidores = load_configuration()
        
    # Crear las clases de las MV
    c1 = MV("c1")
    host = MV("host")
    lb = MV("lb")
    red = Red("red")

    # Establecer la posición de la orden en la línea de argumentos
    orden = sys.argv[1]

    if orden == "crear":
        # Crear la red
        red.crear_red()
        # Crear los servidores
        for i in range(num_servidores):
            s = MV(f's{i + 1}')
            s.crear_mv("cdps-vm-base-pc1.qcow2", "LAN2", False)
        # Crear el resto de máquinas virtuales
        c1.crear_mv("cdps-vm-base-pc1.qcow2", "LAN1", False)
        host.crear_mv("cdps-vm-base-pc1.qcow2", "LAN1", False)
        lb.crear_mv("cdps-vm-base-pc1.qcow2", "null", True)

    elif orden == "arrancar":
        if len(sys.argv) < 3:
            # Arrancar los servidores
            for i in range(num_servidores):
                s = MV(f's{i + 1}')
                s.arrancar_mv()
                s.mostrar_consola_mv()
            # Arrancar el resto de máquinas virtuales
            c1.arrancar_mv()
            c1.mostrar_consola_mv()
            host.arrancar_mv()
            host.mostrar_consola_mv()
            lb.arrancar_mv()
            lb.mostrar_consola_mv()
            return
        else:
            nombre_mv = sys.argv[2]
            mv = MV(nombre_mv)
            mv.arrancar_mv()
            mv.mostrar_consola_mv()

    elif orden == "parar":
        if len(sys.argv) < 3:
            # Parar los servidores
            for i in range(num_servidores):
                s = MV(f's{i + 1}')
                s.parar_mv()
            # Parar el resto de máquinas virtuales
            c1.parar_mv()
            host.parar_mv()
            lb.parar_mv()
            return
        else:
            nombre_mv = sys.argv[2]
            mv = MV(nombre_mv)
            mv.parar_mv()

    elif orden == "liberar":
        # Liberar los servidores
        for i in range(num_servidores):
            s = MV(f's{i + 1}')
            s.liberar_mv()
        # Liberar el resto de máquinas virtuales
        c1.liberar_mv()
        host.liberar_mv()
        lb.liberar_mv()
        # Liberar la red
        red.liberar_red()

    elif orden == "monitor":
        # Monitorizar el estado de las máquinas virtuales
        subprocess.call(['sudo', 'virsh', 'list', '--all'])
        
    else:
        print(f"Orden no reconocida: {orden}")

if __name__ == "__main__":
    main()