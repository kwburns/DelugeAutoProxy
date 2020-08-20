#!/usr/bin/env python3
import requests
import json
import subprocess
import argparse

class AutoProxy():

    """ Find best server with least concurrent connections. """

    def __init__(self, countryList):
        self.countryList = countryList

    def serverRecomendations(self):
        JsonResult = requests.get('https://nordvpn.com/api/server')
        server_data = {}
        for server in JsonResult.json():
            if server["features"]["socks"] == True and server["country"] in self.countryList:
                server_data[server["domain"]] = server["load"]

        return {k: v for k, v in sorted(server_data.items(), key=lambda item: item[1])}

    def currentProxy(self):
        with open('core.conf', 'r') as jsonFile:
            data = jsonFile.read().replace('\n', '')
            jsonData = data.replace('{    "file": 1,    "format": 1}','')

        parsedJson = json.loads(jsonData)
        return parsedJson["proxy"]["hostname"]

    def proxyStatus(self, leastCurrentConnections, currentProxy):
        print("\n[+] Current Proxy:    {}".format(currentProxy))
        print("[+] Suggested Proxy:  {}".format(leastCurrentConnections))

        if (currentProxy != leastCurrentConnections):
            return 1

    def alterConfig(self, leastCurrentConnections, currentProxy):

        print("[+] Finding Proxy Data", sep=' ', end='                        \r', flush=True)
        with open('core.conf', 'r') as configFileRead:
            configData = configFileRead.read()
            configOverwriteData = (configData.replace(currentProxy, leastCurrentConnections))

        print("[+] Replacing Proxy Data", sep=' ', end='                        \r', flush=True)
        with open('core.conf', 'w') as configFileWrite:
            configFileWrite.write(configOverwriteData)

    def leastCurrentConnections(self, serverRecomendations):
        print("\n"+json.dumps(serverRecomendations,indent=2))

        return str(list(serverRecomendations.keys())[0])

    def dockerInit(self, status):
        if status == 0:
            print("[+] Stopping Docker", sep=' ', end='                        \r', flush=True)
            subprocess.run(["docker", "stop", "deluge"])
        if status == 1:
            print("[+] Starting Docker", sep=' ', end='                        \r', flush=True)
            subprocess.run(["docker", "start", "deluge"])

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Automaticly switch proxy servers.')
    parser.add_argument("--vs",'--verify-state', choices=[str(0),str(1)], default=str(0), help="Does not alter core.conf file, or restart docker.")
    args = parser.parse_args()

    if int(args.vs) == 0:
        print("\n[+] Persistent Mode")

    else:
        print("\n[+] Verify Mode")

    start = AutoProxy(["United States"])
    serverRecomendations = start.serverRecomendations()
    currentProxy = start.currentProxy()
    leastCurrentConnections = start.leastCurrentConnections(serverRecomendations)
    proxyStatus = start.proxyStatus(leastCurrentConnections, currentProxy)

    if int(args.vs) == 0:
        if proxyStatus:
            start.dockerInit(0)
            start.alterConfig(leastCurrentConnections, currentProxy)
            start.dockerInit(1)
            print("",end='                        ')
            print("\n[+] Finished Task")
        else:
            print("\n[-] No Alteration Required", sep=' ', end='                        ', flush=True)
