#!/usr/bin/env python

# Created by: Moksh Chitkara
# Last Update: May 13th 2026
# v0.1.0
# Copyright (C) 2026  Moksh Chitkara
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import os

# Global Variables
projectManager = resolve.GetProjectManager()

def main_ui():

	# vertical group
	window = [ui.HGroup({"Spacing": 10}, [
				ui.VGroup({"Spacing": 10}, [
					ui.TextEdit({ "ID": "list","Text": "Projects to Archive will be listed here.", "Weight": 20}),
					ui.HGroup({"Spacing": 10},[
						ui.HGap(),
						ui.Button({"ID": "archive","Text": "Archive", "Enabled": False, "Weight": 1}),
						ui.Button({"ID": "clear","Text": "Clear", "Enabled": False, "Weight": 1}),
						ui.HGap(),
					]),
				]),
				ui.VGroup({"Spacing": 10}, [
					ui.Tree({"ID": "browser", 'SortingEnabled': True, 'AlternatingRowColors': True, 'SelectionMode': 'ExtendedSelection',
							'Events': {'ItemDoubleClicked': True, 'ItemClicked': True}, "Weight": 20}),
					ui.HGroup({"Spacing": 10},[
						ui.HGap(),
						ui.Button({"ID": "add","Text": "Add Selected", "Weight": 1}),
						ui.HGap(),
					]),
				]),
			])]

	return window

################################################################################################
# Window creation #
###################

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?

# window definition
window = disp.AddWindow({"WindowTitle": "Moksh's Grade Finder",
			"ID": "GFWin", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True},
			"Geometry": [1000,300,1150,800], # x-position, y-position, width, height
			}, 
			main_ui())


itm = window.GetItems() # Grabs all UI elements to be manipulated

################################################################################################
# Functions #
#############

class PathList:

	def __init__(self, pathlist):
		log("PathList initialized")
		self.list = pathlist
		
	def __iter__(self):
		return iter(self.list)
		
	def __len__(self):
		return len(self.list)
		
	def __str__(self):
		itm["archive"].Enabled = True
		itm["clear"].Enabled = True
		self.sort()
		returnable = str(self.list[0])
		for pathmem in self.list[1:]:
			returnable = returnable + "\n" + str(pathmem)
		return returnable
	
	def sort(self):
		self.list.sort(key=str)
	
	def append(self, newItm):
		if newItm == None:
			log("PathList cannot append None Type", 3)
			
		elif self.iscopy(newItm):
			log("PathList cannot append Duplicates", 3)
			
		else:
			self.list.append(newItm)
	
	def combine(self, newLst):
		if newLst == None:
			log("PathList cannot append None Type", 3)
		else:
			seen = {}
			for item in self.list:
				key = str(item)
				if key not in seen:
					seen[key] = item
			for item in newLst:
				key = str(item)
				if key not in seen:
					seen[key] = item
			self.list = list(seen.values())
		
	def pop(self, idx):
		return self.list.pop(idx)
		
	def undo(self):
		latest = self.pop(-1)
		latest.pop(-1)
		self.append(latest)
		
	def update(self, new):
		latest = self.pop(-1)
		latest.append(new)
		self.append(latest)

class PathMem:
	
	# all this class needs is a timeline item
	def __init__(self, dbInfo):
		log("PathMem initialized")
		self.dbInfo = dbInfo
		self.dbType = dbInfo['DbType']
		self.dbName = dbInfo['DbName']
		self.dbIp = dbInfo['IpAddress']
		self.path = [self.dbName]
		
	def __str__(self):
		if len(self.path) > 1:
			return str(self.dbName) + ' > ' + ' > '.join(self.path[1:])
		else:
			return str(self.dbName)
			
	def __iter__(self):
		return self.path
			
	def append(self, newItm):
		if newItm == None:
			log("PathMem cannot append None Type", 3)
		else:
			self.path.append(newItm)

	def pop(self, idx):
		return self.path.pop(idx)
		
	def resest(self):
		del self.path[1:]
		
	def multiply(self, kids):
		pathlist = []
		for kid in kids:
			newpath = PathMem(self.dbInfo)
			newpath.path = newpath.path + self.path[1:]
			newpath.append(kid)
			pathlist.append(newpath)
		return pathlist
		
	def dupe(self):
		newpath = PathMem(self.dbInfo)
		newpath.path = newpath.path + self.path[1:]
		return newpath
		
	def dupeappend(self, kid):
		newpath = self.dupe()
		newpath.append(kid)
		return newpath
	
	def locate(self):
		projectManager.SetCurrentDatabase(self.dbInfo)
		projectManager.GotoRootFolder()
		for folder in self.path[1:-1]:
			projectManager.OpenFolder(folder)
	
	def archive(self):
		log("Starting archive " + str(self.path[-1]))
		self.locate()
		drapath = os.path.join(str(puitm["path"].Text), str(self.path[-1]))
		projectManager.ArchiveProject(self.path[-1], drapath, puitm["src"].Checked, puitm["cache"].Checked, puitm["proxy"].Checked)

def log(info, level = 1):

	if level == 1:
		level = "INFO"
	elif level == 2:
		level = "WARN"
	else:
		level = "EROR"
	
	time = datetime.datetime.now()
	
	fullLog = [str(time), level, info]
	print(" | ".join(fullLog))	

