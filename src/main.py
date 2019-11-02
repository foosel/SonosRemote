import gc
import machine
import network
import sys
import time

import urequests as requests
import uasyncio as asyncio

from aswitch import Pushbutton
from rotary_irq_esp import RotaryIRQ

import sonos_remote_config as config

ROOM_URL = "{base}/{room}"
VOLUP_URL = ROOM_URL + "/volume/+{step}"
VOLDN_URL = ROOM_URL + "/volume/-{step}"
PLAY_URL = ROOM_URL + "/playpause"
NEXT_URL = ROOM_URL + "/next"
PREV_URL = ROOM_URL + "/previous"

class RotaryEncoder(object):
    def __init__(self, pin_clk, pin_dt, delay=100, cw=None, ccw=None):
        self._rotary = RotaryIRQ(pin_clk, pin_dt)
        self._delay = delay

        self._cb_cw = cw
        self._cb_ccw = ccw

        loop = asyncio.get_event_loop()
        loop.create_task(self.check())
    
    async def check(self):
        old_value = 0

        while True:
            new_value = self._rotary.value()
            difference = abs(new_value - old_value)

            if new_value > old_value and callable(self._cb_ccw):
                self._cb_ccw(difference)
            elif old_value > new_value and callable(self._cb_cw):
                self._cb_cw(difference)
            
            old_value = new_value

            await asyncio.sleep_ms(self._delay)

def wait_for_wifi(wifi, timeout=10):
    for _ in range(timeout):
        if wifi.isconnected():
            break
        time.sleep(1)

def ensure_connection(ssid, key):
    sta_if = network.WLAN(network.STA_IF)
    wait_for_wifi(sta_if)

    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(ssid, key)
        
        wait_for_wifi(sta_if)
        if not sta_if.isconnected():
            print("Error: could not connect to wifi network")
            sys.exit(-1)

def call_url(url):
    gc.collect()
    resp = None
    try:
        resp = requests.get(url, stream=True)
    except Exception as e:
        if isinstance(e, OSError) and resp is not None:
            resp.close()
        raise
    gc.collect()
    return resp

def volume_up(steps):
    url = VOLUP_URL.format(base=config.sonos_base, room=config.sonos_room, step=steps * config.sonos_volume_step)
    print("## Volume up by {}: {}".format(steps, url))
    call_url(url)

def volume_down(steps):
    url = VOLDN_URL.format(base=config.sonos_base, room=config.sonos_room, step=steps * config.sonos_volume_step)
    print("## Volume down by {}: {}".format(steps, url))
    call_url(url)

def toggle_play():
    url = PLAY_URL.format(base=config.sonos_base, room=config.sonos_room)
    print("## Toggle play: {}".format(url))
    call_url(url)

def next_track():
    url = NEXT_URL.format(base=config.sonos_base, room=config.sonos_room)
    print("## Next track: {}".format(url))
    call_url(url)

def prev_track():
    url = PREV_URL.format(base=config.sonos_base, room=config.sonos_room)
    print("## Previous track: {}".format(url))
    call_url(url)

def main():
    builtin_led = machine.Pin(2, machine.Pin.OUT)
    play_button = machine.Pin(config.pin_rotary_sw, machine.Pin.IN)

    # connect wifi
    ensure_connection(config.wifi_ssid, config.wifi_pass)

    # success
    builtin_led(1)
    print("Connected and ready to control Sonos in room {}".format(config.sonos_room))

    # led light wrapper
    def with_led(wrapped):
        def f(*args, **kwargs):
            builtin_led(0) # light on
            try:
                return wrapped(*args, **kwargs)
            finally:
                builtin_led(1) # light off
        return f

    # initialize hardware
    volume_knob = RotaryEncoder(config.pin_rotary_clk, config.pin_rotary_dt, cw=with_led(volume_up), ccw=with_led(volume_down), delay=100)
    button = Pushbutton(play_button, suppress=True)
    button.release_func(with_led(toggle_play))
    button.double_func(with_led(next_track))
    button.long_func(with_led(prev_track))

    # ... and run
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Interrupted")

if __name__ == "__main__":
    main()