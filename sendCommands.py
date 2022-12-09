from __future__ import print_function

import serial
import serial.tools.list_ports
import sys
import getopt
import time
import threading

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

    def __init__(self, ser, sleep_time, timeout=30):
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
                        self.callback(self.response.decode("utf-8", 'ignore'))
                return "OK"
        return "None"  # got no response


def my_callback(response):
    """example callback function to use with HW_interface class.
       Called when the target sends a byte, just print it out"""
    res_split = response.split("\n")
    for data in res_split:
        print(f"Cube Logique: {data}")


def parse_command(command):
    if len(command) == 0:
        print("Empty command received")
        return

    if type(command) == str:
        split_cmd = command.split()
        if split_cmd[0] not in cube_commands:
            print(f"{command} is not in command list: {cube_commands}")
            return

        return command.encode('utf-8', 'ignore')

    val = b''
    for i in command:
        val += bytes(i, 'utf-8')
        val += b' '
    val = val.rstrip()

    split_cmd = val.decode('utf-8', 'ignore').split()

    if split_cmd[0] not in cube_commands:
        print(f"{split_cmd[0]} is not in command list: {cube_commands}")
        return

    return val


def get_all_serial_ports():
    ports = serial.tools.list_ports.comports()
    list_all_ports = []

    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
        list_all_ports.append(tuple((port, desc)))

    return list_all_ports


def main(argv):
    command = None
    get_all_serial_ports()
    try:
        opts, args = getopt.getopt(argv, "c:", ["cmd="])
    except getopt.GetoptError:
        print('sendCommands.pi -c <command> <option>')
        print(f'cube_commands are {cube_commands}')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('sendCommands.pi -c <command>')
            print(f'cube_commands are {cube_commands}')
            sys.exit()
        elif opt in ("-c", "--cmd"):
            command = arg

    for data in args:
        command += " "
        command += data

    port_name = "/dev/cu.usbserial-114130"
    port_baud = "115200"
    ser = serial.Serial(port_name, port_baud, timeout=0, write_timeout=0)
    # timeout=0 means "non-blocking," ser.read() will always return, but
    # may return a null string.
    print("opened port " + port_name + " at " + str(port_baud) + " baud")

    sys.stdout.flush()
    hw = HWInterface(ser, 0.1, 15)

    # when class gets data from the Arduino, it will call the my_callback function
    hw.register_callback(my_callback)

    if not command:
        print("Console mode.")
        print("Commands:")
        print("  c <str> to send command <str>")
        print("  x to exit ")

        while 1:
            sys.stdout.flush()
            cmd = input('--> ')
            cmd = cmd.split()
            sys.stdout.flush()

            if not cmd:
                continue

            if cmd[0] == 'c':
                cmd = cmd[1:]
                if not cmd:
                    print(f"Commands are: {cube_commands}")
                    continue

                val = parse_command(cmd)
                if not val:
                    print("Command not sent")
                    continue
                print(f"Sending command {val.decode('utf-8', 'ignore')}")
                sys.stdout.flush()

                hw.write_hw(val)

            elif cmd[0] == 'x':
                print("Exiting...")
                exit()

            else:
                print("No such command: " + ' '.join(cmd))
    else:
        print(f"Command line mode with {hw.timeout} seconds")
        print(f"Received Command: {command}")
        val = parse_command(command)
        if val:
            time.sleep(5)
            print(f"Sending command {val.decode('utf-8', 'ignore')}")
            sys.stdout.flush()

            hw.write_hw(val)
            while hw.timeout > 0:
                time.sleep(1)
                hw.timeout -= 1

        else:
            print(f"Error parsing command {command}")


if __name__ == '__main__':
    main(sys.argv[1:])
