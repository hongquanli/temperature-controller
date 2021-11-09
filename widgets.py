# set QT_API environment variable
import os 
os.environ["QT_API"] = "pyqt5"
import qtpy

# qt libraries
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *

import numpy as np
import pyqtgraph as pg
from collections import deque
import time

NUMBER_OF_CHANNELS_DISPLAY = 4
pg.setConfigOptions(antialias=True)

class ControlPanel(QFrame):

	signal_logging_onoff = Signal(bool,str)
	signal_tc720_parameter_update_command = Signal(str,list)

	def __init__(self, main=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.font = QFont()
		self.font.setPixelSize(16)
		self.add_components()
		self.setFrameStyle(QFrame.Panel | QFrame.Raised)

	def add_components(self):

		# logging
		self.lineEdit_experimentID = QLineEdit()
		self.btn_logging_onoff = QPushButton('Logging On/Off')
		self.btn_logging_onoff.setDefault(False)
		self.btn_logging_onoff.setCheckable(True)
		self.btn_logging_onoff.setChecked(True)

		grid_line2 = QHBoxLayout()
		grid_line2.addWidget(QLabel('File Prefix'))
		grid_line2.addWidget(self.lineEdit_experimentID)
		grid_line2.addWidget(self.btn_logging_onoff)

		# settings
		self.entry_set_temperature = QDoubleSpinBox()
		self.entry_set_temperature.setMinimum(-20)
		self.entry_set_temperature.setMaximum(60) 
		self.entry_set_temperature.setSingleStep(0.1)
		self.entry_set_temperature.setValue(20)
		self.btn_update_set_temperature = QPushButton('Update')
		self.btn_enable_output = QPushButton('Enable Output')
		self.btn_enable_output.setCheckable(True)
		
		grid_line3 = QGridLayout()
		grid_line3.addWidget(QLabel('Set Temperature'),0,0)
		grid_line3.addWidget(self.entry_set_temperature, 0,1)
		grid_line3.addWidget(self.btn_update_set_temperature,0,10)
		grid_line3.addWidget(self.btn_enable_output,10,0,1,11)

		# readings
		self.label_channel_readings = {}
		for i in range(NUMBER_OF_CHANNELS_DISPLAY):
			self.label_channel_readings[str(i)] = QLabel()
			self.label_channel_readings[str(i)].setFrameStyle(QFrame.Panel | QFrame.Sunken)
			self.label_channel_readings[str(i)].setFixedWidth(50)

		grid_line4 = QGridLayout()
		grid_line4.addWidget(QLabel('Set Temperature'),0,0)
		grid_line4.addWidget(self.label_channel_readings[str(0)],0,1)
		grid_line4.addWidget(QLabel('Temperature 1'),1,0)
		grid_line4.addWidget(self.label_channel_readings[str(1)],1,1)
		grid_line4.addWidget(QLabel('Temperature 2'),2,0)
		grid_line4.addWidget(self.label_channel_readings[str(2)],2,1)
		grid_line4.addWidget(QLabel('Output'),3,0)
		grid_line4.addWidget(self.label_channel_readings[str(3)],3,1)
		
		# widget arrangement
		self.grid = QVBoxLayout()
		self.grid.addLayout(grid_line3)
		self.grid.addLayout(grid_line4)
		self.grid.addStretch()
		self.grid.addLayout(grid_line2)
		# self.grid.addWidget(self.label_channel_readings_print,3,0,1,8)

		self.setLayout(self.grid)

		# connections
		self.btn_logging_onoff.clicked.connect(self.logging_onoff)
		self.btn_update_set_temperature.clicked.connect(self.update_set_temperature)
		self.btn_enable_output.clicked.connect(self.update_output_enable)

	def logging_onoff(self,state):
		self.signal_logging_onoff.emit(state, self.lineEdit_experimentID.text())

	def display_readings(self,readings):
		for i in range(NUMBER_OF_CHANNELS_DISPLAY):
			self.label_channel_readings[str(i)].setText(str(readings[i]))

	def update_set_temperature(self):
		self.signal_tc720_parameter_update_command.emit('set_mode',[0]) # get into the normal set mode
		self.signal_tc720_parameter_update_command.emit('set_control_type',[0]) # get into the PID mode
		self.signal_tc720_parameter_update_command.emit('set_temp',[self.entry_set_temperature.value()])

	def update_output_enable(self,enable):
		self.signal_tc720_parameter_update_command.emit('set_output_enable',[int(enable)]) # get into the normal set mode


class WaveformDisplay(QFrame):

	def __init__(self, main=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.add_components()
		self.setFrameStyle(QFrame.Panel | QFrame.Raised)

	def add_components(self):
		self.plotWidget = {}
		self.plotWidget['Temperature'] = PlotWidget('Temperature',add_legend=True)
		self.plotWidget['Output'] = PlotWidget('Output')

		layout = QGridLayout() #layout = QStackedLayout()
		layout.addWidget(self.plotWidget['Temperature'],0,0)
		layout.addWidget(self.plotWidget['Output'],1,0)
		self.setLayout(layout)

	def plot(self,time,data):
		self.plotWidget['Temperature'].plot(time,data[0,:],'Set Temperature',color=(255,255,255),clear=True)
		self.plotWidget['Temperature'].plot(time,data[1,:],'Temperature 1',color=(255,200,0))
		self.plotWidget['Temperature'].plot(time,data[2,:],'Temperature 2',color=(200,255,0))
		self.plotWidget['Output'].plot(time,data[3,:],'Output',color=(200,200,200),clear=True)

class PlotWidget(pg.GraphicsLayoutWidget):
	
	def __init__(self, title='',parent=None,add_legend=False):
		super().__init__(parent)
		self.plotWidget = self.addPlot(title = '', axisItems = {'bottom': pg.DateAxisItem()})
		if add_legend:
			self.plotWidget.addLegend()
	
	def plot(self,x,y,label,color,clear=False):
		self.plotWidget.plot(x[-1000:],y[-1000:],pen=pg.mkPen(color=color,width=2),name=label,clear=clear)
		# self.plotWidget.plot(x,y,clear=True)
		# self.plotWidget.plot(np.random.rand(10),pen=(0,3),clear=True)
		print('plot ' + label)
