# mycroft-lifx

A Mycroft skill for controlling Lifx bulbs.

## Features

[ ] Set API key using Mycroft settings
[ ] Set the devices room using Mycroft settings
[ ] Use regex for better matching
[x] Connect to Lifx
[x] Turn lights on/off
[ ] Dim/bright lights **(in progress)**
[ ] Set the color of lights (color)
[ ] Change the warmth of the lights (white)
[x] List lights

## Commands

### Connecting to Lifx

When first loaded, this skill will connect to Lifx to determine the names of
all rooms and lights in your account. This is important so that it can listen
for these names in your commands. If you ever decide to change the names of the
lights or rooms, you should issue a command for the skill to refresh it's list

`Reconnect to Lifx`

### Turning lights on/off

To turn on the lights, you can use a simple command like:

`Turn on the lights`

Or to turn them off,

`Turn off the lights`

This will turn on _all_ of the lights though, which isn't always helpful.
Another option is to access devices by their name (label) or room (group). For
example, if you have a group in your Lifx settings called "Livingroom", you
could just say something like

`Turn on the livingroom lights`

to turn on only the lights in the livingroom. The skill supports both
individual light names and group names.

### Changing the brightness

To Be Implemented

Lights can be dimmed individually, by name, or as a group. To do so, just issue
a command like

`Dim the lights in the livingroom`

This will dim the lights by 10% for each time the command is executed.

### Listing lights

So maybe you don't know the names of all the lights in the current room. Don't
worry, this skill can help. By issuing a command like

`What are the names of the lights in here?`

or

`What are the names of the lights in the livingroom?`

you can figure it out. This command will have mycroft list each of the lights
in the room, while pulsing the light, so you know which one it is.