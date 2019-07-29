import sys, json, os

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from CoverLetterGenerator import Ui_MainWindow
import pyperclip


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
	
	def __init__(self):

		self.variables = {}
		self.templateLetter = ""
		self.words = []
		self.filePath = "/Applications/Template"
		self.JSONPath = "/Applications/Template/variables.json"
		self.letterPath = "/Applications/Template/letter.txt"
		self.firstTime = True

		super(MainWindow, self).__init__()
		self.setupUi(self)
		self.initFile()
		self.initLetterBox()
		self.variablesJSON("Initialize")
		self.updateVariableBox()
		self.variableBoxIndexChanged()
		self.assignWidgetsSlots()
		self.show()


	def initFile(self):
		if not os.path.isdir(self.filePath) or not os.path.exists(self.JSONPath) or not os.path.exists(self.letterPath):
			if not os.path.isdir(self.filePath):
				os.mkdir(self.filePath)
		else:
			self.firstTime = False

	def initLetterBox(self):
		"""
		Initializes the plain text edit box with a template letter or last session's letter.
		"""
		if self.firstTime == True:
			with open(self.resource_path("letter.txt"), "r") as letterTextFile:
				self.templateLetter = letterTextFile.read()
				self.letterInput.setPlainText(self.templateLetter)
		else:
			with open(self.letterPath, "r") as letterTextFile:
				self.templateLetter = letterTextFile.read()
				self.letterInput.setPlainText(self.templateLetter)

	def variablesJSON(self, action):
		"""
		Reads and writes to the variables JSON file
		"""
		if action == "Update":
			with open (self.JSONPath, "w") as data:
				json.dump(self.variables, data)
		elif self.firstTime == True:
			JSONpath = self.resource_path("variables.json")
			with open(JSONpath) as data:
				self.variables = json.load(data)
		else:
			with open(self.JSONPath) as data:
				self.variables = json.load(data)

	def updateVariables(self):
		"""
		Updates the variables dictionary locally in the script.
		"""
		self.words = self.templateLetter.split()
		newVariables = []
		for word in self.words:
			if "<<" in word:
				index = self.words.index(word)
				variable = word.strip("<<>>!,.")
				newVariables.append(variable)
				if variable not in self.variables:
					self.variables[variable] = ""	
					
		for var in list(self.variables.keys()):
			if var not in newVariables:
				del self.variables[var]
				self.variableBox.removeItem(self.variableBox.findText(var))
				
		self.variablesJSON("Update")		
		self.updateVariableBox()	

	def updateVariableBox(self):
		"""
		Updates the variables combo box.
		"""
		for var in self.variables:
			if self.variableBox.findText(var) == -1:
				self.variableBox.addItem(var)
	
	def variableValueChanged(self):
		"""
		Updates the local dictionary with the value changed for a variable. 
		Then uses the variablesJSON method to write to the JSON
		"""
		self.variables[self.variableBox.currentText()] = self.variableEdit.text()
		self.variablesJSON("Update")
		print(self.variables)
		
	def assignWidgetsSlots(self):
		"""
		Assigns slots for widget signals.
		"""
		self.variableBox.currentIndexChanged.connect(self.variableBoxIndexChanged)
		self.variableEdit.textEdited.connect(self.variableValueChanged)
		self.updateButton.clicked.connect(self.updateLetter)
		self.generateButton.clicked.connect(self.generateButtonClicked)
		self.editTemplateButton.clicked.connect(self.editTemplateButtonClicked)

	def variableBoxIndexChanged(self):
		"""
		Sets the line edit with the appropriate value for the combo box variable
		"""
		if self.variableBox.currentText():
			self.variableEdit.setText(self.variables[self.variableBox.currentText()])

	def updateLetter(self):
		self.templateLetter = self.letterInput.toPlainText()
		self.updateVariables()
		with open(self.letterPath, "w") as letterTextFile:
			letterTextFile.write(self.templateLetter)
		self.statusLabel.setText("Letter saved.")

	def generateButtonClicked(self):
		with open(self.letterPath, "w") as letterTextFile:
			letterTextFile.write(self.templateLetter)
		generatedLetter = self.templateLetter.replace("<<", "")
		generatedLetter = generatedLetter.replace(">>", "")
		for variable in self.variables:
			generatedLetter = generatedLetter.replace(variable, self.variables[variable])
		self.letterInput.setPlainText(generatedLetter)
		pyperclip.copy(generatedLetter)
		self.statusLabel.setText("Letter copied to clipboard and saved.")

	def editTemplateButtonClicked(self):
		self.letterInput.setPlainText(self.templateLetter)
		self.statusLabel.setText("You may edit the template. Don't forget to click \"SAVE TEMPLATE LETTER\" once done.")


	def resource_path(self, relative_path):
	    """ Get absolute path to resource, works for dev and for PyInstaller """
	    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
     app = QtWidgets.QApplication(sys.argv)
     mainWin = MainWindow()
     ret = app.exec_()
     sys.exit()