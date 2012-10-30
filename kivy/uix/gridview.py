'''
Grid View
===========

.. versionadded:: 1.5

.. warning::

    This widget is still experimental, and its API is subject to change in a
    future version.

The :class:`~kivy.uix.gridview.GridView` widget provides a scrollable/pannable
viewport that is clipped at the scrollview's bounding box, which contains a
list of list item view instances.

:class:`~kivy.uix.gridview.GridView` implements :class:`AbstractView` as a
vertical scrollable list. :class:`AbstractView` has one property, adapter.
:class:`~kivy.uix.gridview.GridView` sets adapter to be an instance of
:class:`~kivy.adapters.gridadapter.GridAdapter`.


    :Events:
        `on_scroll_complete`: (boolean, )
            Fired when scrolling completes.

'''

from kivy.event import EventDispatcher
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.listview import SelectableView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.abstractview import AbstractView
from kivy.adapters.gridadapter import GridAdapter
from kivy.properties import ObjectProperty, DictProperty, \
        NumericProperty, ListProperty, BooleanProperty, StringProperty
from kivy.lang import Builder
from math import ceil, floor

__all__ = ('GridCell', 'GridRow', 'GridView', )


class GridCell(SelectableView, Button):
    ''':class:`~kivy.uix.listview.GridCell` mixes
    :class:`~kivy.uix.listview.SelectableView` with
    :class:`~kivy.uix.button.Button` to produce a button suitable for use in
    :class:`~kivy.uix.listview.ListView`.
    '''

    selected_color = ListProperty([1., 0., 0., 1])
    '''
    :data:`selected_color` is a :class:`~kivy.properties.ListProperty`,
    default to [1., 0., 0., 1].
    '''

    deselected_color = ListProperty([0., 1., 0., 1])
    '''
    :data:`selected_color` is a :class:`~kivy.properties.ListProperty`,
    default to [0., 1., 0., 1].
    '''

    def __init__(self, **kwargs):
        super(GridCell, self).__init__(**kwargs)

        # Set deselected_color to be default Button bg color.
        self.deselected_color = self.background_color

        # Set default border to be 2 pixels all around.
        self.border = [2, 2, 2, 2]

    def select(self, *args):
        self.background_color = self.selected_color
        if type(self.parent) is GridRow:
            self.parent.select_from_child(self, *args)

    def deselect(self, *args):
        self.background_color = self.deselected_color
        if type(self.parent) is GridRow:
            self.parent.deselect_from_child(self, *args)

    def select_from_composite(self, *args):
        self.background_color = self.selected_color

    def deselect_from_composite(self, *args):
        self.background_color = self.deselected_color

    def __repr__(self):
        return self.text


class GridRow(SelectableView, BoxLayout):
    ''':class:`~kivy.uix.gridview.GridRow` mixes
    :class:`~kivy.uix.listview.SelectableView` with :class:`BoxLayout` for a
    generic container-style list item, to be used in
    :class:`~kivy.uix.gridview.GridView`.
    '''

    background_color = ListProperty([1, 1, 1, 1])
    '''ListItem sublasses Button, which has background_color, but
    for a composite list item, we must add this property.

    :data:`background_color` is a :class:`~kivy.properties.ListProperty`,
    default to [1, 1, 1, 1].
    '''

    selected_color = ListProperty([1., 0., 0., 1])
    '''
    :data:`selected_color` is a :class:`~kivy.properties.ListProperty`,
    default to [1., 0., 0., 1].
    '''

    deselected_color = ListProperty([.33, .33, .33, 1])
    '''
    :data:`deselected_color` is a :class:`~kivy.properties.ListProperty`,
    default to [.33, .33, .33, 1].
    '''

    representing_cell = ObjectProperty(None)
    '''Which component grid cell view class, if any, should represent for the
    grid row in __repr__()?

    :data:`representing_cell` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    adapter = ObjectProperty(None)
    '''A reference to the managing adapter for this view, which is needed for
    calling back during selection operations.
    '''

    def __init__(self, **kwargs):
        super(GridRow, self).__init__(**kwargs)

        # Example data:
        #
        #    'cls_dicts': [{'cls': GridCell,
        #                   'kwargs': {'text': "Left"}},
        #                   'cls': GridCell,
        #                   'kwargs': {'text': "Right"}]

        # There is an index to the data item this grid row view represents. Get
        # it from kwargs and pass it along to children (cells) in the loop
        # below.
        index = kwargs['index']

        col_index = 0
        for cls_dict in kwargs['cls_dicts']:
            cls = cls_dict['cls']
            cls_kwargs = cls_dict.get('kwargs', None)

            if cls_kwargs:
                cls_kwargs['index'] = index + col_index

                if 'selection_target' not in cls_kwargs:
                    cls_kwargs['selection_target'] = self

                if 'text' not in cls_kwargs:
                    cls_kwargs['text'] = kwargs['text']

                if 'is_representing_cell' in cls_kwargs:
                    self.representing_cell = cls

                self.add_widget(cls(**cls_kwargs))
            else:
                cls_kwargs = {}
                cls_kwargs['index'] = index + col_index
                if 'text' in kwargs:
                    cls_kwargs['text'] = kwargs['text']
                self.add_widget(cls(**cls_kwargs))
            col_index += 1

    def select(self, *args):
        self.background_color = self.selected_color

    def deselect(self, *args):
        self.background_color = self.deselected_color

    # Selection within a row, all of it or only some cells, is handled here.
    # For column selection, we report the cell selection up to the grid
    # adapter.

    def select_from_child(self, child, *args):
        if self.adapter.selection_mode in ['select-by-rows', ]:
            for c in self.children:
                if c is not child:
                    c.select_from_composite(*args)
        elif self.adapter.selection_mode in ['select-by-columns', ]:
            self.adapter.select_from_child(self, *args)

    def deselect_from_child(self, child, *args):
        if self.adapter.selection_mode in ['select-by-rows', ]:
            for c in self.children:
                if c is not child:
                    c.deselect_from_composite(*args)
        elif self.adapter.selection_mode in ['select-by-columns', ]:
            self.adapter.deselect_from_child(self, *args)

    def __repr__(self):
        if self.representing_cell is not None:
            return str(self.representing_cell)
        else:
            return super(GridRow, self).__repr__()


Builder.load_string('''
<GridView>:
    container: container
    ScrollView:
        pos: root.pos
        on_scroll_y: root._scroll(args[1])
        do_scroll_x: False
        GridLayout:
            cols: 1
            id: container
            size_hint_y: None
