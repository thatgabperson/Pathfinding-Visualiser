'''
16:9 aspect ratio
20% of width is settings menu

Changes:
- Added draw path func

	def eraseNode(self, node):
		if node == self.data.currentNS.start:
			self.data.currentNS.start = None
		elif node == self.data.currentNS.end:
			self.data.currentNS.end = None
		node.setType("Empty")
'''

import guiClasses
import pygame as pg
import math
import random

pg.init()
pg.display.set_caption("Prototype 3")
clock = pg.time.Clock()

# Intialising Pygame display with 16:9 aspect ratio
screenWidth = 1600
screenHeight = 900
screen = pg.display.set_mode((screenWidth, screenHeight))  #pg.NOFRAME

# Data for constructing node grid
gridy = 0.2 * screenHeight
gridHeight = screenHeight - gridy
nodeWidth = 20
totalRows = int(gridHeight / nodeWidth)
totalCols = int(screenWidth / nodeWidth)

# Intialising colours
white = (255, 255, 255)
lightGrey = (200, 200, 200)
cream = (246, 232, 177)
darkGrey = (80, 80, 80)
brown = (204, 153, 102)
blue = (86, 180, 233)
turquoise = (72, 209, 204)
brightTurquoise = (94, 229, 224)
green = (35, 197, 82)
brightGreen = (36, 221, 102)
darkGreen = (3, 106, 72)
darkGreenBlue = (40, 132, 127)
red = (207, 66, 41)
brightRed = (227, 72, 49)
yellow = (255, 232, 124)

# Data for node colours and their correlating colours
nodeColours = {"Empty": white, "Closed": blue, "Wall": darkGrey, "Start": green, "End": red, "Weight": darkGreen, "Current": yellow, "Closed Weight": darkGreenBlue}

# Fonts
buttonText = pg.font.SysFont("Calibri", 30)
statsText = pg.font.SysFont("Calibri", 28)
symbolText = pg.font.SysFont("segoeuisymbol", 12)
largerSymbolText = pg.font.SysFont("segoeuisymbol", 30)
headerOneText = pg.font.SysFont("Calibri", 30)
headerTwoText = pg.font.SysFont("Calibri", 28)
plainText = pg.font.SysFont("Calibri", 22)

# Creation of userevent
event_run_algorithm = pg.USEREVENT + 0  # Creates a 'userevent' in Pygame
pg.time.set_timer(event_run_algorithm, 70)  # Causes event every x milliseconds


class Node:
	def __init__(self, row, col):
		self.x = col * nodeWidth  # Coordinates in Pygame window
		self.y = gridy + row * nodeWidth
		self.row = row  # Index in the 2D node array
		self.col = col
		self.width = nodeWidth
		self.lastNode = None
		self.neighbours = []
		self.type = "Empty"  # Default are empty nodes
		self.lastType = None
		self.colour = white
		self.gCost = float(0)
		self.fCost = float('inf')  # Infinity
		self.weight = 0

	def setType(self, ntype):
		if ntype in nodeColours:  # If valid node type
			lastType = self.type

			# Changes some attributes according to their type
			if ntype == "Empty":
				# Resets the node to default state
				self.neighbours = []
				self.gCost = float(0)
				self.fCost = float('inf')  # Infinity
				self.weight = 0
				self.lastNode = None
			if ntype == "Weight":
				self.neighbours = []
				self.gCost = float(0)
				self.fCost = float('inf')  # Infinity
				# Changes its weight
				self.weight = 4
			if ntype == "Closed" and self.lastType == "Weight":
				ntype = "Closed Weight"
				
			self.type = ntype
			self.lastType = lastType
			self.colour = nodeColours[ntype]
		else:
			# Error message
			print("Error! Node type does not exist")

	def output(self):  # Debugging
		if self.lastNode == None:
			lastNode = (-1, -1)
		else:
			lastNode = (self.lastNode.col, self.lastNode.row)
		
		if self in data.currentNS.openSet:
			inOpenSet = True
		else:
			inOpenSet = False
		
		if self in data.currentNS.closedSet:
			inClosedSet = True
		else:
			inClosedSet = False
			
		print(self.type, self.lastType, (self.col, self.row), lastNode, inOpenSet,  inClosedSet, self.gCost, self.fCost)


