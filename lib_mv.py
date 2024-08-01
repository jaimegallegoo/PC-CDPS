#!/usr/bin/python3

# GRUPO 27
# Jaime Gallego Chillón
# Marta Volpini López

import logging, subprocess, os, getpass
from lxml import etree
from copy import deepcopy

log = logging.getLogger('auto_p2')
    
class MV:
  def __init__(self, nombre):
    self.nombre = nombre
    self.usuario = getpass.getuser()
    log.debug('init MV ' + self.nombre)

  # FUNCIÓN PARA CREAR CADA MÁQUINA VIRTUAL
  def crear_mv (self, imagen, interfaces_red, router):
    log.debug("crear_mv " + self.nombre)
    # Crear imágenes de diferencias
    subprocess.call(['qemu-img', 'create', '-f', 'qcow2', '-b', imagen, f'{self.nombre}.qcow2'])
    # Crear especificaciones en XML
    subprocess.call(['cp', 'plantilla-vm-pc1.xml', f'{self.nombre}.xml'])
    
    # Cargamos el fichero xml
    tree = etree.parse(self.nombre + '.xml')
    # Obtenemos el nodo raiz, buscamos la etiqueta 'name' y luego lo cambiamos
    root = tree.getroot()
    name = root.find("name")
    name.text = self.nombre
    # Buscamos el nodo 'source' bajo 'disk' bajo 'devices' con nombre 'file' y lo cambiamos
    source_disk = root.find("./devices/disk/source")
    source_disk.set("file", "/mnt/tmp/" + self.usuario + "/" + self.nombre + ".qcow2")

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
    # Guardar los cambios realizados
    tree.write(self.nombre + '.xml')

  # FUNCIÓN PARA ARRANCAR CADA MÁQUINA VIRTUAL
  def arrancar_mv (self):
    log.debug("arrancar_mv " + self.nombre)
    # Crear el contenido de interfaces dependiendo de la máquina virtual
    if self.nombre == 's1':
      contenido_interfaces = """
      auto lo
      iface lo inet loopback
      
      auto eth0
        iface eth0 inet static
        address 10.11.2.31
        netmask 255.255.255.0
        gateway 10.11.2.1
      """
    elif self.nombre == 's2':
      contenido_interfaces = """
      auto lo
      iface lo inet loopback
      
      auto eth0
        iface eth0 inet static
        address 10.11.2.32
        netmask 255.255.255.0
        gateway 10.11.2.1
      """
    elif self.nombre == 's3':
      contenido_interfaces = """
      auto lo
      iface lo inet loopback
      
      auto eth0
        iface eth0 inet static
        address 10.11.2.33
        netmask 255.255.255.0
        gateway 10.11.2.1
      """
    elif self.nombre == 's4':
      contenido_interfaces = """
      auto lo
      iface lo inet loopback
      
      auto eth0
        iface eth0 inet static
        address 10.11.2.34
        netmask 255.255.255.0
        gateway 10.11.2.1
      """
    elif self.nombre == 's5':
      contenido_interfaces = """
      auto lo
      iface lo inet loopback
      
      auto eth0
        iface eth0 inet static
        address 10.11.2.35
        netmask 255.255.255.0
        gateway 10.11.2.1
      """
    elif self.nombre == 'c1':
      contenido_interfaces = """
      auto lo
      iface lo inet loopback
      
      auto eth0
        iface eth0 inet static
        address 10.11.1.2
        netmask 255.255.255.0
        gateway 10.11.1.1
      """
    elif self.nombre == 'host':
      contenido_interfaces = """
      auto lo
      iface lo inet loopback
      
      auto eth0
        iface eth0 inet static
        address 10.11.1.3
        netmask 255.255.255.0
        gateway 10.11.1.1
      """
    elif self.nombre == 'lb':
      contenido_interfaces = """
      auto lo
      iface lo inet loopback
      
      auto eth0
        iface eth0 inet static
        address 10.11.1.1
        netmask 255.255.255.0
      
      auto eth1
        iface eth1 inet static
        address 10.11.2.1
        netmask 255.255.255.0
      """

    # Directorio de trabajo actual
    directorio_trabajo = os.getcwd()

    # Ruta completa del archivo "interfaces"
    ruta_interfaces = os.path.join(directorio_trabajo, "interfaces")
    # Escribir el contenido sobre el archivo "interfaces"
    with open(ruta_interfaces, 'w') as interfaces:
      interfaces.write(contenido_interfaces)

    # Ruta completa del archivo "hostname"
    ruta_hostname = os.path.join(directorio_trabajo, "hostname")
    # Escribir el contenido sobre el archivo "hostname"
    with open(ruta_hostname, 'w') as hostname:
      hostname.write(f'{self.nombre}')

    # Copiar los ficheros de configuración a las máquinas virtuales
    subprocess.call(['sudo', 'virt-copy-in', '-a', f'{self.nombre}.qcow2', 'interfaces', '/etc/network'])
    subprocess.call(['sudo', 'virt-copy-in', '-a', f'{self.nombre}.qcow2', 'hostname', '/etc'])

    # Editar el archivo "hosts"
    subprocess.call(['sudo', 'virt-edit', '-a', f'{self.nombre}.qcow2', '/etc/hosts', '-e', '"s/127.0.1.1.*/127.0.1.1', f'{self.nombre}/"'])

    # Configurar el balanceador de tráfico para que funcione como router al arrancar
    if self.nombre == 'lb':
      os.system('sudo virt-edit -a lb.qcow2 /etc/sysctl.conf -e "s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/"')
      
      # MEJORA OPCIONAL Nº2
      # Ruta completa al archivo "rc.local"
      ruta_rc = os.path.join(directorio_trabajo, "rc.local")
      # Crear el contenido de rc.local
      contenido_rc = """
      #!/bin/bash

      # Detener el servicio Apache
      sudo service apache2 stop

      # Añadir configuración a haproxy.cfg
      sudo cat <<EOL >> /etc/haproxy/haproxy.cfg
      frontend lb
      bind *:80
      mode http
      default_backend webservers
      backend webservers
      mode http
      balance roundrobin
      server s1 10.11.2.31:80 check
      server s2 10.11.2.32:80 check
      server s3 10.11.2.33:80 check
      EOL

      # Reiniciar el servicio HAProxy
      sudo service haproxy restart

      exit 0
      """
      # Escribir el contenido sobre el archivo "rc"
      with open(ruta_rc, 'w') as rc:
        rc.write(contenido_rc)
      # Copiar el fichero de configuración al router lb
      subprocess.call(['sudo', 'virt-copy-in', '-a', 'lb.qcow2', 'rc.local', '/etc'])
      # Asignar permisos de ejecución al archivo rc.local en el router lb
      subprocess.call(['sudo', 'virt-customize', '-a', 'lb.qcow2', '--run-command', 'chmod +x {}'.format('/etc/rc.local')])
    
    # Arrancar el gestor de máquinas virtuales
    os.environ['HOME']='/mnt/tmp'
    subprocess.call(['sudo', 'virt-manager'])
    # Arrancar cada máquina virtual
    subprocess.call(['sudo', 'virsh', 'define', f'{self.nombre}.xml'])
    subprocess.call(['sudo', 'virsh', 'start', f'{self.nombre}'])

  # FUNCIÓN PARA MOSTRAR LA CONSOLA DE CADA MÁQUINA VIRTUAL
  def mostrar_consola_mv (self):
    log.debug("mostrar_mv " + self.nombre)
    # Arrancar la consola de la máquina virtual
    subprocess.call([f"xterm -rv -sb -rightbar -fa monospace -fs 10 -title '{self.nombre}' -e 'sudo virsh console {self.nombre}' &"], shell=True)

  # FUNCIÓN PARA PARAR CADA MÁQUINA VIRTUAL
  def parar_mv (self):
    log.debug("parar_mv " + self.nombre)
    # Detener la máquina virtual
    subprocess.call(['sudo', 'virsh', 'shutdown', f'{self.nombre}'])

  # FUNCIÓN PARA LIBERAR CADA MÁQUINA VIRTUAL Y ELIMINAR SUS FICHEROS ASOCIADOS
  def liberar_mv (self):
    log.debug("liberar_mv " + self.nombre)
    # Liberar la máquina virtual
    subprocess.call(['sudo', 'virsh', 'destroy', f'{self.nombre}'])
    # Borrar sus ficheros asociados
    subprocess.call(['rm', '-f', f'{self.nombre}.qcow2', f'{self.nombre}.xml', 'interfaces', 'hostname', 'rc.local'])

class Red:
  def __init__(self, nombre):
    self.nombre = nombre
    log.debug('init Red ' + self.nombre)

  # FUNCIÓN PARA CREAR LA RED
  def crear_red(self):
      log.debug('crear_red ' + self.nombre)
      # Crear los bridges correspondientes a las dos redes virtuales
      subprocess.call(['sudo', 'brctl', 'addbr', 'LAN1'])
      subprocess.call(['sudo', 'brctl', 'addbr', 'LAN2'])
      subprocess.call(['sudo', 'ifconfig', 'LAN1', 'up'])
      subprocess.call(['sudo', 'ifconfig', 'LAN2', 'up'])

  # FUNCIÓN PARA LIBERAR LA RED
  def liberar_red(self):
      log.debug('liberar_red ' + self.nombre)
      # Eliminar los bridges correspondientes a las dos redes virtuales
      subprocess.call(['sudo', 'ifconfig', 'LAN1', 'down'])
      subprocess.call(['sudo', 'ifconfig', 'LAN2', 'down'])
      subprocess.call(['sudo', 'brctl', 'delbr', 'LAN1'])
      subprocess.call(['sudo', 'brctl', 'delbr', 'LAN2'])