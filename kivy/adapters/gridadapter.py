'''
GridAdapter
===========

.. versionadded:: 1.5

.. warning::

    This widget is still experimental, and his API is subject to change in a
    future version.

:class:`~kivy.adapters.gridadapter.GridAdapter` is an adapter around a python
dictionary of records.

Selection operations, as in :class:`ListAdapter`, are a main concern for the class.

From :class:`Adapter`, :class:`GridAdapter` gets cls, template, and
args_converter properties.

and adds several for selection:

* *selection*, a list of selected items.

* *selection_mode*, 'single-by-rows', 'multiple-by-rows',
                'single-by-columns', 'multiple-by-columns',
                'single-by-grid-cells', 'multiple-by-grid-cells', 'none'

* *allow_empty_selection_rows*, a boolean -- False, and a selection is forced;
  True, and only user or programmatic action will change selection, and it can
  be empty. There are equivalent properties for columns and grid cells,
  allow_empty_selection_columns, allow_empty_selection_cells.

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

    selection = ListProperty([])
    '''The selection list property is the container for selected items.

    :data:`selection` is a :class:`~kivy.properties.ListProperty`, default
    to [].
    '''

    selection_mode = OptionProperty('single-by-grid-cells',
            options=('none', 'single-by-rows', 'multiple-by-rows',
                'single-by-columns', 'multiple-by-columns',
                'single-by-grid-cells', 'multiple-by-grid-cells'))
    '''
    Selection modes:

       * *none*, use the list as a simple list (no select action). This option is
         here so that selection can be turned off, momentarily or permanently,
         for an existing grid adapter.

       * *single-*, multi-touch/click ignored. single item selecting only, for
         variants: single-by-rows, single-by-columns, single-by-grid-cells.

       * *multiple-*, multi-touch / incremental addition to selection allowed;
         may be limited to a count by selection_limit. Variants include:
         multiple-by-rows, multiple-by-columns, multiple-by-grid-cells.

    :data:`selection_mode` is an :class:`~kivy.properties.OptionProperty`,
    default to 'single-by-grid-cells'.
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

    allow_empty_selection_rows = BooleanProperty(True)
    '''The allow_empty_selection may be used for cascading selection between
    several list views, or between a list view and an observing view. Such
    automatic maintainence of selection is important for all but simple
    list displays. Set allow_empty_selection False, so that selection is
    auto-initialized, and always maintained, and so that any observing views
    may likewise be updated to stay in sync.

    :data:`allow_empty_selection` is a 
    :class:`~kivy.properties.BooleanProperty`,
    default to True.
    '''

    allow_empty_selection_cols = BooleanProperty(True)
    '''
    Same as for allow_empty_selection_rows.
    '''

    allow_empty_selection_cells = BooleanProperty(True)
    '''
    Same as for allow_empty_selection_rows and _cols.
    '''

    selection_limit_rows = NumericProperty(-1)
    '''When selection_mode is multiple, if selection_limit is non-negative,
    this number will limit the number of selected items. It can even be 1,
    which is equivalent to single selection. This is because a program could
    be programmatically changing selection_limit on the fly, and all possible
    values should be included.

    If selection_limit is not set, the default is -1, meaning that no limit
    will be enforced.

    :data:`selection_limit` is a :class:`~kivy.properties.NumericProperty`,
    default to -1 (no limit).
    '''

    selection_limit_cols = NumericProperty(-1)
    '''
    Same as for seleciton_limit_rows.
    '''

    selection_limit_cells = NumericProperty(-1)
    '''
    Same as for seleciton_limit_rows and _cols.
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
                  allow_empty_selection_rows=self.check_for_empty_selection,
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
        if stale_keys:
            data_keys = self.data.keys()
            self.row_keys = data_keys
            self.col_keys = self.data[self.row_keys[0]].keys()
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
            
    def delete_cache(self, *args):
        self.cached_views = {}

    def selection_mode_changed(self, *args):
        if self.selection_mode == 'none':
            for selected_view in self.selection:
                self.deselect_item_view(selected_view)
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
        item = self.get_data_item(index)
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
            # The data item must be a subclass of SelectableDataItem, or must have
            # an is_selected boolean or function, so it has is_selected available.
            # If is_selected is unavailable on the data item, an exception is
            # raised.
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

    def handle_selection(self, view, hold_dispatch=False, *args):
        if view not in self.selection:
            if self.selection_mode in ['none', 'single'] and \
                    len(self.selection) > 0:
                for selected_view in self.selection:
                    self.deselect_item_view(selected_view)
            if self.selection_mode != 'none':
                if self.selection_mode == 'multiple':
                    if self.allow_empty_selection:
                        # If < 0, selection_limit is not active.
                        if self.selection_limit < 0:
                            self.select_item_view(view)
                        else:
                            if len(self.selection) < self.selection_limit:
                                self.select_item_view(view)
                    else:
                        self.select_item_view(view)
                else:
                    self.select_item_view(view)
        else:
            self.deselect_item_view(view)
            if self.selection_mode != 'none':
                # If the deselection makes selection empty, the following call
                # will check allows_empty_selection, and if False, will
                # select the first item. If view happens to be the first item,
                # this will be a reselection, and the user will notice no
                # change, except perhaps a flicker.
                #
                self.check_for_empty_selection()

        if not hold_dispatch:
            self.dispatch('on_selection_change')

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

    def select_item_view(self, view):
        view.select()
        view.is_selected = True
        self.selection.append(view)

        # [TODO] sibling selection for composite items
        #        Needed? Or handled from parent?
        #        (avoid circular, redundant selection)
        #if hasattr(view, 'parent') and hasattr(view.parent, 'children'):
         #siblings = [child for child in view.parent.children if child != view]
         #for sibling in siblings:
             #if hasattr(sibling, 'select'):
                 #sibling.select()

        # child selection
        for child in view.children:
            if hasattr(child, 'select'):
                child.select()

        if self.propagate_selection_to_data:
            data_item = self.get_data_item(view.index)
            self.select_data_item(data_item)

    def select_list(self, view_list, extend=True):
        '''The select call is made for the items in the provided view_list.

        Arguments:

            view_list: the list of item views to become the new selection, or
            to add to the existing selection

            extend: boolean for whether or not to extend the existing list
        '''
        if not extend:
            self.selection = []

        for view in view_list:
            self.handle_selection(view, hold_dispatch=True)

        self.dispatch('on_selection_change')

    def deselect_item_view(self, view):
        view.deselect()
        view.is_selected = False
        self.selection.remove(view)

        # [TODO] sibling deselection for composite items
        #        Needed? Or handled from parent?
        #        (avoid circular, redundant selection)
        #if hasattr(view, 'parent') and hasattr(view.parent, 'children'):
         #siblings = [child for child in view.parent.children if child != view]
         #for sibling in siblings:
             #if hasattr(sibling, 'deselect'):
                 #sibling.deselect()

        # child deselection
        for child in view.children:
            if hasattr(child, 'deselect'):
                child.deselect()

        if self.propagate_selection_to_data:
            item = self.get_data_item(view.index)
            self.deselect_data_item(item)

    def deselect_list(self, l):
        for view in l:
            self.handle_selection(view, hold_dispatch=True)

        self.dispatch('on_selection_change')

    # [TODO] Could easily add select_all() and deselect_all().

    def initialize_selection(self, *args):
        if len(self.selection) > 0:
            self.selection = []
            self.dispatch('on_selection_change')

        self.check_for_empty_selection()

    def check_for_empty_selection(self, *args):
        if not self.allow_empty_selection_rows:
            if len(self.selection) == 0:
                # Select the first item if we have it.
                v = self.get_view(0)
                if v is not None:
                    print 'selecting first data item view', v, v.is_selected
                    self.handle_selection(v)
