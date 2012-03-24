#!/usr/bin/env python
from kivy.app import App
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.statechart.system.state import State
from kivy.statechart.system.statechart import Statechart
from kivy.statechart.system.statechart import StatechartManager

import os, inspect

from showing_load_dialog import SHOWING_LOAD_DIALOG
from showing_save_dialog import SHOWING_SAVE_DIALOG

class MainView(FloatLayout):
    app = ObjectProperty(None)
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

class SHOWING_MAIN(State):
    def __init__(self, **kwargs):
        kwargs['name'] = 'SHOWING_MAIN'
        super(SHOWING_MAIN, self).__init__(**kwargs)

    def enterState(self, context=None):
        print 'SHOWING_MAIN/enterState'
        setattr(self.statechart.app, 'statechart', self.statechart) # hacky?
                
    def exitState(self, context=None):
        print 'SHOWING_MAIN/exitState'

    def show_load(self, *l):
        self.statechart.gotoState('SHOWING_LOAD_DIALOG')

    def show_save(self, *l):
        self.statechart.gotoState('SHOWING_SAVE_DIALOG')

class RootState(State):
    def __init__(self, **kwargs):
        super(RootState, self).__init__(**kwargs)
    
    initialSubstate = 'SHOWING_MAIN'
    
    SHOWING_MAIN = SHOWING_MAIN
    SHOWING_LOAD_DIALOG  = SHOWING_LOAD_DIALOG
    SHOWING_SAVE_DIALOG  = SHOWING_SAVE_DIALOG

    # Not used at the moment. An event handler can handle multiple events
    # for the state. Compare this to having discrete methods, e.g. show_load
    # in SHOWING_MAIN state.
    @State.eventHandler(['print initial substate', 'print states'])
    def printInfo(self, infoType):
        if infoType is 'print initial substate':
            print 'INFO:', self.initialSubstate
        elif infoType is 'print states':
            print 'INFO:', (self[key].name for key in dir(self) if issubclass(self[key], State))

class AppStatechart(StatechartManager):
    def __init__(self, app, **kw):
        self.app = app
        self.trace = True
        self.rootState = RootState
        super(AppStatechart, self).__init__(**kw)

class Editor(App):
    statechart = ObjectProperty(None)

    def build(self):
        return MainView(app=self)

if __name__ == '__main__':
    app = Editor()
    statechart = AppStatechart(app)
    app.run()

