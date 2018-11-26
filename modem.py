import re
import telnetlib

import xmltodict


class Modem:
    HOST = "192.168.1.1"
    USER = "admin"
    PASSWORD = "admin"

    def __init__(self):
        self.run()

    def run(self):
        self.login()
        self.getDataFromRouter()
        self.logout()

        parsedData = self.parseData()
        hosts = self.getHosts(parsedData)
        self.showActiveHosts(hosts)

    def login(self):
        self.tn = telnetlib.Telnet(self.HOST)
        print("Connection started")

        self.tn.read_until(b"Login: ")
        self.tn.write(self.USER.encode('ascii') + b"\n")
        print("Username passed")

        self.tn.read_until(b"Password: ")
        self.tn.write(self.PASSWORD.encode('ascii') + b"\n")
        print("Password passed")

    def getDataFromRouter(self):
        self.tn.write(b"dumpsysinfo\n")
        print("Sysinfo ok")

    def logout(self):
        self.tn.write(b"exit\n")
        print("Exit ok")

    def parseData(self):
        textData = self.tn.read_all().decode()
        matches = re.finditer(r"<Hosts>(.*?)<\/Hosts>", textData, re.DOTALL)
        return list(matches)[1].group(0)

    def getHosts(self, data):
        dict = xmltodict.parse(data)
        return dict['Hosts']['Host']

    def showActiveHosts(self, hosts):
        for host in hosts:
            if host['Active'] == 'TRUE':
                print(host['IPAddress'], host['HostName'])


Modem()