''')

Builder.load_string('''
<TshirtmanGridView>:
    top_row: top_row
    left_row: left_row
    data: data

    orientation: 'vertical'

    Widget:
        id: parent_top_row
        size_hint_y: None
        height: '1cm'
        BoxLayout:
            id: top_row
            y: parent_top_row.y
            x: data.x
            height: parent_top_row.height
            width: data.width

    BoxLayout:
        Widget:
            id: parent_left_row
            size_hint_x: None
            width: '1cm'
            BoxLayout:
                orientation: 'vertical'
                id: left_row
                x: parent_left_row.x
                y: data.y
                height: data.height
                width: parent_left_row.width

        ScrollView
            GridLayout:
                size_hint: None, None
                id: data
                cols: 10
                size: 2000, 2000
''')


class TshirtmanGridView(BoxLayout):
    left_row = ObjectProperty(None)
    top_row = ObjectProperty(None)
    data = ObjectProperty(None)

    def __init__(self, **kw):
        super(MyGridView, self).__init__(**kw)
        self.bind(left_row=self.populate)
        self.bind(top_row=self.populate)
        self.bind(data=self.populate)

    def populate(self, *args):
        if self.top_row and self.left_row and self.data:
            for i in xrange(10):
                self.left_row.add_widget(Button(text=str(i)))
                self.top_row.add_widget(Button(text=str(i)))
                for j in xrange(10):
                    self.data.add_widget(Label(text=str(10 * i + j)))


class GridView(AbstractView, EventDispatcher):
    ''':class:`~kivy.uix.listview.GridView` is a primary high-level widget,
    handling the common task of presenting grid rows in a scrolling list.

    The adapter property comes via the mixed in
    :class:`~kivy.uix.abstractview.AbstractView` class.

    :class:`~kivy.uix.listview.GridView` also subclasses
    :class:`EventDispatcher` for scrolling.  The event *on_scroll_complete* is
    used in refreshing the main view.
    '''

    container = ObjectProperty(None)
    '''The container is a :class:`~kivy.uix.gridlayout.GridLayout` widget held
    within a :class:`~kivy.uix.scrollview.ScrollView` widget.  (See the
    associated kv block in the Builder.load_string() setup). Grid row view
    instances managed and provided by the dict adapter are added to this
    container.  The container is cleared with a call to clear_widgets() when
    the grid is rebuilt by the populate() method. A padding
    :class:`~kivy.uix.widget.Widget` instance is also added as needed,
    depending on the row height calculations.

    :data:`container` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    row_height = NumericProperty(None)
    '''The row_height property is calculated on the basis of the height of the
    container and the number of grid rows.

    :data:`row_height` is a :class:`~kivy.properties.NumericProperty`,
    default to None.
    '''
    scrolling = BooleanProperty(False)
    '''If the scroll_to() method is called while scrolling operations are
    happening, a call recursion error can occur. scroll_to() checks to see that
    scrolling is False before calling populate(). scroll_to() dispatches a
    scrolling_complete event, which sets scrolling back to False.

    :data:`scrolling` is a :class:`~kivy.properties.BooleanProperty`,
    default to False.
    '''

    _index = NumericProperty(0)
    _sizes = DictProperty({})
    _count = NumericProperty(0)

    _wstart = NumericProperty(0)
    _wend = NumericProperty(None)

    def __init__(self, **kwargs):
        # Check for an adapter argument. If it doesn't exist, we
        # assume that we must make a default GridAdapter using rows and cols
        # integer arguments, to make a simple grid, if they were provided, or
        # we are to make a default GridAdapter from row_keys and col_keys lists
        # of keys, if they were provided. If neither of these sets of arguments
        # were provided, or if they fail checks, raise an exception.
        if 'adapter' not in kwargs:
            row_keys = []
            col_keys = []
            if 'row_keys' not in kwargs or 'col_keys' not in kwargs:
                if 'rows' not in kwargs or 'cols' not in kwargs:
                    msg = ('GridView: row_keys and col_keys key lists, or '
                           'rows and cols integer arguments, or a grid '
                           'adapter needed.')
                    raise Exception(msg)
                else:
                    if not isinstance(kwargs['rows'], int):
                        msg = 'GridView: rows must be an integer value'
                        raise Exception(msg)
                    if not isinstance(kwargs['cols'], int):
                        msg = 'GridView: cols must be an integer value'
                        raise Exception(msg)
                    row_keys = [i for i in xrange(kwargs['rows'])]
                    col_keys = [j for j in xrange(kwargs['cols'])]
            else:
                row_keys = kwargs['row_keys']
                col_keys = kwargs['col_keys']

            data = {}
            for row_key in row_keys:
                data[row_key] = {}
                data[row_key]['text'] = str(row_key)
                for col_key in col_keys:
                    data[row_key][col_key] = \
                            {'text': "{0},{1}".format(row_key, col_key)}

            args_converter = \
                lambda rec: \
                    {'text': rec['text'],
                     'size_hint_y': None,
                     'height': 25,
                     'cls_dicts': [
                         {'cls': GridCell,
                          'kwargs': {'text': rec[col_key]['text']}}
                         for col_key in rec.keys() if col_key != 'text']}

            grid_adapter = GridAdapter(row_keys=row_keys,
                                       col_keys=col_keys,
                                       data=data,
                                       args_converter=args_converter,
                                       cls=GridRow)

            kwargs['adapter'] = grid_adapter

        super(GridView, self).__init__(**kwargs)

        self.register_event_type('on_scroll_complete')

        self._trigger_populate = Clock.create_trigger(self._spopulate, -1)

        self.bind(size=self._trigger_populate,
                  pos=self._trigger_populate,
                  adapter=self._trigger_populate)

        # The bindings setup above sets self._trigger_populate() to fire
        # when the adapter changes, but we also need this binding for when
        # adapter.data and other possible triggers change for view updating.
        # We don't know that these are, so we ask the adapter to set up the
        # bindings back to the view updating function here.
        self.adapter.bind_triggers_to_view(self._trigger_populate)

    def _scroll(self, scroll_y):
        if self.row_height is None:
            return
        scroll_y = 1 - min(1, max(scroll_y, 0))
        container = self.container
        mstart = (container.height - self.height) * scroll_y
        mend = mstart + self.height

        # convert distance to index
        rh = self.row_height
        istart = int(ceil(mstart / rh))
        iend = int(floor(mend / rh))

        istart = max(0, istart - 1)
        iend = max(0, iend - 1)

        if istart < self._wstart:
            rstart = max(0, istart - 10)
            self.populate(rstart, iend)
            self._wstart = rstart
            self._wend = iend
        elif iend > self._wend:
            self.populate(istart, iend + 10)
            self._wstart = istart
            self._wend = iend + 10

    def _spopulate(self, *dt):
        self.populate()

    def populate(self, istart=None, iend=None):
        '''
        This method is a slightly modified copy of the same function in
        :class:`~kivy.uix.listview.ListView`.
        '''
        container = self.container
        sizes = self._sizes
        rh = self.row_height

        # ensure we know what we want to show
        if istart is None:
            istart = self._wstart
            iend = self._wend

        # clear the view
        container.clear_widgets()

        # guess only ?
        if iend is not None:

            # fill with a "padding"
            fh = 0
            for x in xrange(istart):
                fh += sizes[x] if x in sizes else rh
            container.add_widget(Widget(size_hint_y=None, height=fh))

            # now fill with real row_view
            index = istart
            while index <= iend:
                row_view = self.adapter.get_view(index)
                index += 1
                if row_view is None:
                    continue
                sizes[index] = row_view.height
                container.add_widget(row_view)
        else:
            available_height = self.height
            real_height = 0
            index = self._index
            count = 0
            while available_height > 0:
                row_view = self.adapter.get_view(index)
                if row_view is None:
                    break
                sizes[index] = row_view.height
                index += 1
                count += 1
                container.add_widget(row_view)
                available_height -= row_view.height
                real_height += row_view.height

            self._count = count

            # extrapolate the full size of the container from the size
            # of view instances in the adapter
            if count:
                container.height = \
                    real_height / count * self.adapter.get_count()
                if self.row_height is None:
                    self.row_height = real_height / count

    def scroll_to(self, index=0):
        if not self.scrolling:
            self.scrolling = True
            self._index = index
            self.populate()
            self.dispatch('on_scroll_complete')

    def on_scroll_complete(self, *args):
        self.scrolling = False
