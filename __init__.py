#!/usr/bin/env python
# coding=utf-8
from adapt.intent import IntentBuilder
from os import path
import time
import timeit
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger

from pifx import PIFX

LOGGER = getLogger(__name__)

class LifxSkill(MycroftSkill):
    def __init__(self):
        super(LifxSkill, self).__init__(name="LifxSkill")
        # @TODO Get the key from the the settingsmeta.json instead
        self.lifx = PIFX(self._get_key())

    def _get_key(self):
        key_file = open(path.join(path.abspath(path.dirname(__file__)), 'api_key'), 'r')
        key = key_file.read()
        key_file.close()

        return key

    @intent_handler(IntentBuilder("TurnOnIntent")
        .require("OnKeyword")
        .one_of("Group", "LightsKeyword"))
    def handle_turn_on_intent(self, message):
        LOGGER.debug("logging\n")
        LOGGER.debug(message.data)    
        LOGGER.debug("end\n")
        self.lifx.set_state("group:Bedroom", "on")
        self.speak_dialog("turn.on")

    @intent_handler(IntentBuilder("TurnOffIntent")
        .require("OffKeyword")
        .one_of("Group", "LightsKeyword"))
    def handle_turn_off_intent(self, message):
        self.lifx.set_state("group:Bedroom", "off")
        self.speak_dialog("turn.off")

def create_skill():
    return LifxSkill()