class NodeStorage:
	def __init__(self):
		# Creates a 2D array for the node grid
		arr = [[] for i in range(totalRows)]
		row = 0
		while row < totalRows:
			col = 0
			while col < totalCols:
				arr[row].append(Node(row, col))
				col += 1
			row += 1
		self.nodeSet = arr
		self.currentNode = None
		self.start = None
		self.end = None
		self.openSet = []
		self.closedSet = []
		self.endFound = 0
		self.nodePath = []

	def findNeighbours(self, node, diagonal):
		neighbours = [] # Empty array

		# Finds all 8 surronding nodes
		# Scans a 3x3 area with the node in the center
		# Iterates through 3 rows and 3 columns around node
		if diagonal == True:
			for r in range(3):
				for c in range(3):
					# Ensures it's not the passed node
					if r != 1 or c != 1:
						row = node.row - 1 + r
						col = node.col - 1 + c
						# Validation: within index range
						if 0 <= row < totalRows and 0 <= col < totalCols:
							possibleNeighbour = self.nodeSet[row][col]  # Gets node at location
							# Checks if it's a node to be considered: can travel there and not a wall/closed node
							if self.isNodeValid(possibleNeighbour) and not self.isBlocked(node, possibleNeighbour):
								neighbours.append(possibleNeighbour)

		# No diagonals: only directly adjacent nodes
		else:
			adjacentChanges = [(-1, 0), (0, -1), (0, 1), (1, 0)]
			for i in adjacentChanges:
				row = node.row + i[0]
				col = node.col + i[1]
				# Validates to check if in index range
				if 0 <= row < totalRows and 0 <= col < totalCols:
					possibleNeighbour = self.nodeSet[row][col]  # Gets node at location
					# Checks if it's a node to be considered: can travel there and not a wall/closed node
					if self.isNodeValid(possibleNeighbour):
						neighbours.append(possibleNeighbour)

		node.neighbours = neighbours  # Assigns neighbours to node attribute

	def isNodeValid(self, node):
		if node.type != "Wall" and node not in self.closedSet:
			return True
		else:
			return False

	def addToOpenSet(self, node):
		# Validation; ensures we do not insert duplicates
		if node not in self.openSet:
			self.openSet.insert(0, node)

	def sortOpenSet(self):
		# Bubble Sort
		swapped = True

		# Breaks when it passes and does not swap values
		# 	That means that the list is now sorted
		while swapped == True:
			swapped = False
			pos = 0
			while len(self.openSet) - 1 > pos:
				# If the previous value is larger than the next, it swaps them
				if self.openSet[pos].fCost > self.openSet[pos + 1].fCost:
					holder = self.openSet[pos]
					self.openSet[pos] = self.openSet[pos + 1]
					self.openSet[pos + 1] = holder
					swapped = True
				pos = pos + 1

	def popLowestCost(self):
		self.sortOpenSet()
		node = self.openSet.pop(0)
		return node

	def isBlocked(self, n1, n2):
		# Finds the change in column and row
		dCol = n2.col - n1.col
		dRow = n2.row - n1.row
		
		# Checks if the two nodes are diagonal from each other
		if abs(dCol) == 1 and abs(dRow) == 1:
			neighbour1 = self.nodeSet[n1.row + dRow][n1.col]
			neighbour2 = self.nodeSet[n1.row][n1.col + dCol]
			# Checks if the two neighbouring nodes they share are walls
			if neighbour1.type == "Wall" and neighbour2.type == "Wall":
				return True  # Cannot go through walls thus blocked
		return False  # Can traverse from one node to the other


