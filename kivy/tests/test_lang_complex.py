import unittest

rules = '''
<Label>:
    title: 'invalid'
<TestWidget>:
    source: 'invalid.png'

<TestWidget2>:
    source: 'invalid.png'
    source3: 'valid.png'

[Item@TestWidget2]:
    source: ctx.get('anotherctxvalue')

<MainWidget>:
    refwid: myref
    refwid2: myref2
    Item:
        id: myref2
        anotherctxvalue: 'valid.png'
    TestWidget:
        canvas:
            Color:
                rgba: 1, 1, 1, 1
        id: myref
        source: 'valid.png'
        source2: 'valid.png'
        source3: self.source + 'from source3' if self.can_edit else 'valid.png'
        on_release: root.edit()
        Label:
            title: 'valid'
'''


class LangComplexTestCase(unittest.TestCase):

    def test_complex_rewrite(self):
        # this test cover a large part of the lang
        # and was used for testing the validity of the new rewrite lang
        # however, it's not self explained enough :/

        from kivy.lang import Builder
        from kivy.uix.widget import Widget
        from kivy.uix.popup import Popup
        from kivy.factory import Factory
        from kivy.properties import StringProperty, ObjectProperty, \
            BooleanProperty

        Builder.load_string(rules)

        class TestWidget(Widget):
            source = StringProperty('')
            source2 = StringProperty('')
            source3 = StringProperty('')
            can_edit = BooleanProperty(False)

            def __init__(self, **kwargs):
                self.register_event_type('on_release')
                super(TestWidget, self).__init__(**kwargs)

            def on_release(self):
                pass

        class MainWidget(Widget):
            refwid = ObjectProperty(None)
            refwid2 = ObjectProperty(None)

        class TestWidget2(Widget):
            pass

        Factory.register('TestWidget', cls=TestWidget)
        Factory.register('TestWidget2', cls=TestWidget2)

        a = MainWidget()
        self.assertTrue(isinstance(a.refwid, TestWidget))
        self.assertEquals(a.refwid.source, 'valid.png')
        self.assertEquals(a.refwid.source2, 'valid.png')
        self.assertEquals(a.refwid.source3, 'valid.png')
        self.assertTrue(len(a.refwid.children) == 1)
        self.assertEquals(a.refwid.children[0].title, 'valid')
        self.assertTrue(isinstance(a.refwid2, TestWidget2))
        self.assertEquals(a.refwid2.source, 'valid.png')


rules_popup = """
<MainWidget>:
    refwid: myref
    refwid2: myref2
    Item:
        id: myref2

    QuestionPopup:
        size_hint: .5, .5
        pos_hint: {'center_x': .5, 'center_y': .5}

        content:
            orientation: 'vertical'
            padding: 1
            spacing: 1

            Label:
                text: root.question
                height: 30

            TextInput:
                text: root.answer
                size_hint_y: None
                height: 50

            BoxLayout:
                size_hint_y: None
                height: 30
                Button:
                    text: "cancel"

                Button:
                    text: "ok"
"""


class LangComplexPopupTestCase(unittest.TestCase):

    def test_complex_popup_rewrite(self):
        # This test was added when an indentation error, for two many
        # indent levels, showed up in an app for the line that has
        # text: root.node.question
        #
        # In addition to checking for indentation, it uses Popup,
        # instead of Widget as the class.

        from kivy.lang import Builder
        from kivy.uix.widget import Widget
        from kivy.factory import Factory
        from kivy.properties import StringProperty, ObjectProperty, \
            BooleanProperty

        Builder.load_string(rules_popup)

        class MainWidget(Widget):
            refwid = ObjectProperty(None)
            refwid2 = ObjectProperty(None)

        class QuestionPopup(Popup):
            question = StringProperty('')
            answer = StringProperty('')

            def __init__(self, **kwargs):
                super(QuestionPopup, self).__init__(**kwargs)

            def on_release(self):
                pass

        class MainWidget(Widget):
            refwid = ObjectProperty(None)
            refwid2 = ObjectProperty(None)

        Factory.register('QuestionPopup', cls=QuestionPopup)

        a = MainWidget()
        self.assertTrue(isinstance(a.refwid, QuestionPopup))
        self.assertEquals(a.refwid.question, 'What is 2 + 2?')
        self.assertEquals(a.refwid.answer, '4')
        #self.assertTrue(len(a.refwid.children) == 1)
        #self.assertEquals(a.refwid.children[0].title, 'valid')

