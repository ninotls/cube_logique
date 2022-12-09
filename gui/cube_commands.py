from __future__ import print_function

import sys
import time
import threading
import serial.tools.list_ports

#  List of Cube commands
cube_commands = ["leds", "switches", "rst"]


class GetCubeData(threading.Thread):
    def __init__(self, sleep_time, poll_func):
        self.sleep_time = sleep_time
        self.poll_func = poll_func
        threading.Thread.__init__(self)
        self.run_flag = threading.Event()  # clear this to pause thread
        self.run_flag.clear()
        # response is a byte string, not a string
        self.response = b''

    def run(self):
        self.run_flag.set()
        self.worker()

    def worker(self):
        while 1:
            if self.run_flag.is_set():
                self.poll_func()
                time.sleep(self.sleep_time)
            else:
                time.sleep(0.01)

    def pause(self):
        self.run_flag.clear()

    def resume(self):
        self.run_flag.set()

    def running(self):
        return self.run_flag.is_set()


class HWInterface(object):

    def __init__(self, ser, sleep_time, timeout):
        self.ser = ser
        self.sleep_time = float(sleep_time)
        self.worker = GetCubeData(self.sleep_time, self.poll_hw)
        self.worker.setDaemon(True)
        self.response = None  # last response retrieved by polling
        self.worker.start()
        self.callback = None
        self.timeout = timeout
        self._init_timeout = timeout

    def register_callback(self, proc):
        """Call this function when the hardware sends us serial data"""
        self.callback = proc

    def kill(self):
        self.worker.kill()

    def write_hw(self, command):
        """ Send a command to the hardware"""
        self.ser.write(command.rstrip())
        self.ser.flush()

    def poll_hw(self):
        """Called repeatedly by thread. Check for interlock, if OK read HW
        Stores response in self.response, returns a status code, "OK" if so"""

        data_in = self.ser.inWaiting()
        response = self.ser.read(data_in)
        if response is not None:
            if len(response) > 0:  # did something write to us?
                response = response.strip()  # get rid of newline, whitespace
                if len(response) > 0:  # if an actual character
                    self.response = response
                    sys.stdout.flush()
                    if self.callback:
                        # a valid response so convert to string and call back
                        self.timeout = self._init_timeout
                        self.callback(self.response.decode('utf-8'))
                return "OK"
        return "None"  # got no response

    @staticmethod
    def parse_command(command):
        if len(command) == 0:
            print("Empty command received")
            return

        split_cmd = command.split()
        if split_cmd[0] not in cube_commands:
            print(f"{split_cmd[0]} is not in command list: {cube_commands}")
            return

        return command.encode('utf-8')


class CubeSerial:
    def __init__(self, serial_port, serial_baud):
        self.port_name = serial_port
        self.port_baud = serial_baud
        self.serial = serial.Serial(self.port_name, self.port_baud, timeout=0, write_timeout=0)

    @staticmethod
    def get_all_serial_ports():
        ports = serial.tools.list_ports.comports()
        list_all_ports = []

        for port, _, _ in sorted(ports):
            list_all_ports.append(port)

        return list_all_ports
