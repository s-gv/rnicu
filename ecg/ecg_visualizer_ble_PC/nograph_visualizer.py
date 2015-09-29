import CC2540ble as ble

def main():
    print "Connecting to BLE Dongle . . ."
    bt = ble.BTDongle(port='/dev/ttyACM0')

    print "Discovering BLE devices in the vicinity . . ."
    devs = bt.discover()
    print "BLE Devices found: ", devs

    print "Changing conncection parameters . . ."
    bt.changeConnectionSettings()

    print "Establishing link to the first device found . . ."
    print bt.link(devs[0])

    print "Enabling notifications . . ."
    print bt.enableNotifications('0x002F')

    for evt in bt.pollNotifications():
        if len(evt) == 16:
            f2s = lambda x: x if x < 2**13 or x >= 65530 else (-2**14 + x)
            vals = [ f2s(lsb + 256*msb) for (lsb, msb) in zip(evt[::2], evt[1::2]) ]
            vals = [ val for val in vals if val < 65530 ]
            print vals

if __name__ == '__main__':
    main()
