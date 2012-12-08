'''
GridAdapter
===========

.. versionadded:: 1.5

.. warning::

    This code is still experimental, and his API is subject to change in a
    future version.

:class:`~kivy.adapters.gridadapter.GridAdapter` is an adapter around a python
dictionary of records.

Selection operations, as in :class:`ListAdapter`, are a main concern for the
class.

From :class:`Adapter`, :class:`GridAdapter` gets cls, template, and
args_converter properties.

and adds several for selection:

* *selection*, a list of selected grid cells.

* *selection_mode*, 'row-single', 'row-multiple',
                'column-single', 'column-multiple',
                'cell-single', 'cell-multiple', 'none'

* *allow_empty_selection*, a boolean -- False, and a selection is forced;
  True, and only user or programmatic action will change selection, and it can
  be empty.

and several methods used in selection operations.

:class:`~kivy.adapters.listadapter.GridAdapter` dispatches the
*on_selection_change* event.

    :Events:
        `on_selection_change`: (view, view list )
            Fired when selection changes

'''

__all__ = ('GridAdapter', )

import inspect
from kivy.event import EventDispatcher
from kivy.adapters.adapter import Adapter
from kivy.adapters.models import SelectableDataItem
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.properties import DictProperty
from kivy.properties import BooleanProperty
from kivy.properties import OptionProperty
from kivy.properties import NumericProperty
from kivy.lang import Builder


