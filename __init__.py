#!/usr/bin/env python
# coding=utf-8
import time
import timeit
from mycroft.skills.core import MycroftSkill

from pifx import PIFX

class LifxSkill(MycroftSkill):
    def __init__(self):
        super(LifxSkill, self).__init__(name="LifxSkill")
        # @TODO Get the key from the the settingsmeta.json instead
        self.lifx = PIFX(self._get_key())

    def _get_key(self):
        file = open('api_key', 'r')
        key = file.read()
        file.close()

        return key

    @intent_handler(IntentBuilder("TurnOnIntent").require("OnKeyword"))
    def handle_turn_on_intent(self, message):
        self.lifx.set_state("label:Chris's Lamp", "on")
        self.speak_dialog("turn.on")

    @intent_handler(IntentBuilder("TurnOffIntent").require("OffKeyword"))
    def handle_turn_off_intent(self, message):
        self.lifx.set_state("label:Chris's Lamp", "off")
        self.speak_dialog("turn.off")

def create_skill():
    return LifxSkill()