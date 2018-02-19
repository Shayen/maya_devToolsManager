import os
import sys
import json

import maya.cmds as cmds

modulePath = os.path.dirname(__file__)

class dev_tools_controller(object):

	def __init__(self):
		self.config_filePath = modulePath + '/configure.json'

		self._windowName_	= 'Dev hub tool' 
		self._UIname_ 		= 'devHubToolWindow'

		# Load data from dataset
		self.tool_data = self.load_config()

	def load_config(self):
		
		# If not config
		if not os.path.exists(self.config_filePath) :
			sturcture = {}
			f = open(self.config_filePath, 'w')
			f.write( json.dumps(sturcture,indent = 2) )
			f.close()

		# Load data
		f = open(self.config_filePath, 'r')
		data = json.loads( f.read() )
		f.close()

		# Check recent added module [When have new module]
		allModules = set([i for i in os.listdir(modulePath) if os.path.isdir(modulePath + '/' + i)])
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

			f = open(self.config_filePath, 'w')
			f.write( json.dumps(data,indent = 2) )
			f.close()

		return data

	def getmodules_Button(self):
		impcmd = 'from dev_tools.{module} import {file}\nreload({file})\n{run_cmd}'

		# Create button
		for module in sorted(self.tool_data.keys()) :
			
			runcmd 	 = self.tool_data[module]['runcmd']
			mainfile = self.tool_data[module]['mainfile']
			cmds.button(l = module,c= impcmd.format(module = module, file = mainfile, run_cmd = runcmd))

	def tools_tab (self):
		layout = cmds.columnLayout(adj=True)
		cmds.text(l="Dev tools :")

		self.getmodules_Button()

		cmds.setParent("..")

		return layout

	def setting_tab(self):

		layout = cmds.columnLayout(adj=True)
		cmds.text(l="Setting:")

		for module in sorted(self.tool_data.keys()) :
			cmds.frameLayout(l=module,collapsable=True)
			cmds.rowColumnLayout(nc=2)
			cmds.text(l="mainfile")
			cmds.textField(width = 200, tx= self.tool_data[module]['mainfile'])
			cmds.text(l="runcmd")
			cmds.textField(width = 200, tx= self.tool_data[module]['runcmd'])
			cmds.setParent("..")
			cmds.setParent("..")

		cmds.button(l="save setting")
		cmds.setParent("..")

		return layout	

	def clearUI(self):
		if cmds.window(_UIname_, exists = True):
			cmds.deleteUI(_UIname_)
			clearUI()
		return

	def show(self):
		
		clearUI()

		cmds.window(self._UIname_, title = self._windowName_)
		tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

		tools = tools_tab()

		setting = setting_tab()

		cmds.tabLayout( tabs, e=True, tabLabel=((tools, 'Tools'), (setting, 'Setting')) )
		cmds.showWindow(_UIname_)

		cmds.window(_UIname_, e=True, w= 220)

def run():
	app = dev_tools_controller()
	app.show()
