import paramiko
import os
import time
from Databaze import Databaze_radius
from datetime import datetime



# configure logging
# logging.basicConfig(level=logging.DEBUG)

class Router():
    def __init__(self, ip_router):
        # self.host_name = hostname
        # self.host_name = self.host_name.decode("utf-8") # převod na text
        # self.host_name = self.host_name.split("\r\n")[1] # rozdělení řetězce a získání druhého prvku
        self.ip_router = ip_router.strip()
        self.ip_router_mask = self.get_ip_router_mask(self.ip_router)
        self.rsc_file_name = self.ip_router.replace(".", "_") + ".rsc"
        self.file_name = self.ip_router.replace(".", "_")
        self.file_name_backup = self.file_name + ".backup"
        
        self.version = None
        self.mac_address = None
        self.device_name = None
        self.interfaces = []
        self.ip_vpn = None
        self.dhcp_devices = []
        
        self.cesta = "Migrace_MBS"
        # self.cesta = "/home/jiri"
        
        self.local_path = f"{self.cesta}zalohy_routeru"
        self.pokracovat = True
        # Spousteni funkci
        # self.connecting()
        # self.get_ppp_interfaces()
        # self.get_btm_central_ip()
            
        # self.backup_local()
        # self.backup_download()
        # self.get_version() # nemusim volat, vola se v update fw
        # self.get_mac_address()
        # self.update_firmware()
        # self.create_and_add_vpn() ####
        # self.get_mikrotik_name()
        # self.unconnect()
        # self.log()
        # self.report()
        # self.backup_full()
    
        
    def get_btm_central_ip(self):
        stdin, stdout, stderr = self.client.exec_command("/ip address print")
        output = stdout.read().decode()
        
        for line in output.split("\n"):
            # print(line)
            if "BTM-CENTRAL" in line:
                self.ip_vpn = line.split(" ")[2]
                # ip = ip_line.strip().split("/")[0]
                return self.ip_vpn
        
        
    def get_ppp_interfaces(self):
        stdin, stdout, stderr = self.client.exec_command("/interface print detail")
        output = stdout.read().decode()
        
        for line in output.split("\n"):
            # print(line)
            if "ovpn-out" in line:
                interface = line.strip().split(" ")[5]
                self.interfaces.append(interface)
        # print(interfaces)
        return self.interfaces
    
        
        
    def backup_full(self):
        try:
            if self.connecting():
                # pokracovat = input(f"Chces zálohovat tento router? {self.get_device_name()} \n")
                # if pokracovat == "y": 
                log_1 = self.backup_local()
                time.sleep(10)
                log_2 = self.backup_download_rsc()
                # time.sleep(10)
                log_3 = self.backup_download()
                self.log(log_1, log_2, log_3, "", "",)
            else:
                self.log("", "", "", "", "")
                    
                    
        except:
            print("to se nepovedlo")
            self.offline_log()
            
            
            
    def log(self, arg_1, arg_2, arg_3, arg_4, arg_5):
        time_stemp = time.strftime("%H:%M:%S-%d-%m-%Y")
        log_file = time.strftime("%d-%m-%Y") + ".csv"
        self.get_mac_address()
        self.get_version()
        self.get_device_name()
        

        
        with open(f"{self.cesta}/logs/log_{log_file}", "a") as file:
            file.write("{},{},{},{},{},{},{},{},{},{}\n".format(self.ip_router, self.mac_address, self.version, self.device_name, arg_1, arg_2, arg_3, arg_4, arg_5, time_stemp))

            
    def offline_log(self):
        time_stemp = time.strftime("%H:%M:%S-%d-%m-%Y")
        log_file = time.strftime("%d-%m-%Y") + ".csv"
        
        with open(f"{self.cesta}/logs/log_{log_file}", "a") as file:
            file.write("{},{},{},{},{},{},{},{}\n".format(self.ip_router, "", "", "", "", "", "", time_stemp))           
            
        
    def report(self):
        time_stemp = time.strftime("%H:%M:%S-%d-%m-%Y")
        log_file = time.strftime("%d-%m-%Y") + ".csv"
        try:
            if self.connecting():  
                self.get_mac_address()
                self.get_version()
                self.get_device_name()
                self.get_ppp_interfaces()
                self.get_btm_central_ip()

                with open(f"{self.cesta}/logs/report_{log_file}", "a") as file:
                    file.write("{},{},{},{},{},{}, {}\n".format(self.ip_router, self.ip_vpn, self.mac_address, self.version, self.device_name, self.interfaces, time_stemp))
                    
                self.unconnect()      
            else:
                with open(f"{self.cesta}/logs/report_{log_file}", "a") as file:
                    file.write("{},{},{},{},{},{}, {}\n".format(self.ip_router, self.ip_vpn, self.mac_address, self.version, self.device_name, self.interfaces, time_stemp))
            
        except:
            print("Nepripojeno")

        
    def get_ip_router_mask(self, ip):
        parts = ip.split(".")
        self.ip_router_mask = ".".join(parts[:-1]) + ".0/24"
        # print(self.ip_router_mask)
        return self.ip_router_mask
           
    def connecting(self):
        try:
            # Create an SSH client
            self.client = paramiko.SSHClient()

            # Add the Mikrotik router's host key
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the Mikrotik router
            self.client.connect(hostname=self.ip_router, username='admin', password='', port=22, look_for_keys=False)
            
            # self.client.connect(hostname=self.ip_router, username='admin', password='MikroPass', port=20222, look_for_keys=False)
            self.sftp = self.client.open_sftp()
            
            print(f"SSH session login successful {self.ip_router} on port 22")
            return True
            
        except Exception as e:
            # Report login failure
            print(f"SSH session failed on login {self.ip_router} port 22")
            print(e)
            return False
        
        
        
    def connecting_20222(self):
        try:
            # Create an SSH client
            self.client = paramiko.SSHClient()

            # Add the Mikrotik router's host key
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the Mikrotik router
            # self.client.connect(hostname=self.ip_router, username='admin', password='', port=22, look_for_keys=False)
            
            self.client.connect(hostname=self.ip_router, username='admin', password='MikroPass', port=20222, look_for_keys=False)
            self.sftp = self.client.open_sftp()
            
            print(f"SSH session login successful {self.ip_router} on port 20222")
            return True
            
        except Exception as e:
            # Report login failure
            print(f"SSH session failed on login {self.ip_router} port 20222")
            print(e)
            return False
            
    def backup_local(self):
        
        try:
            stdin, stdout, stderr = self.client.exec_command(f"/export file={self.file_name}")
            time.sleep(2)
            stdin, stdout, stderr = self.client.exec_command(f"/system backup save dont-encrypt=yes name={self.file_name}")
            time.sleep(2)
            
            log = "Backup files created successfully."
            print(log)
            return log
            
        except Exception as e:
            log = "An error occurred while creating the backup files."
            print(e)
            print(log)
            return log
            
    def backup_download_rsc(self):
                    
            try:
                self.sftp.get(self.rsc_file_name, os.path.join(self.local_path, self.rsc_file_name))
                log = "RSC file downloaded successfully."
                print(log)
                return log
                
            except Exception as e:
                log = "An error occurred while downloading the RSC file."
                print(e)
                print(log)
                return log
                
    def backup_download(self):
                
            try:
                self.sftp.get(self.file_name_backup, os.path.join(self.local_path, self.file_name_backup))
                log = "Backup file downloaded successfully."
                print(log)
                return log
                
                
            except Exception as e:
                log = "Error while downloading backup file"
                print(e)
                print(log)
                return log
            
            
    def get_version(self):
        stdin, stdout, stderr = self.client.exec_command("system resource print")
        output = stdout.read().decode()
        # print(output)
        for line in output.split("\n"):
            # print(line)
            if "version: " in line:
                self.version = line
                self.version = self.version.strip()
                self.version = self.version.split("version: ")[1]
                break
        
        print(f"{self.version}")
        return self.version
    
    def get_mac_address(self):
        stdin, stdout, stderr = self.client.exec_command("/interface print detail")
        output = stdout.read().decode()
        for line in output.split("\n"):
            if "mac-address" in line:
                self.mac_address = line.strip()
                self.mac_address = self.mac_address.split(" ")[0] # oddelí mac
                self.mac_address = self.mac_address.split("=")[1] # oddeli popis
                break
            
        print(f"Current MAC address: {self.mac_address}")
        return self.mac_address
    
    
    
    def get_device_name(self):
        stdin, stdout, stderr = self.client.exec_command("/system identity print")
        self.device_name = stdout.read().decode()
        self.device_name = self.device_name.strip()
        self.device_name = self.device_name.split(":")[1]
        self.device_name = self.device_name.strip()
            
        print(f"Current device name: {self.device_name}")
        return self.device_name

            
    def update_firmware(self):
        
        while self.pokracovat:
            try:
                self.connecting()
                self.version = self.get_version()
                if self.version == "7.9 (stable)":
                    print(f"step 6/6 - Verze: {self.version}, Changing port and user password")
                    
                    stdin, stdout, stderr = self.client.exec_command("/ip service set ssh port=20222")   
                    # Změna hesla a přidání uživatele root

                    stdin, stdout, stderr = self.client.exec_command(f"/user set [find name=admin] password=MikroPass")

                    
                    result_service = stdout.read().decode()
                    result_service = result_service + "Heslo změneno"
                    
                    if "failed" in result_service.lower():
                        raise Exception("Heslo nezměneno") 
                    else:
                        # print(result_service)
                        pass
                    
                    
                elif self.version == "7.9 (test)":
                    
                    #Prepinam na stable
                    
                    stdin, stdout, stderr = self.client.exec_command("system package update set channel=stable") 

                    result = stdout.read().decode()
                    print("step 5/6 - Version set to Stable")
                    print(result)
                    if "failed" in result.lower():
                        raise Exception("Setting channel to testing failed.")
                    time.sleep(1)
                    self.update_firmware()
                    
                    
                elif self.version == "7.10beta5 (development)":
                    
                    #Prepinam na stable
                    
                    stdin, stdout, stderr = self.client.exec_command("system package update set channel=stable") 
                    stdin, stdout, stderr = self.client.exec_command("system package update check-for-updates")
                    stdin, stdout, stderr = self.client.exec_command("system package update download")
                    stdin, stdout, stderr = self.client.exec_command("system routerboard upgrade")
                    stdin, stdout, stderr = self.client.exec_command("reboot")
                    result = stdout.read().decode()
                    print("step 5/6 - Version set to Stable")
                    print(result)
                    if "failed" in result.lower():
                        raise Exception("Setting channel to testing failed.")
                    time.sleep(1)
                    self.update_firmware()

                        
                else:
        
                    try:
                        
                        print("Upgrading router")
                        
                        stdin, stdout, stderr = self.client.exec_command("system package update set channel=test") 
                        result = stdout.read().decode()
                        print("step 1/6 - Version set to Test")
                        if "failed" in result.lower():
                            raise Exception("Setting channel to testing failed.")
                        time.sleep(2)

                        stdin, stdout, stderr = self.client.exec_command("system package update check-for-updates")
                        result = stdout.read().decode()
                        print("step 2/6 - Checked for updates")
                        print(result)
                        if "failed" in result.lower():
                            raise Exception("Checking for updates failed.")
                        time.sleep(2)
                        
                        stdin, stdout, stderr = self.client.exec_command("system package update download")
                        result = stdout.read().decode()
                        print("step 3/6 - Updates downloaded")
                        print(result)
                        if "failed" in result.lower():
                            raise Exception("Downloading updates failed.")
                        time.sleep(2)

                        stdin, stdout, stderr = self.client.exec_command("system routerboard upgrade")
                        result = stdout.read().decode()
                        print("step 4/6 - Router upgraded. Going to reboot")
                        print(result)
                        
                        if "failed" in result.lower():
                            raise Exception("Upgrading routerboard failed.")
                        
                        else: 
                            # reboot
                            stdin, stdout, stderr = self.client.exec_command("reboot")
                        
                        time.sleep(10)
                        
                        
                    except Exception as e:
                        print("An error occurred while upgrading firmware.")
                        print(e)




                    
            except:
                
                
                    print("Could not connect on port 22")
                    # self.unconnect()
                    
                    time.sleep(2)
                    
                    print("Trying to connect on port 20222")
                    if self.connecting_20222():
                        

                        
                        # brzda = input("Upgrade finished, do you want to install the Router? (NO, n , N)\n")
                        # if brzda == "NO" or brzda == "N" or brzda == "n":
                        #     self.pokracovat = False
                        #     return self.pokracovat 
                            
                            
                        self.version = self.get_version()
                        
                        self.create_and_add_vpn()
                       
                        self.pokracovat = False
                        return self.pokracovat 
                    
                    else:
                        print("Error on connecting to port 20222")


                    input
                    print("Error, I am trying again in 10s..")
                    time.sleep(10)
                    self.update_firmware()


                
    # def check_name(self):
        
    #     if self.connecting_20222():
                
    #         try:
    #             # Vytvoreni VPN
    #             databaze = Databaze_radius(self.get_mac_address(), self.get_device_name())
                
    #             databaze.get_device_name_by_mac()
        
    #         except:
    #             print("nepovedlo se")

            
            
    def create_and_add_vpn(self):
        try:
            if self.connecting_20222():
                
                try:
                    # Vytvoreni VPN
                    databaze = Databaze_radius(self.get_mac_address(), self.get_device_name())
                 
                    # databaze.get_device_name_by_mac()
                    databaze.create_new_acc()  ##### Pozor přepíše to všechno
                    
                    # print("debug 2")
                    stdin, stdout, stderr = self.client.exec_command(f"/interface ovpn-client remove [find]")
                    time.sleep(2)
                    stdin, stdout, stderr = self.client.exec_command(f"/interface ovpn-client add name=BTM-CENTRAL connect-to=95.80.221.210 port=1194 mode=ip protocol=udp user={databaze.username} password={databaze.password} profile=default tls-version=any auth=sha1 cipher=aes256-cbc use-peer-dns=yes disconnect-notify=yes")
                    # print("debug 3")
                    result_vpn = stdout.read().decode()
                    # print("debug 4")
                    result_vpn = "install step 1 - OK - " + result_vpn + "VPN created"
                    if "failed" in result_vpn.lower():
                        raise Exception("install step 1 - ERR - VPN was not added.")
                    else:
                        print(result_vpn)
                    time.sleep(2)
                    
                except:
                    print("install step 1 - ERR - Could not created VPN")
                
                
                
                try:
                    # Zde přidejte vaše přihlašovací údaje pro SSH
                    ssh_username = "jiri"
                    ssh_password = "Bour@k2022"
                    remote_host = "10.120.1.12"

                    # Vytvoreni CCD na routeru
                    file_path = (f"/usr/local/etc/openvpn/ccd/{databaze.username}")
                    

                    # Připojení k vzdálenému serveru
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(remote_host, username=ssh_username, password=ssh_password)

                    # Vytvoření souboru na vzdáleném serveru a zápis dat
                    sftp = ssh.open_sftp()
                    with sftp.open(file_path, "w") as f:
                        f.write(f"ifconfig-push {databaze.ip_address} 10.100.0.1\n")
                        f.write("push \"route 10.120.1.0 255.255.255.0\"\n")
                    
                    # Nastavení oprávnění souboru (rw-rw-r--)
                    sftp.chmod(file_path, 0o664)

                    # Ověření existence souboru na vzdáleném serveru
                    try:
                        sftp.stat(file_path)
                        result_ccd = f"install step 2 - OK - File {file_path} was created."
                    except FileNotFoundError:
                        result_ccd = f"install step 2 - ERR-  File {file_path} was not created"

                    # Ukončení spojení a výpis výsledku
                    sftp.close()
                    ssh.close()
                    print(result_ccd)
                    time.sleep(2)
                    
                except:
                    print(f"install step 2 - ERR - I did not created CCD file - ERROR: {result_ccd}")

                
                
                try:
                    
                    # Pridani routy      
                    stdin, stdout, stderr = self.client.exec_command("/")
                    stdin, stdout, stderr = self.client.exec_command("/ip route add dst-address=10.100.0.0/24 gateway=BTM-CENTRAL vrf-interface=BTM-CENTRAL distance=1 scope=30 target-scope=10 routing-table=main")
                    result_route = stdout.read().decode()
                    result_route = "install step 3 - OK - " + result_route + "Routes was added"
                    if "failed" in result_route.lower():
                        raise Exception("install step 3 - ERR - Routes wasnt added.") 
                    else:
                        print(result_route)
                    time.sleep(2)
                    
                except:
                    print("install step 3 - ERR - Add route failed.")
                    
                
                
                try:
                    
                    # # Odstranění existujícího záznamu
                    # stdin, stdout, stderr = self.client.exec_command("/interface list member remove [find interface=BTM-CENTRAL list=LAN]")
                    # Pridani interface do LAN
                    stdin, stdout, stderr = self.client.exec_command("/interface list member add interface=BTM-CENTRAL list=LAN")
                    result_interface = stdout.read().decode()
                    result_interface = "install step 4 - OK - " + result_interface + "Interface BTM-CENTRAL was added to LAN"
                    if "failed" in result_interface.lower():
                        raise Exception("install step 4 - ERR - Add interface BTM-CENTRAL to lan was failed.") 
                    else:
                        print(result_interface)
                    time.sleep(2)
                except:
                    print("install step 4 - ERR -: Add interface failed.")
                
                
                try:
                    
                    # Spusteni sluzeb 
                    stdin, stdout, stderr = self.client.exec_command(f"/ip service set winbox address=10.100.0.0/24,{self.ip_router_mask},192.168.207.0/24")
                    stdin, stdout, stderr = self.client.exec_command(f"/ip service set www address=10.100.0.0/24,{self.ip_router_mask},192.168.207.0/24")
                    stdin, stdout, stderr = self.client.exec_command(f"/snmp set enabled=yes trap-version=2 location={self.device_name}")
                    result_service = stdout.read().decode()
                    result_service = "install step 5 - OK - " + result_service + "Services were successfully started"
                    
                    if "failed" in result_service.lower():
                        raise Exception("install step 5 - ERR - Add services failed.") 
                    else:
                        print(result_service)
                    time.sleep(2)
                    
                except:
                    print("install step 5 - ERR - Add services failed.")

            
                try:
                    
                    # Wifi
                    stdin, stdout, stderr = self.client.exec_command("/interface wireless/security-profiles/set default mode=dynamic-keys authentication-types=wpa2-psk wpa2-pre-shared-key=BluePass70")
                    
                    stdin, stdout, stderr = self.client.exec_command("/interface wireless set wlan1 ssid=dsmediaplay-zr")

                    stdin, stdout, stderr = self.client.exec_command("interface wireless disable wlan1")

                    stdin, stdout, stderr = self.client.exec_command(f"/system identity set name={databaze.username}")
                    print("install step 6 - OK - Wifi was successfully set")
                    
                except:
                    print("install step 6 - ERR - Add services failed.")

                

                #     print(result_service)
                time.sleep(2)    
                
                
                print(f"Good JOB, router is prepare for production, do not forget for printing the stick with name: {self.file_name}   #######")
                
                # reboot
                stdin, stdout, stderr = self.client.exec_command("reboot")
                    
                    
                # # Deaktivace všech existujících DHCP serverů
                # stdin, stdout, stderr = self.client.exec_command("/ip dhcp-server disable [find]")
                    
                    
                # # Ukonceni sesion    
                # self.unconnect()
                
                
            
        except:
            print(f"Nepřipojeno k {self.get_device_name()}")
                
            
                    
    def unconnect(self):
        #Close the SFTP session
        self.sftp.close()
        
        # Close the SSH connection
        self.client.close()
        

    def get_name(self):
        stdin, stdout, stderr = self.client.exec_command("/interface print detail")
        output = stdout.read().decode()
        for line in output.split("\n"):
            if "mac-address" in line:
                self.mac_address = line.strip()
                self.mac_address = self.mac_address.split(" ")[0] # oddelí mac
                self.mac_address = self.mac_address.split("=")[1] # oddeli popis
                break
            
        print(f"Current MAC address: {self.mac_address}")
        return self.mac_address
            


    def get_dhcp_devices(self):
        time_stemp = time.strftime("%H:%M:%S-%d-%m-%Y")
        log_file = time.strftime("%d-%m-%Y") + "_devices.csv"
        device_address = None
        device_mac_address = None
        device_host_name = None
        try:
            if self.connecting():
                stdin, stdout, stderr = self.client.exec_command("/ip dhcp-server lease print")
                output = stdout.read().decode()
                lines = output.split("\n")
            
                for line in lines:
                    if line and not line.startswith(";") and not line.startswith("#") and not line.startswith("Columns"):

                        # print(line)
                        values = line.split()
                        device_address = values[1]
                        # print(device_address)
                        device_mac_address = values[2]
                        # print(device_mac_address)
                        device_host_name = values[3]
                        # print(device_host_name)
                        
                        
                        self.get_mac_address()
                        # self.get_version()
                        self.get_device_name()
                        # self.get_ppp_interfaces()
                        self.get_btm_central_ip()

                        with open(f"{self.cesta}/logs/report_{log_file}", "a") as file:
                            file.write("{},{},{},{},{},{},{},{}\n".format(self.ip_router, self.ip_vpn, self.mac_address, self.device_name, device_address, device_mac_address, device_host_name, time_stemp))
                                      
        except:
            print("nepovedlo se")
            with open(f"{self.cesta}/logs/report_{log_file}", "a") as file:
                file.write("{},{},{},{},{},{},{},{}\n".format(self.ip_router, self.ip_vpn, self.mac_address, self.device_name, device_address, device_mac_address, device_host_name, time_stemp)) 




    # def dhcp_setup(self):

        
       









####### PROGRAM #########


# # Create an instance of the Program class
# router = Router("10.100.0.10")
# router.get_dhcp_devices()


## Import dokumentu ###
# with open("report_po_upgradu.csv") as csv: # importuje soubor

# with open("Migrace_MBS/logs/archiv/report_po_upgradu.csv") as csv: # importuje soubor
#     # print(csv.readline()) # přečte a ignoruje první řádek
#     for x in csv.readlines(): # přečte postupně řádky
#         data = x.split(",") # udělá u toho list a rozdělí ho
#         ip = data[0]
#         ip = ip.strip() # naplní objekt daty ze souboru
#         ip_nase = data[1]
#         mac = data[2]
#         mac = mac.strip()
#         # if mac != "None" and ip_nase == "None":
        
#         # print(ip)
#         rpi = Router(ip)
#         rpi.get_dhcp_devices()
#             # dalsi_router = input("Pokračovat na další router? (Pokud ne, NO)\n")
#             # if dalsi_router == "NO" or dalsi_router == "N" or dalsi_router == "n":
#             #     break
       





