
import mysql.connector
import random
import string
import os
import socket
import struct
import paramiko


class Databaze_radius():

    # def __init__(self, version, mac_address, ):
    def __init__(self, mac_address, mikrotik_name):
        
        self.mikrotik_name = mikrotik_name
        # self.version = version
        self.mac_address = mac_address
        self.password = self.generate_password()
        self.id_username = None
        self.username = None
        self.ip_address = None
        self.model = "Mikrotik"
        self.description = None
        self.location = None
        self.dhcp_ip = None
        self.dhcp_mask = None
        self.dhcp_mac_mikrotik = None
        
    def create_new_acc(self):
        self.connect()
   
        self.get_free_username()
     
        self.add_to_radcheck()
        
        self.addgw()
        
        self.delete_free_username()
        
        self.disconnect()

    def mac2long(self, mac):
        return int(mac.replace(':', ''), 16)
    
    def long2mac(self, num):
        # Convert integer to MAC address string with colons
        if isinstance(num, int):
            mac = "{:012X}".format(num)
            mac_with_colons = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
            return mac_with_colons

        else:
            pass



    def long2ip(self, ip_long):
        packed_ip = struct.pack("!L", ip_long)
        return socket.inet_ntoa(packed_ip)

    def ip2long(self, ip):
        packed_ip = socket.inet_aton(ip)
        return struct.unpack("!L", packed_ip)[0]


    def connect(self):
        # Connect to the MySQL server
        self.cnx = mysql.connector.connect(user='admin_jmal', password='Borec2021',
                              host='10.120.1.12',
                              database='radius')
        self.cursor = self.cnx.cursor()
        
        
    def disconnect(self):
        # Close the self.cursor and connection
        self.cursor.close()
        self.cnx.close()
            
    def get_free_username(self):
        query = "SELECT * FROM free_usernames ORDER BY id ASC LIMIT 1"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        self.id_username = result[0]
        self.username = result[1]
        self.ip_address = result [2]
        print(f"{self.id_username} a {self.username}")
        return self.id_username, self.username
    
    def delete_free_username(self):
        query = f"DELETE FROM free_usernames WHERE id={self.id_username}"
        self.cursor.execute(query)
        self.cnx.commit()
        print(f"Smazáno: {self.username}")
    
    def generate_password(self):
        characters = string.ascii_letters + string.digits
        self.password = ''.join(random.sample(characters, 12))
        print(self.password)
        return self.password
        
    def add_to_radcheck(self):
        # Nastavte přihlašovací údaje pro vzdálený server
        remote_host = "10.120.1.12"
        remote_user = "jiri"
        remote_password = "Bour@k2022"

        # Vytvořte SSH klienta
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Připojte se k vzdálenému serveru
        ssh_client.connect(remote_host, username=remote_user, password=remote_password)

        # Spusťte příkaz na vzdáleném serveru
        cmd = f"/etc/scripts/addacct.sh make '{self.username}' '{self.password}'"
        
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        output = stdout.read().decode()
        print(f"heslo kontrola : {self.username} {self.password}")
        print(output)

        # Uzavřete SSH připojení
        ssh_client.close()
    
    # def add_to_radcheck(self):
    #     # Předpokládám, že již máte nastaveno self.username a self.password
    #     query = "INSERT INTO radius.radcheck (username, attribute, op, value) VALUES (?, 'Cleartext-Password', ':=', ?)"
    #     self.cursor.execute(query, (self.username, self.password))
        
    #     # Proveďte změny v databázi
    #     self.connection.commit()
        
    #     print(f"Uživatel {self.username} byl úspěšně přidán do tabulky radius.radcheck s heslem {self.password}.")

        
    
        
        
    def addgw(self):
        # Nastavte přihlašovací údaje pro vzdálený server
        remote_host = "10.120.1.12"
        remote_user = "jiri"
        remote_password = "Bour@k2022"

        # Vytvořte SSH klienta
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Připojte se k vzdálenému serveru
        ssh_client.connect(remote_host, username=remote_user, password=remote_password)

        # Připravte příkaz pro spuštění na vzdáleném serveru
        self.mac_address = self.mac_address.replace(":", "")
        cmd = f"/etc/scripts/addgw.sh make '{self.username}' '{self.mac_address}' '{self.username}:{self.password}' '{self.ip_address}' '{self.location}' '{self.model}' '{self.mikrotik_name}'"

        # Spusťte příkaz na vzdáleném serveru
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        output = stdout.read().decode()

        print(output)

        # Uzavřete SSH připojení
        ssh_client.close()
        
    
    
    def connect_btm(self):
        # Connect to the MySQL server
        self.cnx = mysql.connector.connect(user='admin_jmal', password='Borec2021',
                              host='10.120.1.12',
                              database='btm')
        self.cursor = self.cnx.cursor()
    
    
    def get_free_dhcp(self):
        self.connect_btm()
        query = "SELECT * FROM net ORDER BY ip ASC LIMIT 1"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        self.dhcp_ip = result[0]
        self.dhcp_mask = result[1]
        self.dhcp_mac_mikrotik = result[2]

        print(f"{self.long2ip(self.dhcp_ip)} a {self.long2ip(self.dhcp_mask)} a {self.long2mac(self.dhcp_mac_mikrotik)}")
        # return self.id_username, self.username


test = Databaze_radius("","")
test.get_free_dhcp()



