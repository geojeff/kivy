'''
Statechart tests, init with assigned root state
===========
'''

import unittest

counter = 0

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.statechart.system.state import State
from kivy.statechart.system.statechart import StatechartManager

import os, inspect

owner = ObjectProperty(None)

class A(State):
    def __init__(self, **kwargs):
        kwargs['name'] = 'A'
        super(A, self).__init__(**kwargs)

    def foo(self, *l):
        print 'foo called, trying to goto B'
        self.statechart.gotoState('B') # [PORT] self.gotoState should work...

class B(State):
    def __init__(self, **kwargs):
        kwargs['name'] = 'B'
        super(B, self).__init__(**kwargs)

    def bar(self, *l):
        print 'bar called, trying to goto A'
        self.statechart.gotoState('A')

class Statechart1(StatechartManager):
    def __init__(self, **kw):
        super(Statechart1, self).__init__(**kw)

    initialState = 'A'

    A = A
    B = B

#Statechart1 = StatechartManager(**{
#    'initialState': 'A',
#    'A': State(**{ 'foo': lambda self,*l: self.gotoState('B')}),
#    'B': State(**{ 'bar': lambda self,*l: self.gotoState('A')})
#    })

class TestApp(App):
    pass

class StatechartTestCase(unittest.TestCase):
    def setUp(self):
        global app
        global s1
        s1 = Statechart1()

    def test_init_with_unassigned_root_state(self):
        self.assertTrue(s1.isStatechart)
        self.assertTrue(s1.statechartIsInitialized)
