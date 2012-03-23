'''
Statechart tests
===========
'''

import unittest

counter = 0

from kivy.app import App
from kivy.statechart.system.state import State
from kivy.statechart.system.statechart import Statechart

import os, inspect

class A(State):
    def __init__(self, **kwargs):
        kwargs['name'] = 'A'
        super(A, self).__init__(**kwargs)

    def foo(self):
        self.gotoState('B')

class B(State):
    def __init__(self, **kwargs):
        kwargs['name'] = 'B'
        super(B, self).__init__(**kwargs)

    def bar(self):
        self.gotoState('A')

class Statechart1(Statechart):
    def __init__(self, app, **kw):
        self.app = app
        self.rootState = self._rootState()
        super(Statechart1, self).__init__(**kw)

    def _rootState(self):
        class RootState(State):
            def __init__(self, **kwargs):
                super(RootState, self).__init__(**kwargs)
    
            initialSubstate = 'A'
    
            A = A
            B = B

        return RootState

class TestApp(App):
    pass

class StatechartTestCase(unittest.TestCase):

    def setUp(self):
        global app
        global s1
        app = TestApp()
        s1 = Statechart1(app)
        app.statechart = s1

    def test_initStatechart(self):
        app.statechart.initStatechart()
        self.assertTrue(app.statechart.isStatechart)
        self.assertTrue(app.statechart.statechartIsInitialized)
        self.assertEqual(app.statechart.rootState.name, '__ROOT_STATE__')
        self.assertEqual(app.statechart.initialState, None)
        self.assertTrue(app.statechart.getState('A').isCurrentState)
        self.assertFalse(app.statechart.getState('B').isCurrentState)