class DataStorage:
	def __init__(self):
		# Sets the default settings to these attributes
		self.run = False
		self.animationSpeed = 70
		self.selectedNodeType = "Start"
		self.resetOption = "Path Only"
		self.algorithm = "A*"
		self.heuristic = "Manhattan"
		self.diagonal = True
		self.traversedNodes = 0
		self.pathCost = 0
		self.timeTaken = 0
		self.helpActive = False
		self.nsSet = []
		self.currentNS = NodeStorage()

	def setRun(self, boolean):
		# Validates to ensure it's a bool data type
		if type(boolean) == bool:
			self.run = boolean

	def setAnimationSpeed(self, speed):
		# Range check validation
		if 1 <= speed <= 100:
			self.animationSpeed = speed

	def setSelectedNodeType(self, nodeType):
		self.selectedNodeType = nodeType

	def setResetOption(self, resetOption):
		self.resetOption = resetOption

	def setAlgorithm(self, algorithm):
		self.algorithm = algorithm

	def setHeuristic(self, heuristic):
		self.heuristic = heuristic

	def setDiagonal(self, boolean):
		if type(boolean) == bool:  # Validates to ensure it's a bool data type
			self.diagonal = boolean

	def setTraversedNodes(self, num):
		self.traversedNodes = num

	def setpathCost(self, num):
		self.pathCost = num

	def setTimeTaken(self, num):
		self.timeTaken = num

	def toggleHelp(self):
		if self.helpActive == True:
			self.helpActive = False
		else:
			self.helpActive = True


