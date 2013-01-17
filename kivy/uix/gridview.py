'''
Grid View
===========

.. versionadded:: 1.5

.. warning::

    This widget is still experimental, and its API is subject to change in a
    future version.

The :class:`~kivy.uix.gridview.GridView` widget provides a scrollable/pannable
viewport that is clipped at the scrollview's bounding box, which contains a
grid cell view instances.

:class:`~kivy.uix.gridview.GridView` implements :class:`AbstractView` as a
vertical scrollable list. :class:`AbstractView` has one property, adapter.
:class:`~kivy.uix.gridview.GridView` sets adapter to be an instance of
:class:`~kivy.adapters.gridadapter.GridAdapter`.


    :Events:
        `on_scroll_complete`: (boolean, )
            Fired when scrolling completes.

Basic Example
-------------

In its simplest form, we make a gridview with 100 rows and 10 columns::

    from kivy.uix.gridview import GridView
    from kivy.uix.gridlayout import GridLayout


    class MainView(GridLayout):

        def __init__(self, **kwargs):
            kwargs['cols'] = 2
            kwargs['rows'] = 5
            kwargs['size_hint'] = (1.0, 1.0)
            super(MainView, self).__init__(**kwargs)

            grid_view = GridView(cols=10, rows=100)

            self.add_widget(grid_view)


    if __name__ == '__main__':
        from kivy.base import runTouchApp
        runTouchApp(MainView(width=800))

'''

from math import ceil, floor

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
        NumericProperty, ListProperty, BooleanProperty, StringProperty, \
        OptionProperty
from kivy.lang import Builder

__all__ = ('SelectableGridCellView', 'GridCell', 'GridShapeBase', 'GridRow',
           'HeaderButton', 'GridView', )


class SelectableGridCellView(SelectableView):
    '''The :class:`~kivy.uix.gridview.SelectableGridCellView` mixin is used to
    design GridCell classes that are to be instantiated by an adapter to be used
    in a gridview. From :class:`~kivy.uix.listview.SelectableView`,
    :class:`~kivy.uix.gridview.SelectableGridCellView` gets two properties,
    index and is_selected, and two methods, select() and deselect(). select()
    and deselect() are to be overridden with display code to mark items as
    selected or not, if desired.

    The row_key and col_key properties added below allow dictionary-style
    reference to grid cell views.

    The index property, inherited from
    :class:`~kivy.uix.listview.SelectableView`, is set also, and is a
    two-dimensional array-style reference, in row-major order.
    '''

    row_key = ObjectProperty(None)
    '''The row key into the underlying dict and data item this view
    represents.

    :data:`row_key` is a :class:`~kivy.properties.ObjectProperty`, default
    to None.
    '''

    col_key = ObjectProperty(None)
    '''The col key into the underlying dict and data item this view
    represents.

    :data:`col_key` is a :class:`~kivy.properties.ObjectProperty`, default
    to None.
    '''

    def __init__(self, **kwargs):
        super(SelectableGridCellView, self).__init__(**kwargs)