class GridAdapter(Adapter, EventDispatcher):
    ''':class:`~kivy.adapters.gridadapter.GridAdapter` is an adapter around a
    python dictionary of records. It extends the list-like capabilities of
    :class:`~kivy.adapters.listadapter.ListAdapter`.
    '''

    row_keys = ListProperty([])
    '''The row_keys list property contains a list of hashable objects (can be
    strings). A required args_converter will receive a row record from a lookup
    in the data, for instantiation of grid cell class instances making up a
    grid row.

    Length of this list is the number of rows.

    :data:`row_keys` is a :class:`~kivy.properties.ListProperty`, default
    to [].
    '''

    col_keys = ListProperty([])
    '''The col_keys list property contains a list of hashable objects (can be
    strings). A required args_converter will receive data for a row, as noted
    for the row_keys property. As grid cell view class instances are created
    within a row, the col_keys will be set.

    Length of this list is the number of cols.

    :data:`col_keys` is a :class:`~kivy.properties.ListProperty`, default
    to [].
    '''

    data = DictProperty(None)
    '''A dict that indexes records by keys that are (row_key, col_key) tuples:

    data[row_key][col_key] = grid cell data item

    The values can be strings, class instances, dicts, etc. These form the data
    for building individual grid cells within grid rows.

    :data:`data` is a :class:`~kivy.properties.DictProperty`, default
    to None.
    '''

    selection = ListProperty([])
    '''The selection list property is the container for selected grid cells.

    :data:`selection` is a :class:`~kivy.properties.ListProperty`, default
    to [].
    '''

    selection_mode = OptionProperty('cell-single',
            options=('none', 'row-single', 'row-multiple',
                'column-single', 'column-multiple',
                'cell-single', 'cell-multiple'))
    '''
    Selection modes:

       * *none*, use the list as a simple list (no select action). This option
         is here so that selection can be turned off, momentarily or
         permanently, for an existing grid adapter.

    :data:`selection_mode` is an :class:`~kivy.properties.OptionProperty`,
    default to 'cell-single'.
    '''

    propagate_selection_to_data = BooleanProperty(False)
    '''Normally, data items are not selected/deselected, because the data items
    might not have an is_selected boolean property -- only the item view for a
    given data item is selected/deselected, as part of the maintained selection
    list. However, if the data items do have an is_selected property, or if
    they mix in :class:`~kivy.adapters.models.SelectableDataItem`, the
    selection machinery can propagate selection to data items. This can be
    useful for storing selection state in a local database or backend database
    for maintaining state in game play or other similar needs. It is a
    convenience function.

    To propagate selection or not?

    Consider a shopping list application for shopping for fruits at the
    market. The app allows selection of fruits to buy for each day of the
    week, presenting seven lists, one for each day of the week. Each list is
    loaded with all the available fruits, but the selection for each is a
    subset. There is only one set of fruit data shared between the lists, so
    it would not make sense to propagate selection to the data, because
    selection in any of the seven lists would clobber and mix with that of the
    others.

    However, consider a game that uses the same fruits data for selecting
    fruits available for fruit-tossing. A given round of play could have a
    full fruits list, with fruits available for tossing shown selected. If the
    game is saved and rerun, the full fruits list, with selection marked on
    each item, would be reloaded fine if selection is always propagated to the
    data. You could accomplish the same functionality by writing code to
    operate on list selection, but having selection stored on the data might
    prove convenient in some cases.

    :data:`propagate_selection_to_data` is a
    :class:`~kivy.properties.BooleanProperty`,
    default to False.
    '''

    allow_empty_selection = BooleanProperty(True)
    '''allow_empty_selection may be used for cascading selection between
    several grid views, or between a grid view and an observing view. Such
    automatic maintainence of selection is important for all but simple
    list displays. Set allow_empty_selection False, so that selection is
    auto-initialized, and always maintained, and so that any observing views
    may likewise be updated to stay in sync.

    :data:`allow_empty_selection` is a
    :class:`~kivy.properties.BooleanProperty`,
    default to True.
    '''

    selection_limit = NumericProperty(-1)
    '''When selection_mode is multiple, if selection_limit is non-negative,
    this number will limit the number of selected items. It can even be 1,
    which is equivalent to singular selection. This is because a program could
    be programmatically changing selection_limit dynamically, and all possible
    values should be included.

    If selection_limit is not set, the default is -1, meaning that no limit
    will be enforced.

    :data:`selection_limit` is a :class:`~kivy.properties.NumericProperty`,
    default to -1 (no limit).
    '''

    cached_views = DictProperty({})
    '''View instances for data items are instantiated and managed in the
    adapter. Here we maintain a dictionary containing the view
    instances keyed to the indices in the data.

    This dictionary works as a cache. get_view() only asks for a view from
    the adapter if one is not already stored for the requested index.

    :data:`cached_views` is a :class:`~kivy.properties.DictProperty`,
    default to {}.
    '''

    def __init__(self, **kwargs):
        if 'row_keys' in kwargs:
            if type(kwargs['row_keys']) not in (tuple, list):
                msg = 'GridAdapter: row_keys must be tuple or list'
                raise Exception(msg)
        else:
            raise Exception('GridAdapter: row_keys is required')

        if 'col_keys' in kwargs:
            if type(kwargs['col_keys']) not in (tuple, list):
                msg = 'GridAdapter: col_keys must be tuple or list'
                raise Exception(msg)
        else:
            raise Exception('GridAdapter: col_keys is required')

        super(GridAdapter, self).__init__(**kwargs)

        self.register_event_type('on_selection_change')

        self.bind(selection_mode=self.selection_mode_changed,
                  allow_empty_selection=self.check_for_empty_selection,
                  data=self.update_for_new_data)

        self.update_for_new_data()

        self.bind(row_keys=self.initialize_row_and_col_keys)
        self.bind(col_keys=self.initialize_row_and_col_keys)

    def bind_triggers_to_view(self, func):
        self.bind(row_keys=func)
        self.bind(col_keys=func)
        self.bind(data=func)

    # self.data is paramount to self.row_keys and self.col_keys. If row_keys or
    # col_keys is reset to mismatch data, force a reset of row_keys to
    # data.keys() and col_keys to data[data.keys.()[0]].keys(). So, in order to
    # do a complete reset of data, row_keys, and col_keys, data must be reset
    # first, followed by a reset of row_keys and col_keys, if needed.
    def initialize_row_and_col_keys(self, *args):
        stale_keys = False

        for row_key in self.row_keys:
            if not row_key in self.data:
                stale_keys = True
                break
            for col_key in self.col_keys:
                if not col_key in self.data[row_key]:
                    stale_keys = True
                    break

        if not stale_keys:
            if len(self.row_keys) != len(self.data):
                stale_keys = True

            if len(self.col_keys) != len(self.data[self.row_keys[0]]):
                stale_keys = True

        if stale_keys:
            self.row_keys = self.data.keys()

            # One of the col_keys is 'text', so skip it.
            self.col_keys = \
                [key for key in self.data[self.row_keys[0]].keys()
                        if key != 'text']

        self.delete_cache()
        self.initialize_selection()

    # This is in ListAdapter:
    #
    #def update_for_new_data(self, *args):
    #    self.delete_cache()
    #    self.initialize_selection()

    # Override ListAdapter.update_for_new_data().
    def update_for_new_data(self, *args):
        self.initialize_row_and_col_keys()

    # Note: this is not len(self.data).
    def get_count(self):
        return len(self.row_keys)

    def get_data_item_for_row(self, index):
        if index < 0 or index >= len(self.row_keys):
            return None
        return self.data[self.row_keys[index]]

    def get_data_item_for_grid_cell(self, row_key, col_key):
        if row_key < 0 or row_key >= len(self.row_keys):
            return None
        if col_key < 0 or col_key >= len(self.col_keys):
            return None
        if not row_key in self.data:
            return None
        if not col_key in self.data[row_key]:
            return None
        return self.data[row_key][col_key]

    def get_grid_cell_count(self):
        return len(self.row_keys) * len(self.col_keys)

    def get_grid_row_data(self, index):
        grid_row_data = []
        if index < 0 or index >= len(self.row_keys):
            return None
        row_key = self.row_keys[index]
        for col_key in self.col_keys:
            grid_row_data.append(self.data[row_key][col_key])
        return grid_row_data

    # [TODO] Also make methods for scroll_to_sel_start, scroll_to_sel_end,
    #        scroll_to_sel_middle.

    def trim_left_of_sel(self, *args):
        '''Cut grid rows with indices in row_keys that are less than the
        index of the first selected item, if there is selection.
        '''
        if len(self.selection) > 0:
            selected_keys = [sel.text for sel in self.selection]
            first_sel_index = self.row_keys.index(selected_keys[0])
            desired_keys = self.row_keys[first_sel_index:]
            self.data = {key: self.data[key] for key in desired_keys}

    def trim_right_of_sel(self, *args):
        '''Cut grid rows with indices in row_keys that are greater than
        the index of the last selected item, if there is selection.
        '''
        if len(self.selection) > 0:
            selected_keys = [sel.text for sel in self.selection]
            last_sel_index = self.row_keys.index(selected_keys[-1])
            desired_keys = self.row_keys[:last_sel_index + 1]
            self.data = {key: self.data[key] for key in desired_keys}

    def trim_to_sel(self, *args):
        '''Cut grid rows with indices in row_keys that are les than or
        greater than the index of the last selected item, if there is
        selection. This preserves intervening grid rows within the selected
        range.
        '''
        if len(self.selection) > 0:
            selected_keys = [sel.text for sel in self.selection]
            first_sel_index = self.row_keys.index(selected_keys[0])
            last_sel_index = self.row_keys.index(selected_keys[-1])
            desired_keys = self.row_keys[first_sel_index:last_sel_index + 1]
            self.data = {key: self.data[key] for key in desired_keys}

    def cut_to_sel(self, *args):
        '''Same as trim_to_sel, but intervening grid rows within the selected
        range are cut also, leaving only grid rows that are selected.
        '''
        if len(self.selection) > 0:
            selected_keys = [sel.text for sel in self.selection]
            self.data = {key: self.data[key] for key in selected_keys}

    def has_selection(self):
        if self.selection:
            return True
        return False

    def delete_cache(self, *args):
        self.cached_views = {}

    def selection_mode_changed(self, *args):
        if self.selection_mode == 'none':
            for selected_view in self.selection:
                self.do_selection_op('deselect', selected_view)
        else:
            self.check_for_empty_selection()

    def get_view(self, index):
        if index in self.cached_views:
            return self.cached_views[index]
        item_view = self.create_view(index)
        if item_view:
            self.cached_views[index] = item_view
        return item_view

    def create_view(self, index):
        '''This method is more complicated than the one in
        :class:`kivy.adapters.adapter.Adapter` and
        :class:`kivy.adapters.simplelistadapter.SimpleListAdapter`, because
        here we create bindings for the data item, and its children back to
        self.handle_selection(), and do other selection-related tasks to keep
        item views in sync with the data.
        '''
        item = self.get_data_item_for_row(index)
        if item is None:
            return None

        item_args = self.args_converter(item)

        item_args['index'] = index
        item_args['adapter'] = self

        if self.cls:
            view_instance = self.cls(**item_args)
        else:
            view_instance = Builder.template(self.template, **item_args)

        if self.propagate_selection_to_data:
            # The data item must be a subclass of SelectableDataItem, or must
            # have an is_selected boolean or function, so it has is_selected
            # available.  If is_selected is unavailable on the data item, an
            # exception is raised.
            #
            if isinstance(item, SelectableDataItem):
                if item.is_selected:
                    self.handle_selection(view_instance)
            elif type(item) == dict and 'is_selected' in item:
                if item['is_selected']:
                    self.handle_selection(view_instance)
            elif hasattr(item, 'is_selected'):
                if (inspect.isfunction(item.is_selected)
                        or inspect.ismethod(item.is_selected)):
                    if item.is_selected():
                        self.handle_selection(view_instance)
                else:
                    if item.is_selected:
                        self.handle_selection(view_instance)
            else:
                msg = "ListAdapter: unselectable data item for {0}"
                raise Exception(msg.format(index))

        view_instance.bind(on_release=self.handle_selection)

        for child in view_instance.children:
            child.bind(on_release=self.handle_selection)

        return view_instance

    def on_selection_change(self, *args):
        '''on_selection_change() is the default handler for the
        on_selection_change event.
        '''
        pass

    def grid_cell_view(self, row_key, col_key):
        grid_row = self.get_view(self.row_keys.index(row_key))
        for grid_cell in grid_row.children:
            if grid_cell.col_key == col_key:
                return grid_cell

    # handle_row_selection() takes advantage of the existence of GridRow,
    # using its methods to aid processing of grid_cells.
    #
    def handle_row_selection(self, row_key):
        index = self.row_keys.index(row_key)
        grid_row = self.get_view(index)

        if self.selection_mode in ['row-single',
                                   'row-multiple',
                                   'cell-multiple']:
            selected_cells_in_row = []
            unselected_cells_in_row = []
            cols = len(self.col_keys)
            half_count = cols / 2
            handled = False
            for grid_cell in grid_row.children:
                if grid_cell.is_selected:
                    selected_cells_in_row.append(grid_cell)
                else:
                    unselected_cells_in_row.append(grid_cell)
                if len(selected_cells_in_row) > half_count:
                    self.handle_selection(selected_cells_in_row[-1])
                    handled = True
                    break
                if len(unselected_cells_in_row) > half_count:
                    self.handle_selection(unselected_cells_in_row[-1])
                    handled = True
                    break
            if not handled:
                if len(selected_cells_in_row) > len(unselected_cells_in_row):
                    self.handle_selection(selected_cells_in_row[-1])
                else:
                    self.handle_selection(unselected_cells_in_row[-1])

    # handle_column_selection() has no "grid column" class to use, so there is
    # a loop over grid rows, finding the grid cells for the column.
    #
    def handle_column_selection(self, col_key):
        if self.selection_mode in ['column-single',
                                   'column-multiple',
                                   'cell-multiple']:
            selected_cells_in_column = []
            unselected_cells_in_column = []
            rows = len(self.row_keys)
            half_count = rows / 2
            handled = False
            grid_rows = [self.get_view(i) for i in xrange(len(self.row_keys))]
            for grid_row in grid_rows:
                grid_cell = grid_row.grid_cell(col_key)
                if grid_cell.is_selected:
                    selected_cells_in_column.append(grid_cell)
                else:
                    unselected_cells_in_column.append(grid_cell)
                if len(selected_cells_in_column) > half_count:
                    self.handle_selection(selected_cells_in_column[-1])
                    handled = True
                    break
                if len(unselected_cells_in_column) > half_count:
                    self.handle_selection(unselected_cells_in_column[-1])
                    handled = True
                    break
            if not handled:
                if (len(selected_cells_in_column)
                        > len(unselected_cells_in_column)):
                    self.handle_selection(selected_cells_in_column[-1])
                else:
                    self.handle_selection(unselected_cells_in_column[-1])

    def handle_selection(self, view, hold_dispatch=False, *args):

        selection_before = self.selection[:]

        selection_removals = []

        grid_row = self.get_view(self.row_keys.index(view.row_key))

        op = 'select'
        if ((self.selection_mode in ['row-single', 'row-multiple']
                and grid_row in self.selection) or (view in self.selection)):
            op = 'deselect'

        if op == 'select':
            if len(self.selection) > 0:
                if self.selection_mode in ['none',
                                           'row-single',
                                           'column-single',
                                           'cell-single']:
                    for selected_view in self.selection:
                        if hasattr(selected_view, 'col_key'):
                            selection_removals.extend(self.do_selection_op(
                                'deselect', selected_view))

            if self.selection_mode in ['row-multiple',
                                       'column-multiple',
                                       'cell-multiple']:
                # If < 0, selection_limit is not active.
                if self.selection_limit < 0:
                    self.do_selection_op('select', view)
                else:
                    if len(self.selection) < self.selection_limit:
                        self.do_selection_op('select', view)
            else:
                self.do_selection_op('select', view)
        else:
            selection_removals.extend(self.do_selection_op('deselect', view))

        if selection_removals:
            for sel_index in reversed(list(set(selection_removals))):
                del self.selection[sel_index]

            self.check_for_empty_selection(hold_dispatch=True)

        if not hold_dispatch:
            before_len = len(selection_before)
            after_len = len(self.selection)

            if after_len == before_len:
                objects_handled = []
            elif after_len > before_len:
                sb = set(selection_before)
                objects_handled = \
                        [obj for obj in self.selection if not obj in sb]
            else:
                sa = set(self.selection)
                objects_handled = \
                        [obj for obj in selection_before if not obj in sa]

            if objects_handled:
                self.dispatch('on_selection_change', objects_handled)

    def select_data_item(self, item):
        self.set_data_item_selection(item, True)

    def deselect_data_item(self, item):
        self.set_data_item_selection(item, False)

    def set_data_item_selection(self, item, value):
        if isinstance(item, SelectableDataItem):
            item.is_selected = value
        elif type(item) == dict:
            item['is_selected'] = value
        elif hasattr(item, 'is_selected'):
            if (inspect.isfunction(item.is_selected)
                    or inspect.ismethod(item.is_selected)):
                item.is_selected()
            else:
                item.is_selected = value

    def do_selection_op(self, op, view):
        selection_removals = []

        if hasattr(view, 'col_key'):
            grid_row = self.get_view(self.row_keys.index(view.row_key))
        else:
            grid_row = view

        col_key = view.col_key
        row_key = view.row_key

        # Do op for grid cell.
        if hasattr(view, 'col_key'):
            if op == 'select':
                view.select()
                view.is_selected = True
                if view not in self.selection:
                    self.selection.append(view)
            else:
                view.deselect()
                view.is_selected = False
                if view in self.selection:
                    selection_removals.append(self.selection.index(view))

        # Do op for grid_row.
        if self.selection_mode in ['row-single',
                                   'row-multiple']:
            if op == 'select':
                for grid_cell in grid_row.children:
                    if hasattr(grid_cell, 'select'):
                        grid_cell.select()
                        grid_cell.is_selected = True
                        if grid_cell not in self.selection:
                            self.selection.append(grid_cell)
            else:
                for grid_cell in grid_row.children:
                    if hasattr(grid_cell, 'deselect'):
                        grid_cell.deselect()
                        grid_cell.is_selected = False
                        if grid_cell in self.selection:
                            selection_removals.append(
                                    self.selection.index(grid_cell))

        # Do op for column.
        if self.selection_mode in ['column-single',
                                   'column-multiple']:
            for i in xrange(len(self.row_keys)):
                grid_cell = self.get_view(i).grid_cell(col_key)
                if grid_cell != view:
                    if op == 'select':
                        grid_cell.select()
                        grid_cell.is_selected = True
                        if grid_cell not in self.selection:
                            self.selection.append(grid_cell)
                    else:
                        grid_cell.deselect()
                        grid_cell.is_selected = False
                        if grid_cell in self.selection:
                            selection_removals.append(
                                    self.selection.index(grid_cell))

        if self.propagate_selection_to_data:
            if self.selection_mode == 'cell-single':
                # Selection will only extend grid-cell-deep.
                data_item = self.get_data_item_for_grid_cell(col_key, row_key)
                if op == 'select':
                    self.select_data_item(data_item)
                else:
                    self.deselect_data_item(data_item)
            elif self.selection_mode == 'row-single':
                data_item = self.get_data_item(grid_row.index)
                if op == 'select':
                    self.select_data_item(data_item)
                else:
                    self.deselect_data_item(data_item)

        return selection_removals

    def select_list(self, view_list, extend=True):
        '''The select call is made for the items in the provided view_list.

        Arguments:

            view_list: the list of item views to become the new selection, or
            to add to the existing selection

            extend: boolean for whether or not to extend the existing list
        '''
        selection_before = self.selection[:]

        if not extend:
            self.selection = []
            selection_before = []

        for view in view_list:
            self.handle_selection(view, hold_dispatch=True)

        sb = set(selection_before)
        objects_handled = [obj for obj in self.selection if not obj in sb]

        self.dispatch('on_selection_change', objects_handled)

    def deselect_list(self, l):
        selection_before = self.selection[:]

        for view in l:
            self.handle_selection(view, hold_dispatch=True)

        sa = set(self.selection)
        objects_handled = [obj for obj in selection_before if not obj in sa]

        self.dispatch('on_selection_change', objects_handled)

    def select_all(self):
        cells = []

        if self.selection_mode in ['row-single',
                                   'row-multiple']:
            for index in xrange(len(self.row_keys)):
                grid_row = self.get_view(index)
                if not grid_row.is_selected:
                    cells.append(grid_row.children[0])
        elif self.selection_mode in ['column-single',
                                     'column-multiple']:
            first_grid_row = self.get_view(0)
            for grid_cell in first_grid_row.children:
                if not grid_cell.is_selected:
                    cells.append(grid_cell)
        elif self.selection_mode in ['cell-single',
                                     'cell-multiple']:
            for index in xrange(len(self.row_keys)):
                grid_row = self.get_view(index)
                for grid_cell in grid_row.children:
                    if not grid_cell.is_selected:
                        cells.append(grid_cell)

        self.select_list(cells)

    def deselect_all(self):
        cells = []

        if self.selection_mode in ['none',
                                   'row-single',
                                   'row-multiple']:
            for row_key in self.row_keys:
                grid_row = self.get_view(row_key)
                if grid_row.is_selected:
                    cells.append(grid_row.children[0])
        elif self.selection_mode in ['column-single',
                                     'column-multiple']:
            first_grid_row = self.get_view(0)
            for grid_cell in first_grid_row.children:
                if grid_cell.is_selected:
                    cells.append(grid_cell)
        elif self.selection_mode in ['cell-single',
                                     'cell-multiple']:
            for row_key in self.row_keys:
                grid_row = self.get_view(row_key)
                for grid_cell in grid_row.children:
                    if grid_cell.is_selected:
                        cells.append(grid_cell)

        self.deselect_list(cells)

    def initialize_selection(self, *args):
        selection_before = self.selection[:]

        if len(self.selection) > 0:
            self.selection = []

        self.check_for_empty_selection(hold_dispatch=True)

        before_len = len(selection_before)
        after_len = len(self.selection)

        if after_len == before_len:
            objects_handled = []
        elif after_len > before_len:
            sb = set(selection_before)
            objects_handled = \
                    [obj for obj in self.selection if not obj in sb]
        else:
            sa = set(self.selection)
            objects_handled = \
                    [obj for obj in selection_before if not obj in sa]

        if objects_handled:
            self.dispatch('on_selection_change', objects_handled)

    def check_for_empty_selection(self, hold_dispatch=False, *args):
        if not self.allow_empty_selection:
            if len(self.selection) == 0:
                if self.selection_mode != 'none':
                    first_grid_row = self.get_view(0)
                    if first_grid_row is not None:
                        col_index = len(self.col_keys) - 1
                        grid_cell = first_grid_row.children[col_index]
                        if grid_cell:
                            self.handle_selection(grid_cell,
                                                  hold_dispatch=hold_dispatch)