def dataTree():

	log("Building Database Tree")

	global toqueue
	toqueue = None
	itm["add"].Enabled = False
	itm["browser"].Clear()
	
	header = itm["browser"].NewItem()
	header.Text[0] = "Databases"
	itm["browser"].SetHeaderItem(header)
	itm["browser"].ColumnCount = 1
	itm["browser"].ColumnWidth[0] = 300
	
	global databaseLst
	databaseLst = projectManager.GetDatabaseList()
	for data in databaseLst:
		newRow = itm["browser"].NewItem()
		newRow.Text[0] = data['DbName']
		itm["browser"].AddTopLevelItem(newRow)
	
	itm["browser"].SortByColumn(0, "AscendingOrder")
	log("Database Tree Built")
	
	global state
	state = "dataTree"
	
def projTree():

	log("Building Project Tree")

	itm["add"].Enabled = True
	itm["browser"].Clear()
	
	header = itm["browser"].NewItem()
	header.Text[0] = "Projects"
	itm["browser"].SetHeaderItem(header)
	itm["browser"].ColumnCount = 1
	itm["browser"].ColumnWidth[0] = 300
	
	folderLst = projectManager.GetFolderListInCurrentFolder()
	projLst = projectManager.GetProjectListInCurrentFolder()
	
	for proj in sorted(projLst + folderLst):
		newRow = itm["browser"].NewItem()
		newRow.Text[0] = str(proj)
		itm["browser"].AddTopLevelItem(newRow)
	
	itm["browser"].SortByColumn(0, "AscendingOrder")
	
	newRow = itm["browser"].NewItem()
	newRow.Text[0] = " * GO TO PARENT FOLDER * "
	itm["browser"].AddTopLevelItem(newRow)
	
	log("Project Tree Built")
	
	global state
	state = "projTree"

def setDatabase(DbName):

	log("Running set Database")

	for database in databaseLst:
		if database['DbName'] == DbName:
			return projectManager.SetCurrentDatabase(database)
	log("No match database match found")
	return False

def _add(ev):

	log("Adding selected items to Queue")

	selected = itm["browser"].SelectedItems()
	
	if len(selected) < 1:
		return
	
	pathlist = []
	allprojects = projectManager.GetProjectListInCurrentFolder()
	allfolders = projectManager.GetFolderListInCurrentFolder()
	
	for key in selected:
		item = selected[key].Text[0]
		if item in allfolders:	
			while not projectManager.OpenFolder(item):
				pass
			toqueue.append(item)
			pathlist = pathlist + toqueue.multiply(projectManager.GetProjectListInCurrentFolder())
			toqueue.pop(-1)
			while not projectManager.GotoParentFolder():
				pass
		
		elif item in allprojects:
			pathlist.append(toqueue.dupeappend(item))
	
	global pathqueue
	if pathqueue == None:
		pathqueue = PathList(pathlist)
	else:
		pathqueue.combine(pathlist)
		
	itm["list"].Text = str(pathqueue)

	log("Queue Updated")

def _clear(ev):

	log("Clearing Queue")

	global pathqueue
	pathqueue = None

	itm["list"].Text = "Projects to Archive will be listed here."
	itm["archive"].Enabled = False
	itm["clear"].Enabled = False

def _tree(ev):
	
	global toqueue
	selected = itm["browser"].SelectedItems()
	
	for key in selected:
		folder = selected[key].Text[0]

	if selected == {}:
		if state == "dataTree":
			dataTree()
		else:
			toqueue.reset()
			projectManager.GotoRootFolder() # Goes to root in project manager 
			projTree()

	elif str(folder) == " * GO TO PARENT FOLDER * ":
		if projectManager.GotoParentFolder():
			toqueue.pop(-1)
			projTree()
		else:
			dataTree()
	
	elif projectManager.OpenFolder(str(folder)):	# opens folder if it is selected
		toqueue.append(str(folder))
		projTree()

	elif setDatabase(str(folder)):
		toqueue = PathMem(projectManager.GetCurrentDatabase())
		if state == "dataTree":
			projectManager.GotoRootFolder()
		projTree()
			
def _filebrowser(ev):
	location = fu.RequestDir()
	puitm["path"].Text = str(location)

def _archwin(ev):
	_filebrowser("none")
	
	if os.path.exists(puitm["path"].Text):		
		window.Hide()
		disp.ExitLoop()
		puwindow.Show()
		disp.RunLoop()
		puwindow.Hide()

def _main(ev):
	puitm["ok"].Enabled = False
	puitm["browse"].Enabled = False

	total = len(pathqueue)
	i = 0
	for project in pathqueue:
		i += 1
		puitm["progress"].Text = "Working on " + str(i) + " of " + str(total) + " archives." + "\n" + str(project)
		project.archive()

	puitm["progress"].Text = "Done!" + "\n\n" + str(pathqueue)

	puitm["ok"].Enabled = True
	puitm["browse"].Enabled = True

# needed to close window
def _close(ev):
	disp.ExitLoop()

################################################################################################
# GUI Elements #
# manipulations
dataTree()
# button presses
window.On.GFWin.Close = _close
window.On.browser.ItemDoubleClicked = _tree
window.On.archive.Clicked = _archwin
window.On.clear.Clicked = _clear
window.On.add.Clicked = _add
# window loops
window.Show()
disp.RunLoop()
window.Hide()
#################################################################################################