class GridCell(SelectableGridCellView, Button):
    ''':class:`~kivy.uix.listview.GridCell` mixes
    :class:`~kivy.uix.listview.SelectableView` with
    :class:`~kivy.uix.button.Button` to produce a button suitable for use in
    :class:`~kivy.uix.gridview.GridView`.
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

    def deselect(self, *args):
        self.background_color = self.deselected_color

    def __repr__(self):
        return self.text

# [TODO] Implement a multitouch system for adding shapes.
#
#    def on_touch_down(self, touch):
#        if not self.collide_point(touch.x, touch.y):
#            return False
#        if self in touch.ud:
#            return False
#        touch.grab(self)
#        touch.ud[self] = True
#        print touch.ud
#        return True


class GridShapeBase(SelectableGridCellView, BoxLayout):
    ''':class:`~kivy.uix.gridview.GridShapeBase` mixes
    :class:`~kivy.uix.listview.SelectableView` with :class:`BoxLayout` for a
    generic container-style item, to be used in
    :class:`~kivy.uix.gridview.GridView`.
    '''

    background_color = ListProperty([1, 1, 1, 1])
    '''ListItem sublasses Button, which has background_color, but
    for a container-style item, we must add this property.

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
    grid cell container in __repr__()?

    :data:`representing_cell` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    adapter = ObjectProperty(None)
    '''A reference to the managing adapter for this view's parent list-type
    widget, which is needed for calling back during selection operations.

    :data:`adapter` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    children_dict = DictProperty({})
    '''A dictionary of grid cell view instances, keyed by row_key and col_key
    for easier grid cell lookup, e.g., children_dict[row_key][col_key].

    For a GridRow (shape = 'row'), grid cells are instantiated here,
    and this dictionary is created, and used for grid cell lookup into the
    children list. The GridRow is used as an intermediate container to
    facilitate scrolling.

    For a GridColumn (shape = 'column'), and other shapes, grid cells are not
    instantiated here, and must be looked up across other rows in the adapter.

    :data:`key_indices` is an :class:`~kivy.properties.DictProperty`,
    default to {}.
    '''

    cell_keys = ListProperty([])
    '''This is a list of (row_key, col_key) tuples, for the grid cells
    contained here.

    :data:`cell_keys` is an :class:`~kivy.properties.ListProperty`,
    default to [].
    '''

    shape = OptionProperty('row',
            options=('row', 'column', 'block', 'diagonal', 'checkerboard',
                     'border', 'path', 'shape', 'set'))
    '''The shape property describes the way grid cells are arranged in this
    container.

    **Only row, column, and block have been implemented so far.**

    :data:`shape` is an :class:`~kivy.properties.OptionProperty`,
    default to 'row'.
    '''

    cell_args = ListProperty([])
    '''A list of args dicts for grid cells to be instantiated.

    :data:`cell_args` is an :class:`~kivy.properties.ListProperty`,
    default to [].
    '''

    origin_grid_cells = ListProperty([])
    '''What cell was clicked or touched to add this shape? It would be the
    first element.

    What cells were touched to add this shape? That would be the entire list.

    :data:`origin_grid_cells` is an :class:`~kivy.properties.ListProperty`,
    default to [].
    '''

    specific_shape = StringProperty('')
    '''A shape such as block can have variants suchs as a 2x2 cell block, or
    a 16x16 block. Each could have specific_shape names, but would in general,
    just be different sizes of block. This gives flexibility to the different
    shape types.

    :data:`origin_grid_cell` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    def __init__(self, **kwargs):
        if not 'shape' in kwargs:
            raise Exception("GridShapeBase: Missing shape argument.")

        super(GridShapeBase, self).__init__(**kwargs)

        if self.cell_args:
            # Example cell_args:
            #
            #    'cell_args': [{'cls': GridCell,
            #                   'kwargs': {'text': "Left"}},
            #                   'cls': GridCell,
            #                   'kwargs': {'text': "Right"}]

            cell_count = 0
            for cell_args_dict in self.cell_args:
                if not 'cls' in cell_args_dict:
                    msg = ("GridShapeBase: Must provide grid cell cls for "
                           "cell: {0}.").format(cell_count)
                    raise Exception(msg)

                if not 'index' in cell_args_dict:
                    msg = ("GridShapeBase: Must provide grid cell index for "
                           "cell {0}.").format(cell_count)
                    raise Exception(msg)

                if not 'row_key' in cell_args_dict:
                    msg = ("GridShapeBase: Must provide grid row_key for "
                           "cell: {0}.").format(cell_count)
                    raise Exception(msg)

                if not 'col_key' in cell_args_dict:
                    msg = ("GridShapeBase: Must provide grid col_key for "
                           "cell: {0}.").format(cell_count)
                    raise Exception(msg)

                if not 'text' in cell_args_dict:
                    cell_args_dict['text'] = kwargs['text']

                cls = cell_args_dict['cls']

                if 'is_representing_cell' in cell_args_dict:
                    self.representing_cell = cls

                row_key = cell_args_dict['row_key']
                col_key = cell_args_dict['col_key']

                # Copy the args, except for cls.
                cls_args = {k: cell_args_dict[k]
                                for k in cell_args_dict if k != 'cls'}

                self.add_widget(cls(**cls_args))

                if not row_key in self.children_dict:
                    self.children_dict[row_key] = {}

                self.children_dict[row_key][col_key] = self.children[0]

                self.cell_keys.append((row_key, col_key))

                cell_count += 1
        else:
            # The grid cells are stored, at least partially, in other rows in
            # the adapter.
            for row_key, col_key in self.cell_keys:
                if not row_key in self.children_dict:
                    self.children_dict[row_key] = {}

                self.children_dict[row_key][col_key] = \
                        self.adapter.grid_cell_view(row_key, col_key)

        self.bind(cell_keys=self.cell_keys_changed)

    def cell_keys_changed(self, *args):
        self.children_dict = {}

        for row_key, col_key in self.cell_keys:
            if not row_key in self.children_dict:
                self.children_dict[row_key] = {}

            self.children_dict[row_key][col_key] = \
                    self.adapter.grid_cell_view(row_key, col_key)

    def grid_cell(self, row_key, col_key):
        return self.children_dict[row_key][col_key]

    def select(self, *args):
        self.background_color = self.selected_color

    def deselect(self, *args):
        self.background_color = self.deselected_color

    def __repr__(self):
        if self.representing_cell is not None:
            return str(self.representing_cell)
        else:
            return super(GridShapeBase, self).__repr__()

    def cells(self):
        cells = []
        for row_key in self.children_dict:
            for col_key in self.children_dict[row_key]:
                cells.append(self.children_dict[row_key][col_key])
        return cells


