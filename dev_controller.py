import os
import sys
import json
import subprocess
import traceback

from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from Qt import QtCompat

import syntax
reload(syntax)

import maya.cmds as cmds

try :
	import shiboken as sbk
except ImportError :
	import shiboken2 as sbk

import maya.OpenMayaUI as apiUI

modulePath = os.path.dirname(__file__)

__windowTitle__ = 'Dev hub tool'
__UIName__		= 'devHubToolWindow'
config_filePath = modulePath + '/configure.json'

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

class tool_widget(QtWidgets.QWidget):

	tool_command = str()
	location 	 = str()

	saveSetting = QtCore.Signal(str)

	def __init__(self,  parent = None, modulename = '', command = '', location = ''):
		super(tool_widget, self).__init__(parent)
		# QtWidgets.QWidget.__init__(parent)

		self.parent = parent
		self.tool_command = command
		self.modulename = modulename

		self.setupUi()
		self.initConnection()

	def setupUi(self):

		# ===================== MAIN WIDGET =====================
		self.horizontalLayout = QtWidgets.QHBoxLayout( self )
		self.groupbox = QtWidgets.QGroupBox(self)
		self.layout = QtWidgets.QVBoxLayout(self.groupbox)

		self.H_layout = QtWidgets.QHBoxLayout( self)
		self.label 	= QtWidgets.QLabel(self)
		self.openLocation = QtWidgets.QPushButton(self.groupbox)
		self.openLocation.setText("Open folder")

		self.groupbox.setLayout(self.layout)
		self.luanch_button = QtWidgets.QPushButton(self)
		self.luanch_button.setText("Luanch")
		self.setting_button= QtWidgets.QPushButton(self)
		self.setting_button.setIcon(QtGui.QIcon(modulePath + '/icon/gear.png'))
		
		self.H_layout.addWidget(self.label)
		self.H_layout.addWidget(self.openLocation)
		self.H_layout.addWidget(self.setting_button)
		self.layout.addLayout(self.H_layout)
		self.layout.addWidget(self.luanch_button)
		self.horizontalLayout.addWidget(self.groupbox)

		self.H_layout.setStretchFactor(self.label, 1)

		# Setup stylesheet
		luanch_button_styleSheet = \
		'''
		QPushButton:disabled {background-color:#3f3f3f;
		color: #757575;}
		QPushButton{color : black ;background-color: #b8ff2b;
		font-style : bold;border: none;
		}
		'''
		self.luanch_button.setStyleSheet(luanch_button_styleSheet)
		self.luanch_button.setMinimumHeight(30)

		self.groupbox.setStyleSheet('''QGroupBox {font: bold;}''')

		# ===================== SETTING WIDGET =====================
		self.setting_widget = QtWidgets.QWidget()
		self.setting_widget.resize(450, 400)
		setting_V_layout = QtWidgets.QVBoxLayout( self.setting_widget )
		setting_locationLabel = QtWidgets.QLabel(self.setting_widget)
		setting_locationLabel.setText("Location :")
		self.setting_location = QtWidgets.QLineEdit(self.setting_widget)
		setting_label = QtWidgets.QLabel(self.setting_widget)
		setting_label.setText("command :")
		self.setting_commandEditor = QtWidgets.QTextEdit(self.setting_widget)
		self.setting_commandEditor.setWordWrapMode(QtGui.QTextOption.NoWrap)
		self.setting_commandEditor.setPlainText(self.tool_command)
		self.setting_saveSetting = QtWidgets.QPushButton(self.setting_widget)
		self.setting_saveSetting.setText("save setting")

		setting_V_layout.addWidget(setting_locationLabel)
		setting_V_layout.addWidget(self.setting_location)
		setting_V_layout.addWidget(setting_label)
		setting_V_layout.addWidget(self.setting_commandEditor)
		setting_V_layout.addWidget(self.setting_saveSetting)

		highlight = syntax.PythonHighlighter(self.setting_commandEditor.document())

		if self.tool_command == '':
			self.luanch_button.setEnabled(False)

	def initConnection(self):
		''' Initial connection in Widget '''

		# Main widget
		self.luanch_button.clicked.connect(self.__runCommand  )
		self.openLocation.clicked.connect( self.__openExplorer)
		self.setting_button.clicked.connect(self.call_settingWindow)

		# setting widget
		self.setting_saveSetting.clicked.connect(self.__updateCommand)

	def __updateCommand(self):
		''' update command to '''
		raw_data = self.parent.tool_data

		command  = self.setting_commandEditor.toPlainText()
		location = self.setting_location.text()

		# Update
		raw_data['tools'][self.modulename]['runcmd'] = command
		raw_data['tools'][self.modulename]['location'] = location

		save_config(config_filePath, raw_data)

	def call_settingWindow(self):
		''' open setting window '''
		self.setting_widget.show()

	def setTitle(self, title):
		self.groupbox.setTitle(title)
		self.modulename = title

	def setLinkStatus(self, is_link = False):

		if is_link and self.tool_command != '':
			status = "Status : Linked"
			pixmap = QtGui.QPixmap( modulePath + '/icon/linked.png')
			self.label.setPixmap(pixmap)
		else :
			status = "Status : Not linked"
			pixmap = QtGui.QPixmap( modulePath + '/icon/unlinked.png')
			self.label.setPixmap(pixmap)

		# self.label.setText(status)

	def setCommand(self, command):
		self.tool_command = command

	def setLocation(self,location):
		self.location = location
		self.setting_location.setText(location)

	def __openExplorer(self):
		"""Open File explorer after finish."""
		pathTofolder = self.location.replace('/', '\\')
		subprocess.Popen('explorer \/select,\"%s\"' % pathTofolder)

	def __runCommand(self):
		''' Run given command '''
		if self.tool_command == '':
			print ("Please set up command")
			return

		try:
			print(self.tool_command)
			exec(self.tool_command)
		except Exception as e:
			print('\n============ ERROR ============\n')
			traceback.print_exc()
			print(str(e) + "\nPlease check your tool's setting.")

