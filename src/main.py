import gc
import machine
import network
import sys
import time

from rotary_irq_esp import RotaryIRQ

import sonos_remote_config as config

builtin_led = machine.Pin(2, machine.Pin.OUT)

sta_if = network.WLAN(network.STA_IF)

def wait_for_wifi(timeout):
    for _ in range(timeout):
        if sta_if.isconnected():
            break
        time.sleep(1)

wait_for_wifi(10)

if not sta_if.isconnected():
    sta_if.active(True)
    sta_if.connect(config.wifi_ssid, config.wifi_pass)
    
    wait_for_wifi(10)
    if not sta_if.isconnected():
        print("Error: could not connect to wifi network")
        sys.exit(-1)

try:
    import urequests
except ImportError:
    # try to install it
    print("urequests seems to be missing, trying to install it via upip")
    import upip
    upip.install("micropython-urequests")
    import urequests

try:
    import uasyncio as asyncio
except ImportError:
    # try to install it
    print("uasyncio seems to be missing, trying to install it via upip")
    import upip
    upip.install("uasyncio")
    import uasyncio as asyncio

builtin_led(1)
print("Connected and ready to control Sonos in room {}".format(config.sonos_room))

knob = RotaryIRQ(config.pin_rotary_clk, config.pin_rotary_dt)

def call_url(url):
    gc.collect()
    resp = None
    try:
        resp = urequests.get(url, stream=True)
    except Exception as e:
        if isinstance(e, OSError) and resp is not None:
            resp.close()
        raise
    gc.collect()
    return resp

async def evaluate_volume():
    old_knob = 0

    while True:
        new_knob = knob.value()
        print("Value = {}".format(new_knob))

        difference = abs(new_knob - old_knob)
        print("\t## Steps: {}".format(difference))

        #total_volume_step = config.sonos_volume_step
        total_volume_step = difference

        try:
            if new_knob > old_knob:
                # volume down
                url = "{}/{}/volume/-{}".format(config.sonos_base, config.sonos_room, total_volume_step)
                print("\t## Volume down by {}: {}".format(total_volume_step, url))
                call_url(url)
            elif new_knob < old_knob:
                # volume up
                url = "{}/{}/volume/+{}".format(config.sonos_base, config.sonos_room, total_volume_step)
                print("\t## Volume up by {}: {}".format(total_volume_step, url))
                call_url(url)
        except Exception as e:
            print("Something went wrong while trying to adjust the volume: {}".format(e))
        
        old_knob = new_knob

        await asyncio.sleep_ms(100)

loop = asyncio.get_event_loop()
loop.create_task(evaluate_volume())

try:
    loop.run_forever()
except KeyboardInterrupt:
    print("Interrupted")