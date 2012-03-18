#!/usr/bin/env python
from kivy.factory import Factory
from kivy.statechart.system.state import State

class SHOWING_APP_State(State):
    def __init__(self):
        super(SHOWING_APP_State, self).__init__(name='SHOWING_APP')

    def enterState(self):
        print 'SHOWING_APP/enterState'
                
    def exitState(self):
        print 'SHOWING_APP/exitState'

    def show_load(self):
        self.gotoState('SHOWING_LOAD_DIALOG')

    def show_save(self):
        self.gotoState('SHOWING_SAVE_DIALOG')
