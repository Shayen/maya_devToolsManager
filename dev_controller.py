import os
import sys
import json

from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from Qt import QtCompat

# import maya.cmds as cmds

modulePath = os.path.dirname(__file__)

def setup_ui(uifile, base_instance=None):
	"""Load a Qt Designer .ui file and returns an instance of the user interface
	Args:
		uifile (str): Absolute path to .ui file
		base_instance (QWidget): The widget into which UI widgets are loaded
	Returns:
		QWidget: the base instance
	"""
	ui = QtCompat.loadUi(uifile)  # Qt.py mapped function
	if not base_instance:
		return ui
	else:
		for member in dir(ui):
			if not member.startswith('__') and \
			   member is not 'staticMetaObject':
				setattr(base_instance, member, getattr(ui, member))
		return ui

class dev_tools_controller(QtWidgets.QMainWindow):

	def __init__(self, parent = None):
		super(dev_tools_controller, self).__init__(parent)

		UI_path = modulePath + '/ui/devTools_manager.ui'

		# ---- LoadUI -----
		self.base_instance = setup_ui(UI_path, self)
		# -----------------

		self.config_filePath = modulePath + '/configure.json'

		self._windowName_	= 'Dev hub tool' 
		self._UIname_ 		= 'devHubToolWindow'

		# Load data from dataset
		self.tool_data = self.load_config()

		self.setupUI()

	def setupUI(self):
		''' setup UI '''

		# set main tool page
		impcmd = 'from dev_tools.{module} import {file}\nreload({file})\n{run_cmd}'

		if len(self.tool_data.keys()) > 0 :
			self.label_Placeholder.hide()

			# Create button
			for module in sorted(self.tool_data.keys()) :

				print (module)
				
				runcmd 	 = self.tool_data[module]['runcmd']
				mainfile = self.tool_data[module]['mainfile']


				groupbox = QtWidgets.QGroupBox(self.tab_tools)
				groupbox.setTitle(module)
				layout = QtWidgets.QVBoxLayout(groupbox)
				groupbox.setLayout(layout)
				label = QtWidgets.QLabel(groupbox)
				label.setText("Hello world")
				layout.addWidget(label)

				self.verticalLayout_3.addWidget(groupbox)

			spacer = QtWidgets.QSpacerItem(20,40,QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
			self.verticalLayout_3.addItem(spacer)

			# Delete
			# Note : https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
			# item = self.verticalLayout_3.itemAt(0).widget().deleteLater()
			# print item
			# self.verticalLayout_3.removeItem(item)

		else : 
			self.label_Placeholder.show()

	def load_config(self):
		
		# If not config
		if not os.path.exists(self.config_filePath) :
			sturcture = {}
			self.save_config(sturcture)

		# Load data
		f = open(self.config_filePath, 'r')
		data = json.loads( f.read() )
		f.close()

		# Check recent added module [When have new module]
		allModules = set([i for i in os.listdir(modulePath) \
			if  os.path.isdir (modulePath + '/' + i)  \
			and os.path.exists(modulePath + '/' + i + '/__init__.py')])
		diff_add = list(allModules.difference(set(data.keys()))) # find new module
		diff_rem = list(set(data.keys()).difference(allModules)) # fine not exists module

		if diff_add or diff_rem :

			if diff_add :
				# Add structure and place holder
				for module in diff_add :
					data[module] = {"mainfile":"","runcmd":""}

			if diff_rem :
				# Remove not exists item from data set
				for module in diff_rem :
					data.pop(module)

			self.save_config(data)

		print(data)
		return data

	def save_config(self,data):
		''' write data to configure.json '''
		f = open(self.config_filePath, 'w')
		f.write( json.dumps(data,indent = 2) )
		f.close()

	# def getmodules_Button(self, widget = None):
	# 	impcmd = 'from dev_tools.{module} import {file}\nreload({file})\n{run_cmd}'

	# 	# Create button
	# 	for module in sorted(self.tool_data.keys()) :

	# 		print (module)
			
	# 		runcmd 	 = self.tool_data[module]['runcmd']
	# 		mainfile = self.tool_data[module]['mainfile']
			# cmds.button(l = module,c= impcmd.format(module = module, file = mainfile, run_cmd = runcmd))

	# def tools_tab (self):
	# 	layout = cmds.columnLayout(adj=True)
	# 	cmds.text(l="Dev tools :")

	# 	self.getmodules_Button()

	# 	cmds.setParent("..")

	# 	return layout

	# def setting_tab(self):

	# 	layout = cmds.columnLayout(adj=True)
	# 	cmds.text(l="Setting:")

	# 	for module in sorted(self.tool_data.keys()) :
	# 		cmds.frameLayout(l=module,collapsable=True)
	# 		cmds.rowColumnLayout(nc=2)
	# 		cmds.text(l="mainfile")
	# 		cmds.textField(width = 200, tx= self.tool_data[module]['mainfile'])
	# 		cmds.text(l="runcmd")
	# 		cmds.textField(width = 200, tx= unicode(self.tool_data[module]['runcmd']).replace("\n",'\\n'))
	# 		cmds.setParent("..")
	# 		cmds.setParent("..")

	# 	cmds.button(l="save setting")
	# 	cmds.setParent("..")

	# 	return layout	

	# def clearUI(self):
	# 	if cmds.window(self._UIname_, exists = True):
	# 		cmds.deleteUI(self._UIname_)
	# 		self.clearUI()
	# 	return

	# def show(self):
		
	# 	self.clearUI()

	# 	cmds.window(self._UIname_, title = self._windowName_)
	# 	tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

	# 	tools = self.tools_tab()

	# 	setting = self.setting_tab()

	# 	cmds.tabLayout( tabs, e=True, tabLabel=((tools, 'Tools'), (setting, 'Setting')) )
	# 	cmds.showWindow(self._UIname_)

	# 	cmds.window(self._UIname_, e=True, w= 220)

def run():
	app = dev_tools_controller()
	# app.show()

if __name__ == '__main__':
	print("run")
	# run()

	app = QtWidgets.QApplication(sys.argv)
	form = dev_tools_controller()
	form.show()
	app.exec_()