import os
import sys
import time
import socket
import struct
# import fcntl  # Eliminar esta línea
import subprocess
from datetime import datetime
from threading import Thread

# Constantes
BROADCAST_IP = '255.255.255.255'
LOGGING_ENABLED = False  # Cambiar a True para habilitar el guardado de logs

# Función para enviar el paquete Wake-on-LAN
def send_wol_packet(mac_address):
    mac_bytes = bytes.fromhex(mac_address.replace(':', ''))
    magic_packet = b'\xff' * 6 + mac_bytes * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (BROADCAST_IP, 9))
    log(f"Paquete WOL enviado a {mac_address}")

# Función para obtener detalles de la interfaz de red
def get_network_details():
    details = {}
    try:
        details['local_ip'] = socket.gethostbyname(socket.gethostname())
        details['external_ip'] = subprocess.check_output(['curl', 'ifconfig.me']).decode().strip()
        details['connection_type'] = 'WIFI' if 'wlan' in details['local_ip'] else 'ETHERNET'
        details['ports_in_use'] = subprocess.check_output(['netstat', '-tuln']).decode().strip()
    except Exception as e:
        log(f"Error al obtener detalles de la red: {e}")
    return details

# Función para registrar mensajes
def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    if LOGGING_ENABLED:
        with open('wol_log.txt', 'a') as log_file:
            log_file.write(log_message + '\n')

# Función para verificar la capacidad de WOL
def check_wol_capability():
    try:
        result = subprocess.check_output(['ethtool', 'eth0']).decode()
        if 'Wake-on: g' in result:
            log("WOL está habilitado en eth0")
        else:
            log("WOL no está habilitado en eth0. Por favor, habilítelo usando 'sudo ethtool -s eth0 wol g'")
    except Exception as e:
        log(f"Error al verificar la capacidad de WOL: {e}")

# Función para mostrar el estado
def display_status():
    while True:
        details = get_network_details()
        status_message = f"Estado: Conectado | Tipo: {details['connection_type']} | IP Local: {details['local_ip']} | IP Externa: {details['external_ip']} | Puertos: {details['ports_in_use']}"
        print(status_message, end='\r')
        time.sleep(5)

# Función para mostrar el menú
def display_menu():
    print("\nMenú:")
    print("1. Enviar Paquete WOL")
    print("2. Verificar Capacidad de WOL")
    print("3. Reiniciar Script")
    print("4. Salir")

# Función principal
def main():
    Thread(target=display_status, daemon=True).start()
    while True:
        display_menu()
        choice = input("Ingrese su elección: ")
        if choice == '1':
            mac_address = input("Ingrese la dirección MAC del dispositivo objetivo: ")
            send_wol_packet(mac_address)
        elif choice == '2':
            check_wol_capability()
        elif choice == '3':
            log("Reiniciando script...")
            os.execv(sys.executable, ['python'] + sys.argv)
        elif choice == '4':
            log("Saliendo del script...")
            sys.exit()
        else:
            log("Elección inválida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main()
