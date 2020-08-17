#!/usr/bin/env python3
import requests
import json
import subprocess

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
        if (currentProxy != leastCurrentConnections):

            print("Current Proxy:    {}".format(currentProxy))
            print("Suggested Proxy:  {}".format(leastCurrentConnections))

            return 1

    def alterConfig(self, leastCurrentConnections, currentProxy):

        with open('core.conf', 'r') as configFileRead:
            configData = configFileRead.read()
            configOverwriteData = (configData.replace(currentProxy, leastCurrentConnections))

        with open('core.conf', 'w') as configFileWrite:
            configFileWrite.write(configOverwriteData)

    def leastCurrentConnections(self, serverRecomendations):
        print(json.dumps(serverRecomendations,indent=2))

        return str(list(serverRecomendations.keys())[0])

    def dockerInit(self, status):
        if status == 0:
            subprocess.run(["docker", "stop", "deluge"])
        if status == 1:
            subprocess.run(["docker", "start", "deluge"])

if __name__ == "__main__":
    start = AutoProxy(["United States"])
    serverRecomendations = start.serverRecomendations()
    currentProxy = start.currentProxy()
    leastCurrentConnections = start.leastCurrentConnections(serverRecomendations)
    proxyStatus = start.proxyStatus(leastCurrentConnections, currentProxy)

    if proxyStatus:
        start.dockerInit(self, 0)
        start.alterConfig(leastCurrentConnections, currentProxy)
        start.dockerInit(self, 1)