class MainScreen:
	def __init__(self, data):
		self.data = data
		self.eventList = None
		self.guiElements = {
			# Dictionary of gui elements; ordering from top to the bottom
			"Time Label": guiClasses.Label(55, 20, 120, 32, "right", statsText, "Time Taken:", (0, 3)),
			"Time Value": guiClasses.Label(180, 20, 140, 32, "left", statsText, "-", (0, 4)),
			"Explored Label": guiClasses.Label(15, 70, 160, 32, "right", statsText, "Nodes Visited:", (0, 3)),
			"Explored Value": guiClasses.Label(180, 70, 140, 32, "left", statsText, "0", (0, 4)),
			"Cost Label": guiClasses.Label(50, 120, 125, 32, "right", statsText, "Path Cost:", (0, 3)),
			"Cost Value": guiClasses.Label(180, 120, 140, 32, "left", statsText, "-", (0, 4)),
			# 10 gap
			"Speed Label": guiClasses.Label(330, 20, 140, 32, "center", buttonText, "Animation", (0, 3)),
			"Speed2 Label": guiClasses.Label(330, 52, 140, 32, "center", buttonText, "Speed", (0, 3)),
			"Speed Entry": guiClasses.TextEntry(476, 26, 80, 56, turquoise, brightTurquoise, white, buttonText, "70", "70", (0, 3)),
			"Diagonal Label": guiClasses.Label(330, 110, 140, 32, "center", buttonText, "Diagonal", (0, 3)),
			"Diagonal Toggle": guiClasses.ToggleButton(476, 100, 80, 56, green, brightGreen, red, brightRed, white, buttonText, "On", "Off", (0, 3)),
			# 22 gap
			"Reset Button": guiClasses.Button(578, 32, 120, 48, turquoise, brightTurquoise, white, buttonText, "Reset", (0, 3), controller.reset),
			"Run Toggle": guiClasses.ToggleButton(578, 100, 164, 56, green, brightGreen, red, brightRed, white, buttonText, "Run", "Stop", (0, 3)),
			"Right Button": guiClasses.Button(750, 100, 36, 56, turquoise, brightTurquoise, white, largerSymbolText, ">", (1, -2), controller.algorithmStepForward),
			# 20 gap
			"Reset Label": guiClasses.Label(808, 48, 180, 32, "center", buttonText, "Reset Option", (0, 3)),
			"Reset DDL": guiClasses.DropDownList(808, 84, 180, 48, turquoise, brightTurquoise, white, buttonText, symbolText, ["Path Only", "All"], (0, 3)),
			# 20 gap
			"Node Label": guiClasses.Label(1008, 48, 180, 32, "center", buttonText, "Node", (0, 3)),
			"Node DDL": guiClasses.DropDownList(1008, 84, 180, 48, turquoise, brightTurquoise, white, buttonText, symbolText, ["Start", "End", "Wall", "Weight"], (0, 3)),
			# 20 gap
			"Algorithm Label": guiClasses.Label(1208, 48, 180, 32, "center", buttonText, "Algorithm", (0, 3)),
			"Algorithm DDL": guiClasses.DropDownList(1208, 84, 180, 48, turquoise, brightTurquoise, white, buttonText, symbolText, ["A*", "Dijkstra's"], (0, 3)),
			# 20 gap
			"Heuristic Label": guiClasses.Label(1402, 48, 180, 32, "center", buttonText, "Heuristic", (0, 3)),
			"Heuristic DDL": guiClasses.DropDownList(1402, 84, 180, 48, turquoise, brightTurquoise, white, buttonText, symbolText, ["Manhattan", "Euclidean"], (0, 3)),

			"Help Button": guiClasses.CircularButton(1570, 30, 22, turquoise, brightTurquoise, white, buttonText, "?", (0, 3), self.data.toggleHelp)
		}
		self.helpGuiElements = {
			# Another dictionary of gui elements; ordering from top to the bottom
			# +4 gaps
			"Close Button": guiClasses.Button(90, 90, 200, 48, turquoise, brightTurquoise, white, buttonText, "Close", (0, 3), self.data.toggleHelp),
			"1.1": guiClasses.Label(100, 150, 200, 32, "left", headerOneText, "Pathfinding Visualiser", (0, 3)),
			"1.2": guiClasses.Label(130, 180, 200, 32, "left", plainText, "Using different algorithms, it finds a path from point A to point B factoring in the obstacles and weights of the tiles", (0, 3)),

			"2.1": guiClasses.Label(100, 220, 200, 32, "left", headerOneText, "Controls:", (0, 3)),
			"2.2": guiClasses.Label(130, 250, 232, 28, "left", plainText, "Left click + hold - Paints tiles ctinuously", (0, 3)),
			"2.3": guiClasses.Label(130, 280, 232, 28, "left", plainText, "Right click + hold - Erases tiles continusously", (0, 3)),
			"2.4": guiClasses.Label(130, 310, 232, 28, "left", plainText, "Q - Sets node to Start", (0, 3)),
			"2.5": guiClasses.Label(130, 340, 232, 28, "left", plainText, "W - Sets node to End", (0, 3)),
			"2.6": guiClasses.Label(130, 370, 232, 28, "left", plainText, "E - Sets node to Wall", (0, 3)),
			"2.7": guiClasses.Label(130, 400, 232, 28, "left", plainText, "R - Sets node to Weight", (0, 3)),

			"3.1": guiClasses.Label(100, 440, 200, 32, "left", headerOneText, "Features:", (0, 3)),
			"3.2": guiClasses.Label(130, 470, 232, 28, "left", plainText, "Run/pause – Starts/pauses pathfinding visualiser", (0, 3)),
			"3.3": guiClasses.Label(130, 500, 232, 28, "left", plainText, "Arrows – Steps forward/backwards once in the pathfinding algorithm", (0, 3)),
			"3.4": guiClasses.Label(130, 530, 232, 28, "left", plainText, "Animation Speed – Controls how fast the visualisation displays", (0, 3)),
			"3.5": guiClasses.Label(130, 560, 232, 28, "left", plainText, "Node Selection – Choose which nodes you want to paint", (0, 3)),
			"3.6": guiClasses.Label(130, 590, 232, 28, "left", plainText, "Diagonal Toggle – Allow or disallow to the algorithm to traverse diagonally", (0, 3)),

			"4.1": guiClasses.Label(100, 630, 200, 32, "left", headerOneText, "Algorithms:", (0, 3)),
			"4.2": guiClasses.Label(130, 660, 232, 28, "left", plainText, "A* – An informed pathfinding method that also factors weights", (0, 3)),
			"4.3": guiClasses.Label(130, 690, 232, 28, "left", plainText, "Dijkstra’s – An algorithm that includes weights and will find the shortest path", (0, 3))
		}
		self.ddlExpanded = True
		self.action = None

	def handleEvents(self):
		for event in self.eventList:
			# Quits when close button or escape is pressed
			if event.type == pg.QUIT:
				sys.exit()

			elif event.type == pg.USEREVENT:
				if self.data.run:
					controller.algorithmStepForward()

			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					sys.exit()
				elif event.key == pg.K_q:
					self.data.selectedNodeType = "Start"
					self.guiElements["Node DDL"].setSelected("Start")
				elif event.key == pg.K_w:
					self.data.selectedNodeType = "End"
					self.guiElements["Node DDL"].setSelected("End")
				elif event.key == pg.K_e:
					self.data.selectedNodeType = "Wall"
					self.guiElements["Node DDL"].setSelected("Wall")
				elif event.key == pg.K_r:
					self.data.selectedNodeType = "Weight"
					self.guiElements["Node DDL"].setSelected("Weight")
				elif event.key == pg.K_p:
					controller.randomiseGrid()

			elif event.type == pg.MOUSEBUTTONDOWN and self.data.helpActive == False and self.ddlExpanded == False:
				# Occurs once for every click
				# Returns bool values for left, middle and right click
				# e.g. left click returns [True, False, False]
				buttons_pressed = pg.mouse.get_pressed()
				mx, my = pg.mouse.get_pos()

				# When within node grid, it finds the clicked node and assigns it to action
				if gridy <= my <= screenHeight:
					node = controller.findClickedNode(mx, my)
					if buttons_pressed[0]:  # Left click
						self.action = controller.paintNode
					elif buttons_pressed[2]:  # Right click
						self.action = controller.eraseNode
					elif buttons_pressed[1]:  # Test
						node.output()

			elif event.type == pg.MOUSEBUTTONUP and self.data.helpActive == False and self.ddlExpanded == False:
				mx, my = pg.mouse.get_pos()

				# When within node grid
				if gridy <= my <= screenHeight:
					self.action = None

	def drawGrid(self):
		x = 0
		y = gridy
		width = screenWidth
		height = screenHeight
		space = nodeWidth  # Gap between each line
		lineColour = lightGrey

		while x <= screenWidth:
			# Draws a line from top to bottom
			# Parameters (surface, colour, startPos, endPos, width)
			pg.draw.line(screen, lineColour, (x, y), (x, screenHeight), 1)
			x += space

		x = 0  # Resets x

		while y <= height:
			# Draws a line from left to right
			# Parameters (surface, colour, startPos, endPos, width)
			pg.draw.line(screen, lineColour, (x, y), (screenWidth, y), 1)
			y += space

	def drawNodes(self):
		nodeArray = self.data.currentNS.nodeSet  # Gets the 2D node array
		# Iterates over and draws each node
		for row in nodeArray:
			for node in row:
				pg.draw.rect(screen, node.colour, (node.x, node.y, node.width, node.width))

	def drawSettingsMenu(self):
		# Draws background colour and each GUI element
		pg.draw.rect(screen, cream, (0, 0, screenWidth, gridy))
		for elementIndex in (self.guiElements):
			self.guiElements[elementIndex].draw(screen)

	def drawHelpWindow(self):
		# Draws background then each element
		bgRect = pg.Rect(75, 75, screenWidth - 150, screenHeight - 150)
		pg.draw.rect(screen, cream, bgRect)
		pg.draw.rect(screen, brown, bgRect, 8)
		for elementIndex in self.helpGuiElements:
			self.helpGuiElements[elementIndex].draw(screen)

	def drawPath(self):
		if self.data.currentNS.endFound != 1:
			print("Error")
		else:
			nodePath = self.data.currentNS.nodePath
			pos = 0
			while pos < len(nodePath) - 1:
				x1 = nodePath[pos].x + (nodePath[pos].width/2)
				y1 = nodePath[pos].y + (nodePath[pos].width/2)
				x2 = nodePath[pos+1].x + (nodePath[pos+1].width/2)
				y2 = nodePath[pos+1].y + (nodePath[pos+1].width/2)
				pg.draw.line(screen, yellow, (x1, y1), (x2, y2), 3)
				pos += 1

	def draw(self):
		# Calls draw functions in a specific order
		screen.fill(white)
		self.drawNodes()
		self.drawGrid()
		self.drawSettingsMenu()
		if self.data.currentNS.endFound == 1: # Draws node path if needed
			self.drawPath()
		if self.data.helpActive == True: # Draws help screen if needed
			self.drawHelpWindow()

	def update(self):  # Updates gui elements and the corresponding variables
		self.ddlExpanded = False
		# Enables drag feature for painting/erasing
		if self.action != None:
			if self.data.helpActive == False and self.ddlExpanded == False and data.run == False and data.currentNS.endFound != 1:
				mx, my = pg.mouse.get_pos()
				# When within node grid, it finds the clicked node and executes necessary method
				if gridy <= my <= screenHeight:
						mx, my = pg.mouse.get_pos()
						node = controller.findClickedNode(mx, my)
						self.action(node)
		# Updates GUI
		if self.data.helpActive == False:
			for elementIndex in (self.guiElements):
				element = self.guiElements[elementIndex]
				value = element.update(self.eventList)  # Returns a value if necessary

				# Drop Down Lists
				if type(element) == guiClasses.DropDownList:
					if element.get_draw_menu():  # Checks if any list is expanded
						self.ddlExpanded = True

					if value != -1:  # Option  chosen
						# Changes the respective variable
						if elementIndex == "Reset DDL":
							self.data.setResetOption(element.getSelectedOption())
						elif elementIndex == "Algorithm DDL":
							self.data.setAlgorithm(element.getSelectedOption())
						elif elementIndex == "Heuristic DDL":
							self.data.setHeuristic(element.getSelectedOption())
						elif elementIndex == "Node DDL":
							self.data.setSelectedNodeType(element.getSelectedOption())
						self.ddlExpanded = False

				# Toggle Buttons
				elif type(element) == guiClasses.ToggleButton:
					if value != -1:  # If clicked
						if elementIndex == "Run Toggle":
							if element.toggled:
								self.data.setRun(True)
							else:
								self.data.setRun(False)
						elif elementIndex == "Diagonal Toggle":
							if element.toggled:
								self.data.setDiagonal(False)
							else:
								self.data.setDiagonal(True)

				# Text Entry
				elif type(element) == guiClasses.TextEntry:
					if elementIndex == "Speed Entry":
						# Returned value
						if value != -1:
							# Possible values 1-99
							# 99 Fastest
							milliseconds = int(100 - value)
							# ~ milliseconds = value
							if self.data.animationSpeed != milliseconds:
								self.data.animationSpeed = milliseconds
								pg.time.set_timer(event_run_algorithm, milliseconds)

						# Enters or deletes text
						if element.highlighted == True:  # If selected
							# Finds all key presses then either deletes or types the numbers
							for event in self.eventList:
								if event.type == pg.KEYDOWN:
									if event.key == pg.K_BACKSPACE:
										element.deleteLastCharacter()
									elif event.unicode.isnumeric():  # Ensures it's a number
										# Range check validation before entering text
										if 1 <= int(element.text + event.unicode) <= 99:
											element.addText(event.unicode)

				# Labels
				elif type(element) == guiClasses.Label:
					if elementIndex == "Explored Value":
						self.data.traversedNodes = len(self.data.currentNS.closedSet)
						element.set_text(str(self.data.traversedNodes))

		else:
			for elementIndex in self.helpGuiElements:
				value = self.helpGuiElements[elementIndex].update(self.eventList)  # Returns a value if needed


