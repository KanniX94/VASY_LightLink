from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import ZigBeeDevice
from digi.xbee.devices import RemoteZigBeeDevice
from digi.xbee.devices import XBee64BitAddress
from digi.xbee.models.mode import APIOutputModeBit
from digi.xbee.util import utils

device = ZigBeeDevice("COM11", 9600)

switch_endpoint = 0x11

device_switch_controller_id = 0x0840
switch_cluster_id = {"Identify": 0x00, "Groups": 0x01, "Scenes": 0x02,
                     "On/Off": 0x03, "Level control": 0x04, "Color control": 0x05}

light_endpoint = 0x11

device_light_id = 0x0000
light_cluster_id = {"Identify": 0x00, "Groups": 0x01, "Scenes": 0x02, "On/Off": 0x03}
light_commands = {"Off": "0x00", "On": "0x01", "Toggle": "0x02"}

device_dim_id = 0x0100
dim_cluster_id = {"Identify": 0x00, "Groups": 0x01, "Scenes": 0x02,
                  "On/Off": 0x03, "Level control": 0x04}
dim_commands = {"Move to Level": "0x00", "Move": "0x01", "Step": "0x02",
                "Stop": "0x03", "Move to Level(with On/Off)": "0x04",
                "Move (with On/Off": "0x05", "Step (with On/Off)": "0x06"}

device.open()


xbee_network = device.get_network()

remote_device = RemoteZigBeeDevice(device, XBee64BitAddress.from_hex_string("0013A20041948C1A"))

print("Connected with device: ")
print(remote_device)
if remote_device is None:
    print("Timeout...")
    exit(1)

data = ""

while True:
    print()
    print("How to control..")
    print()
    print("Dim light: ")
    print("duty (0-1023) + transitiontime in s, separate with ','")
    print()
    print("Toggle user LED: ")
    print("on, off, toggle")
    key_input = input()
    if key_input.isdecimal():
        key_input = key_input + "," + "0"
    key_input = key_input.split(',')
    if key_input[0] == 'on':
        print("Turn light status on")
        data = light_commands["On"] + "," + "0"
        device.send_expl_data(remote_xbee_device=remote_device, data=data,
                              src_endpoint=switch_endpoint, dest_endpoint=light_endpoint,
                              cluster_id=light_cluster_id["On/Off"], profile_id=device_light_id)
    elif key_input[0] == "off":
        print("Turn light status off")
        data = light_commands["Off"] + "," + "1"
        device.send_expl_data(remote_xbee_device=remote_device, data=data,
                              src_endpoint=switch_endpoint, dest_endpoint=light_endpoint,
                              cluster_id=light_cluster_id["On/Off"], profile_id=device_light_id)
    elif key_input[0] == "toggle":
        print("Toggle light")
        data = light_commands["Toggle"] + "," + "1"
        device.send_expl_data(remote_xbee_device=remote_device, data=data,
                              src_endpoint=switch_endpoint, dest_endpoint=light_endpoint,
                              cluster_id=light_cluster_id["On/Off"], profile_id=device_light_id)
    elif key_input[0].isdecimal() and key_input[1].isdecimal():
        print("Dim light to next value")
        print(key_input)
        data = dim_commands["Move to Level(with On/Off)"] + "," + key_input[0] + "," + key_input[1]
        print(data)
        device.send_expl_data(remote_xbee_device=remote_device, data=data,
                              src_endpoint=switch_endpoint, dest_endpoint=light_endpoint,
                              cluster_id=dim_cluster_id["Level control"], profile_id=device_dim_id)
    elif key_input[0] == "exit":
        break
        
    else:
        print("None valid command. Check out how to control!")

    print("")


device.close()