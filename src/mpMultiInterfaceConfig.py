from mpConfig import MpConfig
from mpMultiInterfaceTopo import MpMultiInterfaceTopo
from mpParamTopo import MpParamTopo
from mpTopo import MpTopo

class MpMultiInterfaceConfig(MpConfig):
	def __init__(self, topo, param):
		MpConfig.__init__(self, topo, param)

	def configureRoute(self):
		i = 0
		count=int(MpTopo.clientCount)
		for l in self.topo.switch:
			for j in range (1,count+1):
				cmd = self.addRouteTableCommand(self.getClientIP(i,j), i)
			# cmd2 = self.addRouteTableCommand(self.getClient2IP(i), i)
				self.topo.commandTo(self.client[j-1], cmd)
			# self.topo.commandTo(self.client[1], cmd2)


				cmd = self.addRouteScopeLinkCommand(
						self.getClientSubnet(i),
						self.getClientInterface(i,j), i)
				self.topo.commandTo(self.client[j-1], cmd)
			# cmd2 = self.addRouteScopeLinkCommand(
			# 		self.getClientSubnet(i),
			# 		self.getClient2Interface(i), i)
			# self.topo.commandTo(self.client[1], cmd2)

				cmd = self.addRouteDefaultCommand(self.getRouterIPSwitch(i),
						i)
				self.topo.commandTo(self.client[j-1], cmd)
			# self.topo.commandTo(self.client[1], cmd)
			i = i + 1

		for j in range (1,count+1): 
			cmd = self.addRouteDefaultGlobalCommand(self.getRouterIPSwitch(0),
					self.getClientInterface(0,j))
		# cmd2 = self.addRouteDefaultGlobalCommand(self.getRouterIPSwitch(0),
		# 		self.getClient2Interface(0))
			self.topo.commandTo(self.client[j-1], cmd)
		# self.topo.commandTo(self.client[1], cmd2)

		cmd = self.addRouteDefaultSimple(self.getRouterIPServer())
		self.topo.commandTo(self.server, cmd)


	def configureInterfaces(self):
		count=int(MpTopo.clientCount)
		self.client =[]
		print("Configure interfaces for multi inf")
		for i in range (1,count+1):
			self.client.append(self.topo.getHost("Client"+str(i)))
		# self.client[0] = self.topo.getHost(MpTopo.clientName1)
		# self.client[1] = self.topo.getHost(MpTopo.clientName2)
		self.server = self.topo.getHost(MpTopo.serverName)
		self.router = self.topo.getHost(MpTopo.routerName)
		i = 0
		netmask = "255.255.255.0"
		links = self.topo.getLinkCharacteristics()
		for l in self.topo.switch:
			for j in range (1,count+1):
				cmd = self.interfaceUpCommand(
						self.getClientInterface(i,j),
						self.getClientIP(i,j), netmask)

			# cmd2 = self.interfaceUpCommand(
			# 		self.getClient2Interface(i),
			# 		self.getClient2IP(i), netmask)
				self.topo.commandTo(self.client[j-1], cmd)
			# self.topo.commandTo(self.client[0], cmd2)
				clientIntfMac = self.client[j-1].intf(self.getClientInterface(i,j)).MAC()
			# client2IntfMac = self.client[1].intf(self.getClient2Interface(i)).MAC()
				self.topo.commandTo(self.router, "arp -s " + self.getClientIP(i,j) + " " + clientIntfMac)
			# self.topo.commandTo(self.router, "arp -s " + self.getClient2IP(i) + " " + client2IntfMac)

				if(links[i].back_up):
					cmd = self.interfaceBUPCommand(
							self.getClientInterface(i,j))
					# cmd2 = self.interfaceBUPCommand(
					# 		self.getClient2Interface(i))
					self.topo.commandTo(self.client[j-1], cmd)
					# self.topo.commandTo(self.client[1], cmd2)

			cmd = self.interfaceUpCommand(
						self.getRouterInterfaceSwitch(i),
						self.getRouterIPSwitch(i), netmask)

			self.topo.commandTo(self.router, cmd)
			routerIntfMac = self.router.intf(self.getRouterInterfaceSwitch(i)).MAC()
			for j in range (1,count+1):
				self.topo.commandTo(self.client[j-1], "arp -s " + self.getRouterIPSwitch(i) + " " + routerIntfMac)
			# self.topo.commandTo(self.client[1], "arp -s " + self.getRouterIPSwitch(i) + " " + routerIntfMac)

			print(str(links[i]))
			i = i + 1

		cmd = self.interfaceUpCommand(self.getRouterInterfaceServer(),
				self.getRouterIPServer(), netmask)
		self.topo.commandTo(self.router, cmd)
		routerIntfMac = self.router.intf(self.getRouterInterfaceServer()).MAC()
		self.topo.commandTo(self.server, "arp -s " + self.getRouterIPServer() + " " + routerIntfMac)

		cmd = self.interfaceUpCommand(self.getServerInterface(),
				self.getServerIP(), netmask)
		self.topo.commandTo(self.server, cmd)
		serverIntfMac = self.server.intf(self.getServerInterface()).MAC()
		self.topo.commandTo(self.router, "arp -s " + self.getServerIP() + " " + serverIntfMac)

	# def getClientIP(self, interfaceID):
	# 	lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
	# 	clientIP = lSubnet + str(interfaceID) + ".1"
	# 	return clientIP

	def getClientIP(self, interfaceID, j):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientIP = lSubnet + str(interfaceID) + "." + str(j)
		return clientIP

	def getClient2IP(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientIP = lSubnet + str(interfaceID) + ".2"
		return clientIP

	def getClientSubnet(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientSubnet = lSubnet + str(interfaceID) + ".0/24"
		return clientSubnet

	def getRouterIPSwitch(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		routerIP = lSubnet + str(interfaceID) + ".9"
		return routerIP

	def getRouterIPServer(self):
		rSubnet = self.param.getParam(MpParamTopo.RSUBNET)
		routerIP = rSubnet + "0.2"
		return routerIP

	def getServerIP(self):
		rSubnet = self.param.getParam(MpParamTopo.RSUBNET)
		serverIP = rSubnet + "0.1"
		return serverIP

	def getClientInterfaceCount(self):
		return len(self.topo.switch)

	def getRouterInterfaceServer(self):
		return self.getRouterInterfaceSwitch(len(self.topo.switch))

	# def getClientInterface(self, interfaceID):
	# 	return  MpTopo.clientName1 + "-eth" + str(interfaceID)

	def getClientInterface(self, interfaceID, j):
		return  "Client"+ str(j) + "-eth" + str(interfaceID)

	def getClient2Interface(self, interfaceID):
		return  MpTopo.clientName2 + "-eth" + str(interfaceID)	

	def getRouterInterfaceSwitch(self, interfaceID):
		return  MpTopo.routerName + "-eth" + str(interfaceID)

	def getServerInterface(self):
		return  MpTopo.serverName + "-eth0"

	def getMidLeftName(self, id):
		return MpTopo.switchNamePrefix + str(id)

	def getMidRightName(self, id):
		return MpTopo.routerName

	def getMidL2RInterface(self, id):
		return self.getMidLeftName(id) + "-eth2"

	def getMidR2LInterface(self, id):
		return self.getMidRightName(id) + "-eth" + str(id)
