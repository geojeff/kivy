#!/usr/bin/env python
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.statechart.system.state import State

import os

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SHOWING_SAVE_DIALOG_State(State):
    def __init__(self):
        super(SHOWING_SAVE_DIALOG_State, self).__init__()

    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def enterState(self):
        print 'SHOWING_SAVE_DIALOG/enterState'
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="save file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def exitState(self):
        print 'SHOWING_SAVE_DIALOG/exitState'
        self._popup.dismiss()
         
    def save(self):
        path = filechooser.path
        filename = text_input.text
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_input.text)
        self.gotoState('SHOWING_APP')

    def cancel(self):
        self.gotoState('SHOWING_APP')

Factory.register('SaveDialog', cls=SaveDialog)
