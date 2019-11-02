# SonosRemote

Sonos remote control based on an ESP8266, a rotary encoder, MicroPython and [Sonos HTTP API](https://jishi.github.io/node-sonos-http-api/).

## Features

  * Control playback and volume with one knob
    * Volume up/down on cw/ccw rotation of encoder
    * Toggle play/pause on single press
    * Next track on double press
    * Previous track on long press
  * Activity LED on sent commands
  * Configurable via provisioning file
  * Implemented based on asyncio

## BOM/Prerequisits

  * Wemos D1 Mini
  * KY-040 rotary encoder breakout
  * Existing and configured install of [Sonos HTTP API](https://jishi.github.io/node-sonos-http-api/) (e.g. in a Docker container).
