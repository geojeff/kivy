'''
Object View
===========

.. versionadded:: 1.8

.. warning::

    This code is still experimental, and its API is subject to change in a
    future version.

The :class:`~kivy.uix.listview.ObjectView` widget provides a
scrollable/pannable viewport that is clipped at the scrollview's bounding box,
which contains a single item view instance.

:class:`~kivy.uix.listview.ObjectView` implements :class:`AbstractView` as a
vertical scrollable list. :class:`AbstractView` has one property, adapter.
:class:`~kivy.uix.listview.ObjectView` sets adapter to
:class:`~kivy.adapters.objectadapter.ObjectAdapter`, or a subclass.

'''

__all__ = ('ObjectView', )

from kivy.adapter import Adapter
from kivy.binding import DataBinding
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.lang import Builder

from kivy.properties import ObjectProperty

from kivy.uix.abstractview import AbstractView


Builder.load_string('''
<ObjectView>:
    container: container
    scrollview: scrollview
    ScrollView:
        id: scrollview
        pos: root.pos
        GridLayout:
            id: container
            cols: 1
            size_hint_y: None
''')


class ObjectView(Adapter, AbstractView, EventDispatcher):
    ''':class:`~kivy.uix.listview.ObjectView` is a primary high-level widget,
    handling the common task of presenting a view associated with an object.
    The view is held in a scroll view.

    The adapter property comes via the mixed in
    :class:`~kivy.uix.abstractview.AbstractView` class.

    .. versionadded:: 1.8

    '''

    container = ObjectProperty(None)
    '''The container is a :class:`~kivy.uix.gridlayout.GridLayout` widget held
    within a :class:`~kivy.uix.scrollview.ScrollView` widget.  (See the
    associated kv block in the Builder.load_string() setup). The object view
    instance is managed and provided by the adapter.  The container is cleared
    with a call to clear_widgets() when the data view is rebuilt by the
    populate() method.

    :data:`container` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    data_binding = ObjectProperty(None, allownone=True)
    '''Just as ListView needs a ListController or ListProperty bound to it for
    its data source, ObjectView needs an ObjectController or ObjectProperty for
    its data object source.

    In kv put the DataBinding at the end of arguments, indented like this::

        ObjectView:
            other properties: ...
            DataBinding:
                source: app.my_object_controller
                prop: 'data' <-- you don't have to provide this for controllers

    or, in python, the equivalent would be::

        app = App.app()
        my_object_view = ObjectView(other=something,
                                    data_binding=DataBinding(
                                        source=app.my_object_controller,
                                        prop='data'))

    :data:`data_binding` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    object_class = ObjectProperty(None, allownone=True)
    '''The object_class property, holding the view class to be constructed for
    the basis object, is the equivalent of the list_item_class in ListView,
    except that here we only have one data object for which a view is to
    be built. Still it can be useful to have the view class as a configurable
    property.

    :data:`object` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    def __init__(self, **kwargs):

        if 'data_binding' not in kwargs:
            kwargs['data_binding'] = DataBinding()

        # TODO: Make the name of the class in Adapter more generic so it will
        #       also work with ObjectView. For now, this hack:
        if 'object_class' in kwargs:
            kwargs['list_item_class'] = kwargs['object_class']

        super(ObjectView, self).__init__(**kwargs)

        self._trigger_populate = Clock.create_trigger(self._spopulate, -1)
        self._trigger_reset_spopulate = \
            Clock.create_trigger(self._reset_spopulate, -1)

        if self.data_binding.source and self.data_binding.source != self:
            self.data_binding.source.bind(
                **{self.data_binding.prop: self.data_binding.setter('value')})
            self.data_binding.bind_callback(self.update_ui_for_data_change)
            #self.data_binding.source.bind(
                    #on_data_change=self.update_ui_for_data_change)
            self.data = getattr(
                    self.data_binding.source, self.data_binding.prop)
#            if self.data_binding.prop == 'data':
#                self.data_binding.source.bind(
#                        on_data_change=self.update_ui_for_data_change)
#            if self.data_binding.prop == 'selection':
#                self.data_binding.source.bind(
#                    on_selection_change=self.update_ui_for_selection_change)

        if self.container:
            self.container.bind(minimum_height=self.container.setter('height'))

        self.bind(size=self._trigger_populate,
                  pos=self._trigger_populate)

    def init_kv_bindings(self, bindings):

        self.data_binding = db = bindings[0]
        db.source.bind(**{db.prop: db.setter('value')})
        db.bind_callback(self.update_ui_for_data_change)

    def _spopulate(self, *args):
        self.populate()

    def _reset_spopulate(self, *args):
        self.populate()

    def get_data_item(self, index):
        return self.data_binding._value

    def populate(self):

        container = self.container

        # Clear the view.
        container.clear_widgets()

        item_view = self.create_view(0)
        if item_view:
            container.add_widget(item_view)

    def update_ui_for_data_change(self, *args):
        # TODO: brute force here.
        self.populate()

    def update_ui_for_selection_change(self, *args):
        # TODO: brute force here.
        self.populate()

    def get_selection(self):
        '''A convenience method to call to the adapter for the all of the
        selected items.

        .. versionadded:: 1.8

        '''
        return self.get_selection() if self else None

    def get_first_selected(self):
        '''A convenience method to call to the adapter for the first selected
        item.

        .. versionadded:: 1.8

        '''
        return self.get_first_selected() if self else None

    def get_last_selected(self):
        '''A convenience method to call to the adapter for the last selected
        item.

        .. versionadded:: 1.8

        '''
        return self.get_last_selected() if self else None