class GridRow(GridShapeBase):
    ''':class:`~kivy.uix.gridview.GridRow` is the primary container of grid
    cells in a grid: grid cells that make up the grid are children of rows.
    '''

    def __init__(self, **kwargs):

        # GridShapeBase expects a prepared cell_args list, complete with
        # row_key, col_key, and other cell property settings. We will construct
        # the cell_args list and and pass it.
        cell_args = []

        # There is an index to the data item this grid cell container
        # represents. Get it from kwargs and pass it along to children (cells)
        # in the loop below.
        index = kwargs['index']

        row_key = kwargs['adapter'].row_keys[index]
        col_keys = kwargs['adapter'].col_keys
        cols = len(kwargs['cell_args'])

        if cols != len(col_keys):
            msg = "GridRow: # of cell_args ({0}) mismatches # of columns ({1})"
            raise Exception(msg.format(cols, len(col_keys)))

        col_index = 0
        for cls_cell_args, col_key in zip(kwargs['cell_args'], col_keys):
            cls_kwargs = {}

            if 'kwargs' in cls_cell_args:
                for key in cls_cell_args['kwargs']:
                    cls_kwargs[key] = cls_cell_args['kwargs'][key]

            cls_kwargs['cls'] = cls_cell_args['cls']

            cls_kwargs['index'] = (index * cols) + col_index
            cls_kwargs['row_key'] = row_key
            cls_kwargs['col_key'] = col_key

            if not 'text' in kwargs and not 'text' in cls_kwargs:
                cls_kwargs['text'] = "{0}{1}".format(row_key, col_key)

            cell_args.append(cls_kwargs)

            col_index += 1

        kwargs['row_key'] = row_key
        kwargs['cell_args'] = cell_args
        kwargs['shape'] = 'row'

        super(GridRow, self).__init__(**kwargs)

        for cell in self.children:
            if (not hasattr(cell, 'selection_target')
                    or not cell.selection_target):
                cell.selection_target = self

    # Override, to change API from (row_key, col_key) to just call for col_key.
    def grid_cell(self, col_key):
        return self.children_dict[self.row_key][col_key]


