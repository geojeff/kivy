'''
GridAdapter
===========

.. versionadded:: 1.5

.. warning::

    This widget is still experimental, and his API is subject to change in a
    future version.

:class:`~kivy.adapters.gridadapter.GridAdapter` is an adapter around a python
dictionary of records. It extends the list-like capabilities of
:class:`~kivy.adapters.listadapter.ListAdapter`.

If you wish to have a bare-bones list adapter, without selection, use
:class:`~kivy.adapters.simplelistadapter.SimpleListAdapter`.

'''

__all__ = ('GridAdapter', )

from kivy.properties import ListProperty, DictProperty
from kivy.lang import Builder
from kivy.adapters.listadapter import ListAdapter
from kivy.adapters.models import SelectableDataItem


class GridAdapter(ListAdapter):
    ''':class:`~kivy.adapters.gridadapter.GridAdapter` is an adapter around a
    python dictionary of records. It extends the list-like capabilities of
    :class:`~kivy.adapters.listadapter.ListAdapter`.
    '''

    row_keys = ListProperty([])
    '''The row_keys list property contains a list of hashable objects (can be
    strings). A required args_converter will receive the record from a lookup
    in the data, for instantiation of grid row view class instances.

    Length of this list is the number of rows.

    :data:`row_keys` is a :class:`~kivy.properties.ListProperty`, default
    to [].
    '''

    col_keys = ListProperty([])
    '''The col_keys list property contains a list of hashable objects (can be
    strings). A required args_converter will receive the record from a lookup
    in the data, for instantiation of grid cell view class instances.

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
        if stale_keys:
            data_keys = self.data.keys()
            self.row_keys = data_keys
            self.col_keys = self.data[self.row_keys[0]].keys()
        self.delete_cache()
        self.initialize_selection()

    # Override ListAdapter.update_for_new_data().
    def update_for_new_data(self, *args):
        self.initialize_row_and_col_keys()

    # Note: this is not len(self.data).
    def get_count(self):
        return len(self.row_keys)

    def get_data_item(self, index):
        if index < 0 or index >= len(self.row_keys):
            return None
        return self.data[self.row_keys[index]]

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
