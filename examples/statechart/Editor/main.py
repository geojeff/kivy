#!/usr/bin/env python
from kivy.app import App
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.statechart.system.state import State
from kivy.statechart.system.statechart import Statechart

import os, inspect

#from showing_app import SHOWING_APP
from showing_load_dialog import SHOWING_LOAD_DIALOG
from showing_save_dialog import SHOWING_SAVE_DIALOG

class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

class SHOWING_APP(State):
    def __init__(self, **kwargs):
        kwargs['name'] = 'SHOWING_APP'
        super(SHOWING_APP, self).__init__(**kwargs)

    def enterState(self, context=None):
        print 'SHOWING_APP/enterState'
        self.statechart.app.load_config()
        self.statechart.app.load_kv()
        #self.statechart.app.root = Root()
        setattr(self.statechart.app.root, 'statechart', self.statechart)
        self.statechart.app.built = True
        self.statechart.app.run()
                
    def exitState(self, context=None):
        print 'SHOWING_APP/exitState'

    def show_load(self):
        self.gotoState('SHOWING_LOAD_DIALOG')

    def show_save(self):
        self.gotoState('SHOWING_SAVE_DIALOG')

class AppStatechart(Statechart):
    rootState = ObjectProperty(None)

    def __init__(self, app, **kw):
        self.app = app
        self.rootState = self._rootState()
        super(AppStatechart, self).__init__(**kw)

    def _rootState(self):
        class RootState(State):
            def __init__(self, **kwargs):
                super(RootState, self).__init__(**kwargs)
    
            initialSubstate = 'SHOWING_APP'
    
            SHOWING_APP = SHOWING_APP

            SHOWING_LOAD_DIALOG  = SHOWING_LOAD_DIALOG
            SHOWING_SAVE_DIALOG  = SHOWING_SAVE_DIALOG

            @State.eventHandler(['print initial substate', 'print states'])
            def printInfo(self, infoType):
                if infoType is 'print initial substate':
                    print 'INFO:', self.initialSubstate
                elif infoType is 'print states':
                    print 'INFO:', (self[key].name for key in dir(self) if issubclass(self[key], State))

        return RootState

class Editor(App):
    pass

Factory.register('Root', cls=Root)

if __name__ == '__main__':
    app = Editor()
    statechart = AppStatechart(app, allowStatechartTracing=True)
    app.statechart = statechart
    app.statechart.initStatechart()
    app.statechart.rootState.printInfo('print states')

