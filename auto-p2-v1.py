import os
import subprocess
import shutil
import sys
import json

def cargar_configuracion():
    try:
        with open("auto-p2.json", "r") as file:
            configuracion = json.load(file)
            num_servidores = configuracion.get("num_serv", None)
            if num_servidores is None or not isinstance(num_servidores, int) or num_servidores < 1 or num_servidores > 5:
                print("Error: El número de servidores en el archivo de configuración es incorrecto.")
                sys.exit(1)
            return num_servidores
    except FileNotFoundError:
        print("Error: El archivo de configuración 'auto-p2.json' no encontrado.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: El archivo de configuración 'auto-p2.json' no es válido JSON.")
        sys.exit(1)

def crear_escenario():
    # Crear imágenes de diferencias
    subprocess.call(["qemu-img", "create", "-f", "cdps-vm-base-pc1.qcow2", "s1.qcow2"], shell=True)
    subprocess.call(["qemu-img", "create", "-f", "cdps-vm-base-pc1.qcow2", "s2.qcow2"], shell=True)
    subprocess.call(["qemu-img", "create", "-f", "cdps-vm-base-pc1.qcow2", "s3.qcow2"], shell=True)
    subprocess.call(["qemu-img", "create", "-f", "cdps-vm-base-pc1.qcow2", "lb.qcow2"], shell=True)
    subprocess.call(["qemu-img", "create", "-f", "cdps-vm-base-pc1.qcow2", "c1.qcow2"], shell=True)
    subprocess.call(["qemu-img", "create", "-f", "cdps-vm-base-pc1.qcow2", "host.qcow2"], shell=True)

    # Crear especificaciones en XML
    subprocess.call(["cp", "plantilla-vm-pc1.xml", "s1.xml"], shell=True)
    subprocess.call(["cp", "plantilla-vm-pc1.xml", "s2.xml"], shell=True)
    subprocess.call(["cp", "plantilla-vm-pc1.xml", "s3.xml"], shell=True)
    subprocess.call(["cp", "plantilla-vm-pc1.xml", "lb.xml"], shell=True)
    subprocess.call(["cp", "plantilla-vm-pc1.xml", "c1.xml"], shell=True)
    subprocess.call(["cp", "plantilla-vm-pc1.xml", "host.xml"], shell=True)

    # Crear los bridges correspondientes a las dos redes virtuales
    subprocess.call(["sudo", "brctl", "addbr", "LAN1"], shell=True)
    subprocess.call(["sudo", "brctl", "addbr", "LAN2"], shell=True)
    subprocess.call(["sudo", "ifconfig", "LAN1", "up"], shell=True)
    subprocess.call(["sudo", "ifconfig", "LAN2", "up"], shell=True)

    # Arrancar el gestor de máquinas virtuales para monitorizar su arranque
    subprocess.call(["HOME=/mnt/tmp", "sudo", "virt-manager"], shell=True)    

def arrancar_escenario():
    # Arrancar servidor S1
    subprocess.call(["sudo", "virsh", "define", "s1.xml"], shell=True)
    subprocess.call(["sudo", "virsh", "start", "s1"], shell=True)
    subprocess.call(["xterm", "-e", "sudo", "virsh", "console", "s1", "&"], shell=True)
    # Arrancar servidor S2
    subprocess.call(["sudo", "virsh", "define", "s2.xml"], shell=True)
    subprocess.call(["sudo", "virsh", "start", "s2"], shell=True)
    subprocess.call(["xterm", "-e", "sudo", "virsh", "console", "s2", "&"], shell=True)
    # Arrancar servidor S3
    subprocess.call(["sudo", "virsh", "define", "s3.xml"], shell=True)
    subprocess.call(["sudo", "virsh", "start", "s3"], shell=True)
    subprocess.call(["xterm", "-e", "sudo", "virsh", "console", "s3", "&"], shell=True)
    # Arrancar balanceador LB
    subprocess.call(["sudo", "virsh", "define", "lb.xml"], shell=True)
    subprocess.call(["sudo", "virsh", "start", "lb"], shell=True)
    subprocess.call(["xterm", "-e", "sudo", "virsh", "console", "lb", "&"], shell=True)
    # Arrancar cliente C1
    subprocess.call(["sudo", "virsh", "define", "c1.xml"], shell=True)
    subprocess.call(["sudo", "virsh", "start", "c1"], shell=True)
    subprocess.call(["xterm", "-e", "sudo", "virsh", "console", "c1", "&"], shell=True)
    # Arrancar host
    subprocess.call(["sudo", "virsh", "define", "host.xml"], shell=True)
    subprocess.call(["sudo", "virsh", "start", "host"], shell=True)
    subprocess.call(["xterm", "-e", "sudo", "virsh", "console", "host", "&"], shell=True)

def parar_escenario():
    subprocess.call(["sudo", "virsh", "shutdown", "s1"], shell=True)
    subprocess.call(["sudo", "virsh", "shutdown", "s2"], shell=True)
    subprocess.call(["sudo", "virsh", "shutdown", "s3"], shell=True)
    subprocess.call(["sudo", "virsh", "shutdown", "lb"], shell=True)
    subprocess.call(["sudo", "virsh", "shutdown", "c1"], shell=True)
    subprocess.call(["sudo", "virsh", "shutdown", "host"], shell=True)

def liberar_escenario():
    # Destruir servidor S1
    subprocess.call(["sudo", "virsh", "destroy", "s1"], shell=True)
    subprocess.call(["sudo", "rm", "s1.qcow2"], shell=True)
    # Destruir servidor S2
    subprocess.call(["sudo", "virsh", "destroy", "s2"], shell=True)
    subprocess.call(["sudo", "rm", "s2.qcow2"], shell=True)
    # Destruir servidor S3
    subprocess.call(["sudo", "virsh", "destroy", "s3"], shell=True)
    subprocess.call(["sudo", "rm", "s3.qcow2"], shell=True)
    # Destruir balanceador LB
    subprocess.call(["sudo", "virsh", "destroy", "lb"], shell=True)
    subprocess.call(["sudo", "rm", "lb.qcow2"], shell=True)
    # Destruir cliente C1
    subprocess.call(["sudo", "virsh", "destroy", "c1"], shell=True)
    subprocess.call(["sudo", "rm", "c1.qcow2"], shell=True)
    # Destruir host
    subprocess.call(["sudo", "virsh", "destroy", "host"], shell=True)
    subprocess.call(["sudo", "rm", "host.qcow2"], shell=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: auto-p2.py <orden>")
        sys.exit(1)

    orden = sys.argv[1]

    if orden == "crear":
        crear_escenario()
    elif orden == "arrancar":
        arrancar_escenario()
    elif orden == "parar":
        parar_escenario()
    elif orden == "liberar":
        liberar_escenario()
    else:
        print("Orden no reconocida")