class dev_tools_controller(QtWidgets.QWidget):

	def __init__(self, parent = None):
		super(dev_tools_controller, self).__init__(parent)
		# QtWidgets.QMainWindow.__init__(parent)

		UI_path = modulePath + '/ui/devTools_manager.ui'

		# ---- LoadUI -----
		self.base_instance = setup_ui(UI_path, self)
		# -----------------

		# print self.base_instance

		self._windowName_	= __windowTitle__
		self._UIname_ 		= __UIName__

		# Load data from dataset
		self.tool_data = load_config(config_filePath)

		self.__setupPythonPath()
		self.__setupUI()
		self.__initConnect()

	def __setupPythonPath(self):
		''' Append container's location path to PythonPath '''

		if not self.tool_data['setting']['container_path'] in sys.path:
			sys.path.append(self.tool_data['setting']['container_path'])

	def __refresh(self):
		''' Refresh data '''
		self.tool_data = load_config(config_filePath)
		self.__setupPythonPath()

		# Clear tools list widget
		self.tools_listWidget.clear()
		# Re-setui UI
		self.__setupUI()

	def __setupUI(self):
		''' setup UI '''

		self.pushButton_refresh.setIcon(QtGui.QIcon(modulePath + "/icon/refresh.png"))

		# ===== set main tool page =====
		# Create button
		for module in sorted(self.tool_data["tools"].keys()) :

			print (module)
			
			runcmd 	 = self.tool_data["tools"][module]['runcmd']
			location = self.tool_data["tools"][module]['location']

			# tools_listWidget
			item = QtWidgets.QListWidgetItem(self.tools_listWidget)

			item_widget = tool_widget( parent = self, modulename = module, command = runcmd)
			item_widget.setTitle(module)
			item_widget.setLinkStatus(self.checkLinkStatus(modulename = module, modulePath = location))
			item_widget.setLocation(location)

			item.setSizeHint( item_widget.sizeHint() )
			self.tools_listWidget.addItem( item )
			self.tools_listWidget.setItemWidget( item, item_widget)

		# ===== Setup Setting page =====
		self.lineEdit_location.setText(self.tool_data['setting']['container_path'])

	def __initConnect(self):
		''' Initial connection '''

		self.pushButton_saveSetting.clicked.connect(self.pushButton_saveSetting_onClicked)
		self.pushButton_refresh.clicked.connect(self.__refresh)
		self.pushButton_location_openExplorer.clicked.connect(self.pushButton_location_openExplorer_onClicked)

	def checkLinkStatus(self,modulename, modulePath):

		return True

	def pushButton_saveSetting_onClicked(self):
		# Get corrent data

		# Get location
		location = self.lineEdit_location.text()

		# Update data
		self.tool_data['setting']['container_path'] = location

		save_config(config_filePath, self.tool_data)

	def pushButton_location_openExplorer_onClicked(self):
		dialog = QtWidgets.QFileDialog(self.base_instance)
		dialog.setFileMode(QtWidgets.QFileDialog.Directory)
		dialog.setViewMode(QtWidgets.QFileDialog.Detail)
		if dialog.exec_():
			fileNames = dialog.selectedFiles()

			print self.lineEdit_location.setText(fileNames[0])