Builder.load_string('''
<GridView>:
    rows_header: rows_header
    columns_header: columns_header
    container: container

    orientation: 'vertical'

    Widget:
        id: parent_columns_header
        size_hint_y: None
        height: '1cm'
        BoxLayout:
            id: columns_header
            y: parent_columns_header.y
            x: container.x
            height: parent_columns_header.height
            width: container.width

    BoxLayout:
        Widget:
            id: parent_rows_header
            size_hint_x: None
            width: '1cm'

            BoxLayout:
                orientation: 'vertical'
                id: rows_header
                x: parent_rows_header.x
                y: container.y
                height: container.height
                width: parent_rows_header.width

        ScrollView
            GridLayout:
                size_hint_y: None
                id: container
                cols: 1

''')


class HeaderButton(Button):
    '''The :class:`~kivy.uix.gridview.HeaderButtonView` mixin is used to design
    header row or column buttons to be used in a gridview.
    '''

    key = ObjectProperty(None)
    '''A key into the underlying data (either a row key or a col key).

    :data:`key` is a :class:`~kivy.properties.ObjectProperty`, default
    to None.
    '''

    is_selected = BooleanProperty(False)
    '''A boolean for the state of selection.

    :data:`is_selected` is a :class:`~kivy.properties.BooleanProperty`, default
    to False.
    '''

    def __init__(self, **kwargs):
        super(HeaderButton, self).__init__(**kwargs)

    def select(self, *args):
        self.background_color = self.selected_color

    def deselect(self, *args):
        self.background_color = self.deselected_color


