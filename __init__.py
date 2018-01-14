#!/usr/bin/env python
# coding=utf-8
from adapt.intent import IntentBuilder
from os import path
import time
import timeit
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger

import pprint

from pifx import PIFX

LOGGER = getLogger(__name__)

class LifxSkill(MycroftSkill):
    def __init__(self):
        super(LifxSkill, self).__init__(name="LifxSkill")
        # @TODO Get the key from the the settingsmeta.json instead
        self.lifx = PIFX(self._get_key())

        # These will be set by _collect_selectors
        self.labels = {}
        self.groups = {}

    def initialize(self):
        self._collect_selectors()

    def _get_key(self):
        key_file = open(path.join(path.abspath(path.dirname(__file__)), 'api_key'), 'r')
        key = key_file.read()
        key_file.close()

        return key

    def _collect_selectors(self):
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

    def _normalize_selector(self, selector):
        return selector.lower().replace("'", "")

    def _choose_selector(self, message):
        selector = "all"
        if "Group" in message.data:
            selector = "group:" + self.groups.get(message.data["Group"].lower())
        elif "Label" in message.data:
            selector = "label:" + self.labels.get(message.data["Label"].lower())

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

def create_skill():
    return LifxSkill()