# #####################################################################

def load_config(config_filePath):
	
	# If not config
	if not os.path.exists(config_filePath) :
		sturcture = {'setting':{'container_path':''},'tools':{}}
		save_config(config_filePath, sturcture)

	# Load data
	f = open(config_filePath, 'r')
	data = json.loads( f.read() )
	f.close()

	try:
		containerPath = data['setting']['container_path']
	except KeyError :

		if not data.has_key('setting') :
			data['setting'] = {'container_path':''}

		containerPath = data['setting']['container_path']

	if not os.path.exists(containerPath):
		containerPath = os.path.dirname(__file__)

	# Check recent added module [When have new module]
	allModules = set([i for i in os.listdir(containerPath) \
		if  os.path.isdir (containerPath + '/' + i)  \
		and os.path.exists(containerPath + '/' + i + '/__init__.py')])
	diff_add = list(allModules.difference(set(data["tools"].keys()))) # find new module
	diff_rem = list(set(data["tools"].keys()).difference(allModules)) # fine not exists module

	if diff_add or diff_rem :

		if diff_add :
			# Add structure and place holder
			for module in diff_add :
				location = containerPath + '/' + module
				data["tools"][module] = {"runcmd":"","location":location}

		if diff_rem :
			# Remove not exists item from data set
			for module in diff_rem :
				data['tools'].pop(module)

		save_config(config_filePath,data)

	print(data)
	return data

def save_config(config_filePath,data):
	''' write data to configure.json '''
	f = open(config_filePath, 'w')
	f.write( json.dumps(data,indent = 2) )
	f.close()

	print("Update data:\n" + json.dumps(data,indent = 2))

def getMayaWindow():
	"""
	Get the main Maya window as a QMainWindow instance
	@return: QMainWindow instance of the top level Maya windows
	"""
	ptr = apiUI.MQtUtil.mainWindow()
	if ptr is not None:
		return sbk.wrapInstance(long(ptr), QtWidgets.QMainWindow)

def clearUI():
	if cmds.window(__UIName__, exists=True):
		cmds.deleteUI(__UIName__)
		clearUI()

def run():
	clearUI()
	app = dev_tools_controller( getMayaWindow() )
	app.show()

if __name__ == '__main__':
	print("run")
	# run()

	app = QtWidgets.QApplication(sys.argv)
	form = dev_tools_controller(getMayaWindow())
	form.show()
	app.exec_()