class GridView(BoxLayout, AbstractView, EventDispatcher):
    ''':class:`~kivy.uix.listview.GridView` is a primary high-level widget,
    handling the task of presenting grid cell items. The view is row-centric,
    in the sense that GridRows are intermediate containers, having a list of
    grid cells, and behaving as selectable rows in a scrolling list. However,
    GridRow is just one of several possible grid shapes: columns, blocks, etc.
    are also supported for selection.

    The adapter property comes via the mixed in
    :class:`~kivy.uix.abstractview.AbstractView` class.

    :class:`~kivy.uix.listview.GridView` also subclasses
    :class:`EventDispatcher` for scrolling.  The event *on_scroll_complete* is
    used in refreshing the main view.
    '''

    columns_header = ObjectProperty(None)
    '''The columns_header is the column of header buttons normally placed on the
    left side of the grid.

    :data:`columns_header` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    rows_header = ObjectProperty(None)
    '''The rows_header is the row of header buttons normally placed on the top
    side of the grid.

    :data:`rows_header` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    rows_header_view_cls = ObjectProperty(None)
    '''
    A class for instantiating a header row item. (Use this or template).

    :data:`rows_header_view_cls` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    rows_header_view_template = ObjectProperty(None)
    '''
    A class for instantiating a header row item. (Use this or
    rows_header_view_cls).

    :data:`rows_header_view_cls` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    columns_header_view_cls = ObjectProperty(None)
    '''
    A class for instantiating a header col item. (Use this or template).

    :data:`columns_header_view_cls` is an
    :class:`~kivy.properties.ObjectProperty`, default to None.
    '''

    columns_header_view_template = ObjectProperty(None)
    '''
    A class for instantiating a header col item. (Use this or
    columns_header_view_cls).

    :data:`columns_header_view_template` is an
    :class:`~kivy.properties.ObjectProperty`, default to None.
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
        if 'row_height' not in kwargs:
            self.row_height = 25

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
                lambda row_index, rec: \
                    {'text': rec['text'],
                     'size_hint_y': None,
                     'height': 25,
                     'cell_args': [
                         {'cls': GridCell,
                          'kwargs': {'text': rec[col_key]['text']}}
                         for col_key in rec.keys() if col_key != 'text']}

            grid_adapter = GridAdapter(row_keys=row_keys,
                                       col_keys=col_keys,
                                       data=data,
                                       args_converter=args_converter,
                                       selection_mode='row-single',
                                       allow_empty_selection=True,
                                       cls=GridRow)

            kwargs['adapter'] = grid_adapter

        super(GridView, self).__init__(**kwargs)

        if (not self.rows_header_view_cls
                and not self.rows_header_view_template):
            self.rows_header_view_cls = HeaderButton
        if (not self.columns_header_view_cls
                and not self.columns_header_view_template):
            self.columns_header_view_cls = HeaderButton

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

    # Terminology can be confusing here. The columns_header runs left-to-right.
    def columns_header_view(self, col_key):
        col_button = None
        header_args = {}
        header_args['text'] = str(col_key)
        header_args['key'] = col_key
        header_args['height'] = self.row_height
        if self.columns_header_view_cls:
            col_button = self.columns_header_view_cls(**header_args)
        elif self.columns_header_view_template:
            col_button = Builder.template(self.columns_header_view_template,
                                          **header_args)
        if col_button:
            col_button.bind(on_release=self.handle_columns_header_action)
        return col_button

    # Terminology can be confusing here. The rows_header runs up-and-down.
    def rows_header_view(self, index):
        if index < 0 or index >= len(self.adapter.row_keys):
            return None
        row_key = self.adapter.row_keys[index]
        row_button = None
        header_args = {}
        header_args['text'] = str(row_key)
        header_args['key'] = row_key
        header_args['height'] = self.row_height
        if self.rows_header_view_cls:
            row_button = self.rows_header_view_cls(**header_args)
        elif self.rows_header_view_template:
            row_button = Builder.template(self.rows_header_view_template,
                                          **header_args)
        if row_button:
            row_button.bind(on_release=self.handle_rows_header_action)
        return row_button

    def handle_rows_header_action(self, button, *args):
        self.adapter.handle_row_selection(button.key)

    def handle_columns_header_action(self, button, *args):
        self.adapter.handle_column_selection(button.key)

    def _scroll(self, scroll_y):
        # [TODO] GridView -- row_height default is now 25, so needed?
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
        columns_header = self.columns_header
        rows_header = self.rows_header
        sizes = self._sizes
        rh = self.row_height

        # ensure we know what we want to show
        if istart is None:
            istart = self._wstart
            iend = self._wend

        # clear the view
        container.clear_widgets()
        if columns_header:
            columns_header.clear_widgets()
        if rows_header:
            rows_header.clear_widgets()

        # guess only ?
        if iend is not None:

            # fill with a "padding"
            fh = 0
            for x in xrange(istart):
                fh += sizes[x] if x in sizes else rh
            container.add_widget(Widget(size_hint_y=None, height=fh))
            rows_header.add_widget(Widget(size_hint_y=None, height=fh))

            # now fill with real row_view
            index = istart
            while index <= iend:
                row_view = self.adapter.get_view(index)
                rows_header_view = self.rows_header_view(index)
                index += 1
                if row_view is None:
                    continue
                sizes[index] = row_view.height
                container.add_widget(row_view)
                rows_header.add_widget(rows_header_view)
        else:
            available_height = self.height
            real_height = 0
            index = self._index
            count = 0
            while available_height > 0:
                row_view = self.adapter.get_view(index)
                if row_view is None:
                    break
                rows_header_view = self.rows_header_view(index)
                sizes[index] = row_view.height
                index += 1
                count += 1
                container.add_widget(row_view)
                rows_header.add_widget(rows_header_view)
                available_height -= row_view.height
                real_height += row_view.height

            self._count = count

            # extrapolate the full size of the container from the size
            # of view instances in the adapter
            if count:
                container.height = real_height
                rows_header.height = real_height
                # [TODO] GridView -- row_height default is now 25, so needed?
                if self.row_height is None:
                    self.row_height = real_height / count

        # After self.row_height guaranteed.
        for col_key in self.adapter.col_keys:
            columns_header.add_widget(self.columns_header_view(col_key))

    def scroll_to(self, index=0):
        if not self.scrolling:
            self.scrolling = True
            self._index = index
            self.populate()
            self.dispatch('on_scroll_complete')

    def on_scroll_complete(self, *args):
        self.scrolling = False