class Controller:
	def __init__(self, data):
		self.data = data

	def findClickedNode(self, mx, my):
		# Iterates over every node in the 2D array
		for nodeRow in self.data.currentNS.nodeSet:
			for node in nodeRow:
				# Checks if the mouse position is within the node
				if node.x <= mx < node.x+node.width and node.y <= my < node.y+node.width:
					return node

	def paintNode(self, node):
		# Validation: only 1 start/end node may exist
		if data.selectedNodeType == "Start":
			if data.currentNS.start != None:
				self.eraseNode(data.currentNS.start)
			data.currentNS.start = node

		elif data.selectedNodeType == "End":
			if data.currentNS.end != None:
				self.eraseNode(data.currentNS.end)
			data.currentNS.end = node

		node.setType(data.selectedNodeType)

	def eraseNode(self, node):
		if node == self.data.currentNS.start:
			self.data.currentNS.start = None
		elif node == self.data.currentNS.end:
			self.data.currentNS.end = None
		node.setType("Empty")

	def calculateEuclideanDist(self, n1, n2):
		# sqrt((x2-x1)**2 + (y2-y1)**2)
		distance = math.sqrt((n1.col-n2.col)**2 + (n1.row-n2.row)**2)
		return distance

	def calculateManhattanDist(self, n1, n2):
		# |x2-x1| + |y2-y1|
		distance = abs(n1.col-n2.col) + abs(n1.row-n2.row)
		return distance

	def calculateHeuristicDist(self, n1, n2):
		heuristic = self.data.heuristic
		if heuristic == "Euclidean":
			return self.calculateEuclideanDist(n1, n2)
		elif heuristic == "Manhattan":
			return self.calculateManhattanDist(n1, n2)

	def aSearch(self):
		nS = data.currentNS

		# Checks if there is a current node; if not, set current as start node
		if nS.currentNode == None:
			nS.currentNode = nS.start
			nS.currentNode.fCost = 0

		# Adds neighbours to open set or updates them
		nS.findNeighbours(nS.currentNode, data.diagonal)

		# Iterates over neighbours
		for neighbour in nS.currentNode.neighbours:

			# gCost calculation
			# Caluclates distance between current node and neighbour
			gCost = self.calculateEuclideanDist(neighbour, nS.currentNode) + neighbour.weight
			# Adds current node gCost (neighbour's parent) to the calculations
			gCost += nS.currentNode.gCost

			# hCost calculation
			# Calcuates distance between neighbour and end node
			hCost = self.calculateHeuristicDist(neighbour, nS.end)

			# fCost calculation
			fCost = gCost + hCost

			# Compares the new fCost with its existing fCost
			if fCost < neighbour.fCost:
				neighbour.fCost = fCost
				neighbour.gCost = gCost
				neighbour.lastNode = nS.currentNode
				nS.addToOpenSet(neighbour)

		# Marks the current node as closed and adds it to the closed set
		if nS.currentNode.type != "Start" and nS.currentNode.type != "End":
			nS.currentNode.setType("Closed")
		nS.closedSet.append(nS.currentNode)

		# Gets the next current node
		# Validates that there is nodes in the open set; if not, no path available
		if len(nS.openSet) == 0:
			return -1
		else:
			nS.currentNode = nS.popLowestCost()
			if nS.currentNode.type != "Start" and nS.currentNode.type != "End":
				nS.currentNode.setType("Current")

		# Checks if end is found
		if nS.currentNode == nS.end:
			return 1  # Found
		return 0

	def dijkstraSearch(self):
		nS = data.currentNS

		# Checks if there is a current node; if not, set current as start node
		if nS.currentNode == None:
			nS.currentNode = nS.start
			nS.currentNode.fCost = 0

		# Adds neighbours to open set or updates them
		nS.findNeighbours(nS.currentNode, data.diagonal)

		# Iterates over neighbours
		for neighbour in nS.currentNode.neighbours:

			# Caluclates distance between current node and neighbour
			fCost = self.calculateEuclideanDist(neighbour, nS.currentNode) + neighbour.weight
			# Adds current node gCost (neighbour's parent) to the calculations
			fCost += nS.currentNode.gCost

			# Compares the new fCost with its existing fCost
			if fCost < neighbour.fCost:
				neighbour.fCost = fCost
				neighbour.gCost = fCost
				neighbour.lastNode = nS.currentNode
				nS.addToOpenSet(neighbour)

		# Marks the current node as closed and adds it to the closed set
		if nS.currentNode.type != "Start" and nS.currentNode.type != "End":
			nS.currentNode.setType("Closed")
		nS.closedSet.append(nS.currentNode)

		# Gets the next current node
		# Validates that there is nodes in the open set; if not, no path available
		if len(nS.openSet) == 0:
			return -1
		else:
			nS.currentNode = nS.popLowestCost()
			if nS.currentNode.type != "Start" and nS.currentNode.type != "End":
				nS.currentNode.setType("Current")

		# Checks if end is found
		if nS.currentNode == nS.end:
			return 1  # Found
		return 0  # Not found

	def findPath(self):
		# Validation: checks if the end has been found
		nS = self.data.currentNS
		if nS.endFound == 1:
			# Starts from the end node and pushes their parent node into node path stack
			tempNode = nS.end
			while tempNode != nS.start:
				nS.nodePath.append(tempNode)
				tempNode = tempNode.lastNode
			nS.nodePath.append(tempNode)  # Appends start
			
		pathCost = 0
		for node in self.data.currentNS.nodePath:
			if node.type == "Start":
				break
			if node.weight == 0:
				pathCost += 1
			else:
				pathCost += node.weight + 1
		self.data.pathCost = pathCost

	def reset(self):
		nS = self.data.currentNS
		# Iterates over each node in node set
		for nodeRow in nS.nodeSet:
			for node in nodeRow:
				# Resets last type
				node.lastType = None
				# Resets the path only: skips over start/end/wall/weight nodes
				if self.data.resetOption == "Path Only":
					if node.type == "Closed Weight" or node.type == "Weight":
						node.setType("Weight")
					elif node != nS.end and node != nS.start and node.type != "Wall":
						node.setType("Empty")
				# Resets every node
				else:
					node.setType("Empty")
					nS.end = None
					nS.start = None
					
		# Also cleans data when reset
		# Resets end/start nodes g and fcost
		if nS.end != None:
			nS.end.gCost = float(0)
			nS.end.fCost = float('inf')
		if nS.start != None:
			nS.start.gCost = float(0)
			nS.start.fCost = float('inf')
		# Empties sets and resets endFound
		nS.currentNode = None
		nS.openSet = []
		nS.closedSet = []
		nS.endFound = 0
		nS.nodePath = []
		mainScreen.guiElements["Cost Value"].set_text("-")
		mainScreen.guiElements["Time Value"].set_text("-")
		self.data.timeTaken = 0

	def algorithmStepForward(self):
		nS = self.data.currentNS
		# Validation: only runs if theres a start and an end node, and there's no found path
		if nS.endFound == 0 and nS.start != None and nS.end != None:
			if self.data.algorithm == "A*":
				algorithm = self.aSearch
			elif self.data.algorithm == "Dijkstra's":
				algorithm = self.dijkstraSearch
				
			start = pg.time.get_ticks()
			found = algorithm()
			end = pg.time.get_ticks()
			self.data.timeTaken += (end-start)
			
			if found == 1:
				mainScreen.guiElements["Run Toggle"].set_to_inactive()
				self.data.currentNS.endFound = 1
				self.data.setRun(False)
				self.findPath()
				mainScreen.guiElements["Cost Value"].set_text(str(self.data.pathCost))
				mainScreen.guiElements["Time Value"].set_text(str(self.data.timeTaken) + "ms")
			elif found == -1:
				self.data.currentNS.endFound = -1
				mainScreen.guiElements["Run Toggle"].set_to_inactive()
				self.data.setRun(False)

	def randomiseGrid(self):
		# Resets path if needed using "Path Only" option
		# Temporarily changes reset option
		temp = self.data.resetOption
		self.data.resetOption = "Path Only"
		self.reset()
		self.data.resetOption = temp
		
		# Iterates through grid setting nodes randomly
		# Empty(50%) Wall(25%) Weight (25%)
		nS = self.data.currentNS
		for nodeRow in nS.nodeSet:
			for node in nodeRow:
				if node.type != "Start" and node.type != "End":
					# Random values from 0-3
					value = random.randint(0,3)
					if value <= 1:
						node.setType("Empty")
					elif value == 2:
						node.setType("Wall")
					elif value == 3:
						node.setType("Weight")


data = DataStorage()
controller = Controller(data)
mainScreen = MainScreen(data)

run = True
while run:
	clock.tick(60)
	mainScreen.eventList = pg.event.get()
	mainScreen.handleEvents()
	mainScreen.draw()
	mainScreen.update()
	pg.display.update()
