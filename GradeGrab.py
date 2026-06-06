#!/usr/bin/env python

# Created by: Moksh Chitkara
# Last Update: May 22nd 2026
# v0.2.0
# Copyright (C) 2026  Moksh Chitkara
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime

# Global Variables
projectManager = resolve.GetProjectManager()
pathqueue = None
toqueue = None

def main_ui():

	# vertical group
	window = [ui.VGroup({"Spacing": 10}, [
				# Hero Timeline
				ui.HGroup({"Spacing": 1, "Weight": 0}, [
					ui.Label({"ID": "name_label","Text": "Powergrade name: ", "Weight": 0}),
					ui.LineEdit({"ID": "gradename", "Text": f"GradeGrab-{datetime.datetime.now():%m%d}-%02d-%02d-%02d" % (datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second), "Weight": 2}),
					ui.HGap(),
					ui.Label({"ID": "tl_label","Text": "Please select hero timeline: ", "Weight": 0}),
					ui.ComboBox({"ID": "timelines", "Weight": 2})
				]),
				
				ui.HGroup({"Spacing": 10}, [
					ui.VGroup({"Spacing": 10}, [
						ui.TextEdit({ "ID": "list","Text": "Projects to search will be listed here.", "Weight": 20}),
						ui.HGroup({"Spacing": 10},[
							ui.HGap(),
							ui.Button({"ID": "grab","Text": "Grab Grades", "Enabled": False, "Weight": 1}),
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
				]),
			])]

	return window

################################################################################################
# Window creation #
###################

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?

# window definition
window = disp.AddWindow({"WindowTitle": "Moksh's Grade Graber",
			"ID": "GGWin", 
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
		itm["grab"].Enabled = True
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
	def __init__(self, initial):
		log("PathMem initialized")
		self.initial = initial
		self.path = [initial]
		self.tl = None
		
	def __str__(self):
		if len(self.path) > 1:
			return ' > '.join(self.path)
		else:
			return str(self.path[0])
			
	def __iter__(self):
		return self.path
			
	def append(self, newItm, tl = None):
		if newItm == None:
			log("PathMem cannot append None Type", 3)
			
		elif self.tl != None:
			log("PathMem is complete to timeline", 3)
			
		else:
			self.path.append(newItm)
			self.tl = tl
			return True
			
		return False

	def pop(self, idx):
		if self.tl:
			self.tl = None
			return self.path.pop(idx)
		else:
			return self.path.pop(idx)
		
	def resest(self):
		self.tl = None
		self.path = []


	def multiply(self, kids):
		pathlist = []
		for kid in kids:
			newpath = PathMem(self.initial)
			print(self.path[1:])
			newpath.path = newpath.path + self.path[1:]
			newpath.append(kid, kids[kid])
			pathlist.append(newpath)
		return pathlist


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
	
# creates sorted list of all timelines in project
# input: project [item]
# output: tl_lst [list]
def tlLst(project):
	
	tl_lst = [] # placeholder will be filled
	current_tl = project.GetCurrentTimeline().GetName()
	# gets every tl name in project and appends to lst
	for i in range(1, project.GetTimelineCount()+1):
		name = project.GetTimelineByIndex(i).GetName()	
		if current_tl != name:
			tl_lst.append(name)

	tl_lst = sorted(tl_lst)
	tl_lst.insert(0, current_tl)

	return tl_lst # return the list
	
def projTree():

	log("Building Project Tree")

	global state
	state = "project"

	itm["add"].Enabled = False
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
	
def tlTree(project):

	log("Building Timeline Tree")

	global state
	state = "timeline"

	itm["add"].Enabled = True
	itm["browser"].Clear()
	
	header = itm["browser"].NewItem()
	header.Text[0] = "Projects"
	itm["browser"].SetHeaderItem(header)
	itm["browser"].ColumnCount = 1
	itm["browser"].ColumnWidth[0] = 300
	
	for tl in tlLst(project):
		newRow = itm["browser"].NewItem()
		newRow.Text[0] = tl
		itm["browser"].AddTopLevelItem(newRow)
	
	itm["browser"].SortByColumn(0, "AscendingOrder")
	
	newRow = itm["browser"].NewItem()
	newRow.Text[0] = " * GO TO PARENT FOLDER * "
	itm["browser"].AddTopLevelItem(newRow)
	
	log("Timeline Tree Built")

# gets index of timeline
# input: project [item], tl_name [str]
# output: i [int]
def tlidx(project, tlName):

	for i in range(1,project.GetTimelineCount()+1):
		name = project.GetTimelineByIndex(i).GetName()
		if name == tlName:
			return int(i)

def createPowergrade():
	if itm["gradename"].Text == "":
		albumName = f"GradeGrab-{datetime.datetime.now():%m%d}-%02d-%02d-%02d" % (datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second)
	else:
		albumName = itm["gradename"].Text
	
	project = projectManager.GetCurrentProject()
	gallery = project.GetGallery()
	galleryStillAlbum = gallery.CreateGalleryPowerGradeAlbum()
	if gallery.SetAlbumName(galleryStillAlbum, albumName):
		log("Powergrade album created")
		return galleryStillAlbum
	else:
		log("Powergrade album creation failed", 3)
		return False
	

def _add(ev):

	log("Adding selected timelines to Queue")

	selected = itm["browser"].SelectedItems()
	
	if len(selected) < 1:
		return
	project = projectManager.GetCurrentProject()
	tlDict = {}
	
	for key in selected:
		item = selected[key].Text[0]
		tlDict[item] = project.GetTimelineByIndex(tlidx(project, item))
	
	pathlist = toqueue.multiply(tlDict)
	
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

	itm["list"].Text = "Projects to search will be listed here."
	itm["grab"].Enabled = False
	itm["clear"].Enabled = False

def _tree(ev):
	
	global toqueue
	selected = itm["browser"].SelectedItems()
	
	for key in selected:
		folder = selected[key].Text[0]

	if selected == {}:
		toqueue.reset()
		projectManager.GotoRootFolder() # Goes to root in project manager 
		projTree()

	elif str(folder) == " * GO TO PARENT FOLDER * ":
		if state == "project":
			projectManager.GotoParentFolder()
		toqueue.pop(-1)
		projTree()
	
	elif projectManager.OpenFolder(str(folder)):	# opens folder if it is selected
		if toqueue == None:
			toqueue = PathMem(str(folder))
		else:
			toqueue.append(str(folder))
		projTree()
		
	elif projectManager.LoadProject(str(folder)):
		toqueue.append(str(folder))
		project = projectManager.GetCurrentProject()
		tlTree(project)
	
	else:
		log("Unknown input", 3)
		

def _main(ev):
	itm["add"].Enabled = False
	itm["grab"].Enabled = False
	itm["clear"].Enabled = False


	createPowergrade()	# create powergrade albume
	# create mem
	
	

	itm["add"].Enabled = True
	itm["grab"].Enabled = True
	itm["clear"].Enabled = True

# needed to close window
def _close(ev):
	disp.ExitLoop()

################################################################################################
# GUI Elements #
# manipulations
itm["timelines"].AddItems(tlLst(projectManager.GetCurrentProject()))
projectManager.GotoRootFolder()
projTree()
# button presses
window.On.GGWin.Close = _close
window.On.browser.ItemDoubleClicked = _tree
window.On.grab.Clicked = _main
window.On.clear.Clicked = _clear
window.On.add.Clicked = _add
# window loops
window.Show()
disp.RunLoop()
window.Hide()
#################################################################################################
