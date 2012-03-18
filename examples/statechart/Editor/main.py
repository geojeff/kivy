#!/usr/bin/env python
from kivy.app import App
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.statechart.system.state import State
from kivy.statechart.system.statechart import Statechart

import os, inspect

from showing_app import SHOWING_APP_State
from showing_load_dialog import SHOWING_LOAD_DIALOG_State
from showing_save_dialog import SHOWING_SAVE_DIALOG_State

class Root(FloatLayout):
    pass

class AppStatechart(Statechart):
    rootState = ObjectProperty(None)

    def __init__(self, app):
        self.app = app
        self.rootState = self._rootState()
        print inspect.isclass(self.rootState), 'isclass'
        super(Statechart, self).__init__()

    def _rootState(self):
        class RootState(State):
            def __init__(self):
                super(RootState, self).__init__()
    
            initialSubstate = 'SHOWING_APP'
    
            SHOWING_APP = SHOWING_APP_State()
            SHOWING_LOAD_DIALOG  = SHOWING_LOAD_DIALOG_State()
            SHOWING_SAVE_DIALOG  = SHOWING_SAVE_DIALOG_State()

        return RootState

class Editor(App):
    def __init__(self):
        pass

Factory.register('Root', cls=Root)

if __name__ == '__main__':
    app = Editor()
    statechart = AppStatechart(app)
    app.statechart = statechart
    app.statechart.initStatechart()
    app.run()

