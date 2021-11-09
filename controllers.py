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
                set_temperature = self.tc720.get_set_temp()
                temperature_1 = self.tc720.get_temp()
                temperature_2 = self.tc720.get_temp2()
                output = self.tc720.get_output()
                print([set_temperature,temperature_1,temperature_2,output])
                self.signal_readings.emit([self.set_temperature,temperature_1,temperature_2,output])
                self.lock.release()
            else:
                pass

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

    def update_controller_parameter(self,method_name,parameters):
        self.queue_parameter_update_command.put((method_name,parameters))

    def _update_controller_parameter(self,method_name,parameters):
        method = getattr(self.tc720,method_name)
        method(*parameters)

    '''
    def test_fucntion(self,args):
        print('executing the test function')
        self.test_function2(*args)

    def test_function2(self,arg1,arg2,arg3):
        print(arg1)
        print(arg2)
        print(arg3)
    '''
