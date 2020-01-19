from machine import Pin, PWM
import time
import xbee

usrLed = Pin("D4", Pin.OUT, value=1)
dimLed = PWM("P0", duty=0)

endpoint = 0x11

lightClusterId = {"Identify": 0x00, "Groups": 0x01, "Scenes": 0x02, "On/Off": 0x03}
lightCommand = {"Off": 0x00, "On": 0x01, "Toggle": 0x02}

payload = ""
transition_time = 0

dimClusterId = {"Identify": 0x00, "Groups": 0x01, "Scenes": 0x02,
                "On/Off": 0x03, "Level control": 0x04}
dimCommand = {"Move to Level": 0x00, "Move": 0x01, "Step": 0x02,
              "Stop": 0x03, "Move to Level(with On/Off)": 0x04,
              "Move (with On/Off": 0x05, "Step (with On/Off)": 0x06}


def dim(destEndpoint, clusterId, command, nextLevel, transitionTime):
    if destEndpoint == endpoint:
        step = 0
        delta = 1

        if clusterId == dimClusterId["Level control"]:
            if command == dimCommand["Move to Level(with On/Off)"]:
                print("Light is dimming right now")
                level = int(nextLevel) - dimLed.duty()
                if level < 0:
                    delta = -1
                    level = -level
                if level != 0:
                    step = (transitionTime / level) / 1000
                else:
                    step = 0

                if transitionTime == 0:
                    dimLed.duty(int(nextLevel))
                else:
                    while dimLed.duty() != int(nextLevel):
                        if 0 <= dimLed.duty() + delta <= 1023:
                            dimLed.duty((dimLed.duty() + delta))
                            time.sleep(step/1000)
                        elif dimLed.duty() + delta < 0:
                            dimLed.duty(0)
                            break
                        elif dimLed.duty() + delta > 1023:
                            dimLed.duty(1023)
                            break

                    print("Finished")


def light(destEndpoint, clusterId, command, value, transitionTime):
    if destEndpoint == endpoint:
        print(command)
        if clusterId == lightClusterId["On/Off"]:
            if command == lightCommand["Off"] or command == lightCommand["On"]:
                usrLed.value(value)
            else:
                usrLed.toggle()


deviceFunc = {0x0000: light, 0x0100: dim}

print(" +--------------------------------------+")
print(" | XBee MicroPython Dimming LED |")
print(" +--------------------------------------+\n")

while True:
    transitionTime = 0
    received_msg = xbee.receive()
    if received_msg:
        print("Message received")
        if received_msg['source_ep'] == 0x11:
            f = deviceFunc[received_msg['profile']]
            payload = received_msg['payload']
            payload = payload.decode("utf8")
            data = payload.split(",")
            print("Received data...")
            for i in data:
                print(i)
            print("Payload len")
            print(len(data))
            if len(data) == 3:
                transitionTime = int(data[2])
                print(transitionTime)
            f(received_msg['dest_ep'], received_msg['cluster'], int(data[0]), int(data[1]), transitionTime)
