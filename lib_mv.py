#!/usr/bin/python3
import logging
import subprocess
import os
from lxml import etree
from copy import deepcopy

log = logging.getLogger('auto_p2')
    
class MV:
  def __init__(self, nombre):
    self.nombre = nombre
    log.debug('init MV ' + self.nombre)

  def crear_mv (self, imagen, interfaces_red, router):
    log.debug("crear_mv " + self.nombre)
    # Crear imágenes de diferencias
    subprocess.call(['qemu-img', 'create', '-f', 'qcow2', '-b', imagen, f'{self.nombre}.qcow2'])

    # Crear especificaciones en XML
    subprocess.call(['cp', 'plantilla-vm-pc1.xml', f'{self.nombre}.xml'])

    # Cargamos el fichero xml
    tree = etree.parse(self.nombre + '.xml')
    # Lo imprimimos en pantalla
    print(etree.tounicode(tree, pretty_print=True))
    # Obtenemos el nodo raiz, buscamos la etiqueta 'name' y luego lo cambiamos
    root = tree.getroot()
    name = root.find("name")
    name.text = self.nombre
    # Buscamos el nodo 'source' bajo 'disk' bajo 'devices' con nombre 'file' y lo cambiamos
    source_disk = root.find("./devices/disk/source")
    source_disk.set("file", "/mnt/tmp/" + self.nombre + "/" + self.nombre + ".qcow2")

    # Modificar la etiqueta 'interface' dependiendo de si es el router o no
    if router:
      # Buscar la etiqueta 'interface' y duplicarla
      existing_interface = root.find(".//interface")
      # Modificar el valor del atributo 'source' en el primer nodo 'interface'
      source1 = existing_interface.find(".//source")
      source1.set("bridge", "LAN1")
      # Duplicar la etiqueta 'interface'
      new_interface = deepcopy(existing_interface)
      root.find(".//devices").append(new_interface)             
      # Modificar el valor del atributo 'source' en el segundo nodo 'interface'
      source2 = new_interface.find(".//source")
      source2.set("bridge", "LAN2")
    else:
      # Buscamos el nodo 'source' bajo 'interface' bajo 'devices' con nombre 'file', imprimimos su valor y lo cambiamos
      source_interface = root.find("./devices/interface/source")
      source_interface.set("bridge", interfaces_red)

    # Imprimimos el xml con todos los cambios realizados
    print(etree.tounicode(tree, pretty_print=True))
    # Guardar los cambios realizados
    tree.write(self.nombre + '.xml')

  def arrancar_mv (self):
    log.debug("arrancar_mv " + self.nombre)
    # Arrancar el gestor de máquinas virtuales para monitorizar su arranque
    subprocess.call(['HOME=/mnt/tmp', 'sudo', 'virt-manager'])  
    # Arrancar cada máquina virtual
    subprocess.call(['sudo', 'virsh', 'define', f'{self.nombre}.xml'])
    subprocess.call(['sudo', 'virsh', 'start', f'{self.nombre}'])
    # subprocess.call(["xterm", "-e", "sudo", "virsh", "console", self.nombre, "&"], shell=True)

    # Crear los ficheros de configuración de cada máquina virtual en el host en un directorio temporal
    if self.nombre == 's1':
      contenido = """
        auto lo
        iface lo inet loopback
        
        auto eth0
          iface eth0 inet static
          address 10.11.2.31
          netmask 255.255.255.0
          gateway 10.11.2.1
      """
    elif self.nombre == 's2':
      contenido = """
        auto lo
        iface lo inet loopback
        
        auto eth0
          iface eth0 inet static
          address 10.11.2.32
          netmask 255.255.255.0
          gateway 10.11.2.1
      """
    elif self.nombre == 's3':
      contenido = """
        auto lo
        iface lo inet loopback
        
        auto eth0
          iface eth0 inet static
          address 10.11.2.33
          netmask 255.255.255.0
          gateway 10.11.2.1
      """
    elif self.nombre == 'c1':
      contenido = """
        auto lo
        iface lo inet loopback
        
        auto eth0
          iface eth0 inet static
          address 10.11.1.2
          netmask 255.255.255.0
          gateway 10.11.1.1
      """
    elif self.nombre == 'host':
      contenido = """
        auto lo
        iface lo inet loopback
        
        auto eth0
          iface eth0 inet static
          address 10.11.1.3
          netmask 255.255.255.0
          gateway 10.11.1.1
      """
    # HAY QUE PONER INTERFACES PARA EL ROUTER TAMBIÉN???
     
    # Directorio de trabajo actual
    directorio_trabajo = os.getcwd()
    # Ruta completa al archivo "interfaces"
    ruta_interfaces = os.path.join(directorio_trabajo, "interfaces")
    # Escribir el contenido sobre el archivo "interfaces"
    with open(ruta_interfaces, 'w') as interfaces:
      interfaces.write(contenido)

    # Editar el archivo "hostname" HAY QUE CAMBIARLO
    # subprocess.call(['sudo bash -c "echo ' + f'{self.nombre}' + ' > hostname"'])
    subprocess.call(['sudo', 'bash', '-c', '"echo', f'{self.nombre}', '>', 'hostname"'])

    # Copiar los ficheros de configuración a las máquinas virtuales
    subprocess.call(['sudo', 'virt-copy-in', '-a', f'{self.nombre}.qcow2', 'interfaces', '/etc/network'])
    subprocess.call(['sudo', 'virt-copy-in', '-a', f'{self.nombre}.qcow2', 'hostname', '/etc'])

    # Editar el archivo "hosts"
    subprocess.call(['sudo', 'virt-edit', '-a', f'{self.nombre}.qcow2', '/etc/hosts', '-e', '"s/127.0.1.1.*/127.0.1.1', f'{self.nombre}/"'])

    # Configurar el balanceador de tráfico para que funcione como router al arrancar
    subprocess.call(['sudo', 'virt-edit', '-a', 'lb.qcow2', '/etc/sysctl.conf', '\-e', '"s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/"'])

  def mostrar_consola_mv (self):
    log.debug("mostrar_mv " + self.nombre)
    # Arrancar la consola de la máquina virtual
    subprocess.call(['xterm', '-e', 'sudo', 'virsh', 'console', f'{self.nombre}', '&'])

  def parar_mv (self):
    log.debug("parar_mv " + self.nombre)
    # Detener la máquina virtual
    subprocess.call(['virsh', 'shutdown', f'{self.nombre}'])

  def liberar_mv (self):
    log.debug("liberar_mv " + self.nombre)
    # Liberar y borrar la máquina virtual
    subprocess.call(['virsh', 'destroy', f'{self.nombre}'])

class Red:
  def __init__(self, nombre):
    self.nombre = nombre
    log.debug('init Red ' + self.nombre)

  def crear_red(self):
      log.debug('crear_red ' + self.nombre)
      # Crear los bridges correspondientes a las dos redes virtuales
      subprocess.call(['sudo', 'brctl', 'addbr', 'LAN1'])
      subprocess.call(['sudo', 'brctl', 'addbr', 'LAN2'])
      subprocess.call(['sudo', 'ifconfig', 'LAN1', 'up'])
      subprocess.call(['sudo', 'ifconfig', 'LAN2', 'up'])

  def liberar_red(self):
      log.debug('liberar_red ' + self.nombre)