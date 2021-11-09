# set QT_API environment variable
import os 
os.environ["QT_API"] = "pyqt5"
import qtpy

# qt libraries
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *

import controllers
import widgets

class GUI(QMainWindow):

	def __init__(self, is_simulation = False, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.tc720Controller = controllers.TC720Controller(serial_number='AH05OQGC',is_simulation=is_simulation)

		# widget
		self.controlPanel = widgets.ControlPanel()
		self.waveformDisplay = widgets.WaveformDisplay()

		# lay out widgets
		layout = QHBoxLayout()
		layout.addWidget(self.waveformDisplay)
		layout.addWidget(self.controlPanel)
		self.centralWidget = QWidget()
		self.centralWidget.setLayout(layout)
		self.setCentralWidget(self.centralWidget)

		# connections
		self.controlPanel.signal_tc720_parameter_update_command.connect(self.tc720Controller.update_controller_parameter)
		self.tc720Controller.signal_readings.connect(self.controlPanel.display_readings)
		self.tc720Controller.signal_plots.connect(self.waveformDisplay.plot)

		# start
		self.tc720Controller.start()

	def closeEvent(self, event):
		event.accept()