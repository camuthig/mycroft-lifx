#!/usr/bin/env python
# coding=utf-8
from os import path
import time
import timeit
from collections import defaultdict
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger

from pifx import PIFX

LOGGER = getLogger(__name__)

class LifxSkill(MycroftSkill):
    """
    A Mycroft skill for controlling Lifx devices via the HTTP API.
    """

    def __init__(self):
        super(LifxSkill, self).__init__(name="LifxSkill")
        # TODO Get the key from the the settingsmeta.json instead
        self.lifx = PIFX(self._get_key())

        # These will be set by _collect_selectors
        self.labels = {}
        self.groups = {}
        self.room_lights = {}

    def initialize(self):
        self._collect_selectors()

    def stop(self):
        pass

    def _get_key(self):
        key_file = open(path.join(path.abspath(path.dirname(__file__)), 'api_key'), 'r')
        key = key_file.read()
        key_file.close()

        return key

    def _collect_selectors(self):
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
                self.room_lights[normalized].append(label)

    def _normalize_selector(self, selector):
        return selector.lower().replace("'", "")

    def _choose_selector(self, message):
        selector = "all"
        if "Group" in message.data:
            selector = "group:" + self.groups.get(self._normalize_selector(message.data["Group"]))
        elif "Label" in message.data:
            selector = "label:" + self.labels.get(self._normalize_selector(message.data["Label"]))

        return selector

    @intent_handler(IntentBuilder("ConnectToLifxIntent")
        .require("LifxKeyword")
        .require("ConnectKeyword"))
    def handle_connect_to_lifx_intent(self, message):
        self._collect_selectors()
        self.speak_dialog("done")

    @intent_handler(IntentBuilder("TurnOnIntent")
        .require("OnKeyword")
        .one_of("Label", "Group", "LightsKeyword"))
    def handle_turn_on_intent(self, message):
        self.lifx.set_state(self._choose_selector(message), "on")
        self.speak_dialog("turn.on")

    @intent_handler(IntentBuilder("TurnOffIntent")
        .require("OffKeyword")
        .one_of("Label", "Group", "LightsKeyword"))
    def handle_turn_off_intent(self, message):
        self.lifx.set_state(self._choose_selector(message), "off")
        self.speak_dialog("turn.off")

    @intent_handler(IntentBuilder("ListLightsIntent")
        .require("LightsKeyword")
        .require("InKeyword")
        .one_of("Group", "RoomKeyword"))
    def handle_list_lights_intent(self, message):
        room = "here"
        # TODO use settings to configure the default room for the device
        lights = self.labels

        if "Group" in message.data:
            room = self.groups.get(message.data["Group"])
            lights = self.room_lights.get(message.data["Group"])

        self.speak("The lights in {} are".format(room))

        for light in lights:
            self.lifx.pulse_lights("white", selector="label:" + light, cycles=1.0)
            self.speak(light)

    @intent_handler(IntentBuilder("ChangeBrightnessIntent")
        .one_of("BrightenKeyword", "DimKeyword")
        .one_of("Label", "Group", "RoomKeyword"))
    def handle_change_brightness_intent(self, message):
        if "BrightenKeyword" in message.data:
            brightness = .1
        else:
            brightness = -.1

        selector = self._choose_selector(message)

        # TODO Get the library updated to include this feature
        #self.lifx.set_delta(selector=selector, brightness=brightness)

        self.speak_dialog("done")

def create_skill():
    """
    Initialize the skill
    """
    return LifxSkill()
