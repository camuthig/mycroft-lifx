#!/usr/bin/env python
# coding=utf-8
from os import path
import time
import timeit
from collections import defaultdict
from fuzzywuzzy import fuzz
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger

from pifx import PIFX

LOGGER = getLogger(__name__)

COLORS = {
    "blue": "#0000ff",
    "crimson": "#dc143c",
    "cyan": "#00ffff",
    "fuchsia": "#ff00ff",
    "gold": "#ffd700",
    "green": "#008000",
    "lavender": "#e6e6fa",
    "lime": "#00ff00",
    "magenta": "#ff00ff",
    "orange": "#ffa500",
    "pink": "#ffc0cb",
    "purple": "#800080",
    "red": "#ff0000",
    "salmon": "#fa8072",
    "sky blue": "#87ceeb",
    "teal": "#008080",
    "turquoise": "#40e0d0",
    "violet": "#ee82ee",
    "yellow": "#ffff00"
}

class LifxSkill(MycroftSkill):
    """
    A Mycroft skill for controlling Lifx devices via the HTTP API.
    """

    def __init__(self):
        super(LifxSkill, self).__init__(name="LifxSkill")
        # TODO Get the key from the the settingsmeta.json instead
        self.lifx = PIFX(self._get_key())

        # These will be set by _collect_devices
        self.labels = {}
        self.groups = {}
        self.room_lights = {}

    def initialize(self):
        self._collect_devices()

    def stop(self):
        pass

    @intent_handler(IntentBuilder("ConnectToLifxIntent")
        .require("LifxKeyword")
        .require("ConnectKeyword"))
    def handle_connect_to_lifx_intent(self, message):
        """
        Connect to Lifx, syncing up device data
        """
        self._collect_devices()
        self.speak_dialog("done")

    @intent_handler(IntentBuilder("ListLightsIntent")
        .require("ListRoom"))
    def handle_list_lights_intent(self, message):
        """
        List all of the lights in the default room or the named room
        """
        if message.data["ListRoom"] is "room" or message.data["ListRoom"] is "here":
            # TODO use settings to configure the default room for the device
            room = next(iter(self.room_lights))
        else:
            room = self._match_entity_to_group(message.data["ListRoom"])

        if room is None:
            self.speak("I am not sure what room {} is".format(message.data["ListRoom"]))
        else:
            self.speak("The lights in {} are".format(room))

            lights = self.room_lights[room]

            for light in lights:
                self.lifx.pulse_lights("white", selector="label:" + light, cycles=1.0)
                self.speak(light)


    @intent_handler(IntentBuilder("SetPowerIntent")
        .require("LightAction")
        .require("Entity"))
    def handle_set_power_intent(self, message):
        """
        Turn lights on/off by name or room
        """
        entity = message.data["Entity"]
        state = message.data["LightAction"]

        if "LightsStatement" in message.data:
            entity = "the {} lights".format(entity)

        selector = self._match_entity_to_selector(entity)

        self.lifx.set_state(selector=selector, power=state)

        self.speak("Turned {} {}".format(entity, state))

    @intent_handler(IntentBuilder("SetStateValueIntent")
        .require("SetKeyword")
        .one_of("WarmthKeyword", "BrightnessKeyword", "ColorKeyword")
        .require("Entity")
        .require("StateValue") )
    def handle_set_state_intent(self, message):
        """
        A single intent to handle setting the brightness, color and temperature
        """
        entity = message.data["Entity"]
        state_value = message.data["StateValue"]

        self.speak(entity)
        self.speak(state_value)

        if "BrightnessKeyword" in message.data:
            self._handle_set_brightness_intent(entity, state_value)
        elif "WarmthKeyword" in message.data:
            self._handle_set_temperature_intent(entity, state_value)
        elif "ColorKeyword" in message.data:
            self._handle_set_color_intent(entity, state_value)
        else:
            self.speak_dialog("whoops")

    def _handle_set_brightness_intent(self, entity, value):
        """
        Set the brightess of lights by name or room. The room should be a percentage of brightness
        """

        self.lifx.set_state(
            selector=self._match_entity_to_selector(entity),
            brightness=(float(value) / 100)
        )

        self.speak("Set {} to {} percent".format(entity, value))

    def _handle_set_temperature_intent(self, entity, value):
        """
        Set the temperature of lights by name or room.
        """
        selector = self._match_entity_to_selector(entity)

        if selector is None:
            self.speak("Unable to find the light or room {}".format(entity))
        else:
            self.lifx.set_state(
                selector=selector,
                color="kelvin:{}".format(value)
            )

            self.speak_dialog("done")

    def _handle_set_color_intent(self, entity, value):
        color_code = self._match_color(value)
        selector = self._match_entity_to_selector(entity)

        if color_code is None:
            self.speak("Cannot set the color {}".format(value))
        elif selector is None:
            self.speak("Could not find the light or room {}".format(entity))
        else:
            self.lifx.set_state(selector=selector, color=color_code)

            self.speak_dialog("done")

    def _match_entity_to_selector(self, entity):
        """
        Find the closest matching selector to the entity
        """
        for _, name in self.groups.iteritems():
            if fuzz.ratio(name, entity) > 70:
                return "group:" + name
        
        for _, name in self.labels.iteritems():
            if fuzz.ratio(name, entity) > 70:
                return "label:" + name

        # TODO Return configured room instead
        return "all"

    def _match_entity_to_group(self, entity):
        """
        Find the closest matching group to the entity
        """
        for _, name in self.groups.iteritems():
            if fuzz.ratio(name, entity) > 70:
                return name
        
        return None

    def _match_color(self, color):
        """
        Find the best match for the color requested
        """
        for name, code in COLORS.iteritems():
            if fuzz.ratio(name, color) > 70:
                return code

        return None

    def _get_key(self):
        key_file = open(path.join(path.abspath(path.dirname(__file__)), 'api_key'), 'r')
        key = key_file.read()
        key_file.close()

        return key

    def _collect_devices(self):
        self.room_lights = defaultdict(list)
        lights = self.lifx.list_lights()
        for light in lights:
            label = light.get("label")
            normalized = self._normalize_selector(label)
            self.register_vocabulary(normalized, "Label")

            self.labels[normalized] = label

            if light.get("group").get("name"):
                group = light.get("group").get("name")
                normalized = self._normalize_selector(group)
                self.register_vocabulary(normalized, "Group")

                self.groups[normalized] = group
                self.room_lights[group].append(label)

    def _normalize_selector(self, selector):
        return selector.lower().replace("'", "")

    def _choose_selector(self, message):
        selector = "all"
        if "Group" in message.data:
            selector = "group:" + self.groups.get(self._normalize_selector(message.data["Group"]))
        elif "Label" in message.data:
            selector = "label:" + self.labels.get(self._normalize_selector(message.data["Label"]))

        return selector


def create_skill():
    """
    Initialize the skill
    """
    return LifxSkill()
