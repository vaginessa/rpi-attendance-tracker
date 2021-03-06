#/usr/bin/env python

#################################################################################
# Import libraries
#################################################################################
import evdev # lib for keyboard input event detection

#################################################################################
# Perform initializations
#################################################################################
KEY_STATE_DOWN = 1
KEY_STATE_UP = 0
VALID_KEY_HASH = {
    "KEY_0": 0,
    "KEY_1": 1,
    "KEY_2": 2,
    "KEY_3": 3,
    "KEY_4": 4,
    "KEY_5": 5,
    "KEY_6": 6,
    "KEY_7": 7,
    "KEY_8": 8,
    "KEY_9": 9
}

#################################################################################
# Main logic
#################################################################################
# scan for devices
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
# find card reader device
if (len(devices) > 0):
    print("Input event devices available ("
            + str(len(devices)) + "). Devices are: ")
    # init card reader discovery bool
    discovered_card_reader = False
    # display input devices
    for i, device in enumerate(devices):
        print("    " + str(i) + ") (" + device.fn + ", "
                + device.name + ", " + device.phys + ")")
        # search for card reader by its name, "HID c216:0180"
        if str(device.name) == "HID c216:0180":
            print("Discovered card reader..listening for events \
                    until test harness is closed.")
            # rename device for readability
            card_reader = device
            # indefinitely listen for events
            byte_count = 0
            for event in card_reader.read_loop():
                if event.type == evdev.ecodes.EV_KEY:
                    event_key_state = evdev.util.categorize(event).keystate
                    keycode_str = evdev.util.categorize(event).keycode
                    if byte_count < 7:
                        if event_key_state == KEY_STATE_DOWN and keycode_str in VALID_KEY_HASH:
                            keycode_int = VALID_KEY_HASH[keycode_str]
                            if byte_count == 0:
                                print "ID: ",
                            print str(keycode_int),
                            byte_count += 1
                            # add newline
                            if byte_count == 7:
                                print("")
                    if event_key_state == KEY_STATE_UP and keycode_str == "KEY_ENTER":
                        # last byte in card, so reset byte count
                        byte_count = 0

    # error out if unable to find card reader
    if not discovered_card_reader:
        print("ERROR: Unable to find the card reader")
else:
    print("ERROR: No input event devices available")

#################################################################################
# House keeping..close interfaces and processes
#################################################################################
