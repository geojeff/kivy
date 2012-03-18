#!/usr/bin/env python
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.statechart.system.state import State

import os

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SHOWING_LOAD_DIALOG_State(State):
    def __init__(self, **kwargs):
        kwargs['name'] = 'SHOWING_LOAD_DIALOG'
        super(SHOWING_LOAD_DIALOG_State, self).__init__(**kwargs)

    loadfile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def enterState(self):
        print 'SHOWING_LOAD_DIALOG/enterState'
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
        
    def exitState(self):
        print 'SHOWING_LOAD_DIALOG/exitState'
        self._popup.dismiss()
         
    def load(self):
        path = filechooser.path
        filename = filechooser.selection
        with open(os.path.join(path, filename[0])) as stream:
            self.text_input.text = stream.read()
        self.gotoState('SHOWING_APP')

    def cancel(self):
        self.gotoState('SHOWING_APP')

Factory.register('LoadDialog', cls=LoadDialog)
