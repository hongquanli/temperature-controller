# qt libraries
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *

import TC720
import time
import threading
import numpy as np
import queue

class TC720Controller(QObject):

    signal_readings = Signal(list)
    signal_plots = Signal(np.ndarray,np.ndarray)

    def __init__(self, serial_number=None,is_simulation=False):
        QObject.__init__(self)

        # initialize the TC720 controller
        if is_simulation == False:
            self.tc720 = TC720.TC720(serial_number=serial_number)
        else:
            self.tc720 = TC720.TC720_simulation(serial_number=serial_number)

        # inti. the controller
        self.tc720.set_sensor1_choice(1) # 10 kΩ thermistor, type 1 (TS-91)
        self.tc720.set_sensor2_choice(1) # 10 kΩ thermistor, type 1 (TS-91)

        # controller parameters
        self.set_temperature = 20

        # logging and plotting
        self.t_array = np.array([])
        self.set_temperature_array = np.array([])
        self.temperature1_array = np.array([])
        self.temperature2_array = np.array([])
        self.output_array = np.array([])

        # queue for updating parameters
        self.queue_parameter_update_command = queue.Queue()

        # read and write threads
        self.lock = threading.Semaphore()
        self.terminate_the_reading_thread = False
        self.terminate_the_writing_thread = False
        self.writing_lock_requested = False
        self.thread_read = threading.Thread(target=self.read_temperature_and_output, daemon=True)
        self.thread_write = threading.Thread(target=self.send_parameter_update_commands, daemon=True)
        
    def start(self):
        self.thread_read.start()
        self.thread_write.start()

    def read_temperature_and_output(self):
        while(self.terminate_the_reading_thread == False):
            if self.writing_lock_requested == False:
                self.lock.acquire()
                # get readings
                # set_temperature = self.tc720.get_set_temp()
                set_temperature = self.set_temperature
                temperature_1 = self.tc720.get_temp()
                temperature_2 = self.tc720.get_temp2()
                output = self.tc720.get_output()
                # build arrays
                self.t_array = np.append(self.t_array,time.time())
                self.set_temperature_array = np.append(self.set_temperature_array,set_temperature)
                self.temperature1_array = np.append(self.temperature1_array,temperature_1)
                self.temperature2_array = np.append(self.temperature2_array,temperature_2)
                self.output_array = np.append(self.output_array,output)
                # plot
                plot_arrays = np.vstack((self.set_temperature_array,self.temperature1_array,self.temperature2_array,self.output_array))
                self.signal_plots.emit(self.t_array,plot_arrays)
                # print([set_temperature,temperature_1,temperature_2,output])
                self.signal_readings.emit([self.set_temperature,temperature_1,temperature_2,output])
                self.lock.release()
            else:
                pass
            time.sleep(0.1)

    def send_parameter_update_commands(self):
        while(self.terminate_the_writing_thread == False):
            while self.queue_parameter_update_command.empty() == False:
                # update the controller
                self.writing_lock_requested = True
                self.lock.acquire()
                self.writing_lock_requested = False
                method_name,parameters = self.queue_parameter_update_command.get()
                self._update_controller_parameter(method_name,parameters)
                self.lock.release()
                # update the controller object
                if method_name == 'set_temp':
                    self.set_temperature = parameters[0]
            time.sleep(0.1)

    def update_controller_parameter(self,method_name,parameters):
        self.queue_parameter_update_command.put((method_name,parameters))

    def _update_controller_parameter(self,method_name,parameters):
        method = getattr(self.tc720,method_name)
        method(*parameters)

    def close(self):
        self.terminate_the_reading_thread = True
        self.terminate_the_writing_thread = True
        self.thread_read.join()
        self.thread_write.join()

