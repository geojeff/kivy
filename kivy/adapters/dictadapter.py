'''
DictAdapter
===========

.. versionadded:: 1.5

.. warning::

    This code is still experimental, and its API is subject to change in a
    future version.

A :class:`~kivy.adapters.dictadapter.DictAdapter` is an adapter around a
python dictionary of records. It extends the list-like capabilities of the
:class:`~kivy.adapters.listadapter.ListAdapter`.

If you wish to have a bare-bones list adapter, without selection, use the
:class:`~kivy.adapters.simplelistadapter.SimpleListAdapter`.

'''

__all__ = ('DictAdapter', )

from kivy.clock import Clock
from kivy.properties import DictProperty
from kivy.properties import ListProperty
from kivy.properties import ObjectProperty
from kivy.properties import ObservableDict
from kivy.adapters.listadapter import ListAdapter
from kivy.adapters.listadapter import ChangeRecordingObservableList


class ChangeRecordingObservableDict(ObservableDict):
    '''Adds range-observing and other intelligence to ObservableDict, storing
    change_info for use by an observer.
    '''

    def __init__(self, *largs):
        super(ChangeRecordingObservableDict, self).__init__(*largs)

    # TODO: For running test apps, it is ok to have change_info commented out,
    #       but tests will not run, because change_info is not seen as as
    #       property. Conversely, if it is present, test apps will not run,
    #       because it expects an EventDispatcher for the set.
    #
    #           in self.data.change_info,
    #           (the self obj is not an EventDispatcher)
    #
    #change_info = ObjectProperty(None)
    # change_info is a normal python object consisting of the op name and
    # the keys involved:
    #
    #     (data_op, (keys))
    #
    # If the op does not cause a range change, change_info is set to None.
    #
    # Observers of data changes may consult change_info if needed, for
    # example, listview needs to know details for scrolling.
    #
    # DictAdapter itself, the owner of data, is the first observer of data
    # change that must react to delete ops, if the existing selection is
    # affected.
    #

    # ObservableDict __setattr__
    # def __setattr__(self, attr, value):
    #    if attr in ('prop', 'obj'):
    #        super(ObservableDict, self).__setattr__(attr, value)
    #        return
    #    self.__setitem__(attr, value)


    def __setattr__(self, attr, value):
        if attr in ('prop', 'obj'):
            super(ChangeRecordingObservableDict, self).__setattr__(attr, value)
            return
        super(ChangeRecordingObservableDict, self).__setitem__(attr, value)
        if attr != 'change_info':
            self.change_info = ('crod_setattr', (attr, ))

    def __setitem__(self, key, value):
        if isinstance(value, tuple) and key == 'change_info':
            return
        if value is None:
            # ObservableDict will delete the item if value is None, so this is
            # like a delete op.
            self.change_info = ('crod_setitem_delete', (key, ))
        else:
            self.change_info = ('crod_setitem_add', (key, ))
        super(ChangeRecordingObservableDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        self.change_info = ('crod_delitem', (key, ))
        super(ChangeRecordingObservableDict, self).__delitem__(key)

    def clear(self, *largs):
        self.change_info = ('crod_clear', (None, ))
        super(ChangeRecordingObservableDict, self).clear(*largs)

    def remove(self, *largs):
        # remove(x) is same as del s[s.index(x)]
        self.change_info = ('crod_remove', (largs[0], ))
        super(ChangeRecordingObservableDict, self).remove(*largs)

    def pop(self, *largs):
        # This is pop on a specific key. If that key is absent, the second arg
        # is returned. If there is no second arg in that case, a key error is
        # raised. But the key is always largs[0], so store that.
        # s.pop([i]) is same as x = s[i]; del s[i]; return x
        self.change_info = ('crod_pop', (largs[0], ))
        return super(ChangeRecordingObservableDict, self).pop(*largs)

    def popitem(self, *largs):
        # From python docs, "Remove and return an arbitrary (key, value) pair
        # from the dictionary." From other reading, arbitrary here effectively
        # means "random" in the loose sense -- for truely random ops, use the
        # proper random module. Nevertheless, the item is deleted and returned.
        # If the dict is empty, a key error is raised.
        if len(self.keys()) != 0:
            self.change_info = ('crod_popitem', (largs[0], ))
        return super(ChangeRecordingObservableDict, self).popitem(*largs)

    def setdefault(self, *largs):
        present_keys = super(ChangeRecordingObservableDict, self).keys()
        key = largs[0]
        if not key in present_keys:
            self.change_info = ('crod_setdefault', (key, ))
        super(ChangeRecordingObservableDict, self).setdefault(*largs)

    def update(self, *largs):
        present_keys = super(ChangeRecordingObservableDict, self).keys()
        self.change_info = ('crod_update', list(set(largs) - set(present_keys)))
        super(ChangeRecordingObservableDict, self).update(*largs)


class DictAdapter(ListAdapter):
    '''A :class:`~kivy.adapters.dictadapter.DictAdapter` is an adapter around a
    python dictionary of records. It extends the list-like capabilities of
    the :class:`~kivy.adapters.listadapter.ListAdapter`.
    '''

    sorted_keys = ListProperty([])
    '''The sorted_keys list property contains a list of hashable objects (can
    be strings) that will be used directly if no args_converter function is
    provided. If there is an args_converter, the record received from a
    lookup of the data, using keys from sorted_keys, will be passed
    to it for instantiation of list item view class instances.

    :data:`sorted_keys` is a :class:`~kivy.properties.ListProperty` and
    defaults to [].
    '''

    data = DictProperty({}, cls=ChangeRecordingObservableDict)
    '''A dict that indexes records by keys that are equivalent to the keys in
    sorted_keys, or they are a superset of the keys in sorted_keys.

    TODO: Is that last statement about "superset" correct?

    The values can be strings, class instances, dicts, etc.

    :data:`data` is a :class:`~kivy.properties.DictProperty` and defaults
    to None.
    '''

    def __init__(self, **kwargs):
        if 'sorted_keys' in kwargs:
            if type(kwargs['sorted_keys']) not in (tuple, list):
                msg = 'DictAdapter: sorted_keys must be tuple or list'
                raise Exception(msg)
            else:
                # Copy the provided sorted_keys, and maintain it internally.
                # The only function in the API for sorted_keys is to reset it
                # wholesale with a call to reset_sorted_keys().
                self.sorted_keys = list(kwargs.pop('sorted_keys'))
        else:
            self.sorted_keys = sorted(kwargs['data'].keys())

        super(DictAdapter, self).__init__(**kwargs)

        self.bind(sorted_keys=self.initialize_sorted_keys,
                  data=self.crod_data_changed)

    def reset_sorted_keys(self, sorted_keys):
        self.sorted_keys = sorted_keys
        # TODO: call update on dict to match?

    def crod_data_changed(self, *dt):

        # TODO: This is to solve a timing issue when running tests. Remove when
        #       no longer needed.
        if not hasattr(self.data, 'change_info'):
            Clock.schedule_once(lambda dt: self.crod_data_changed(*args))
            return

        print 'DICT ADAPTER crod_data_changed callback'

        data_op, keys = self.data.change_info

        #print self.data.change_info

        if data_op == 'crod_setattr':

            # TODO: If keys[0] is 'prop' or 'obj' the superclass of crod
            # was called. Otherwise, it was the crod. What to do?
            pass

        elif data_op in ['crod_setitem_add',
                         'crod_setdefault',
                         'crod_update']:

            self.sorted_keys.extend(keys)

        elif data_op in ['crod_setitem_delete',
                         'crod_delitem',
                         'crod_clear',
                         'crod_remove',
                         'crod_pop',
                         'crod_popitem']:

            # crod_pop can have second arg as a return dict.

            deleted_indices = [self.sorted_keys.index(k) for k in keys]

            for i in reversed(sorted(deleted_indices)):
                del self.sorted_keys[i]

            start_index = min(deleted_indices)

            # Delete views from cache.
            new_cached_views = {}

            i = 0
            for k, v in self.cached_views.iteritems():
                if not k in deleted_indices:
                    new_cached_views[i] = self.cached_views[k]
                    if k >= start_index:
                        new_cached_views[i].index = i
                    i += 1

            self.cached_views = new_cached_views

            # Handle selection.
            for sel in self.selection:
                if sel.index in deleted_indices:
                    print 'deleting', sel.text
                    del self.selection[self.selection.index(sel)]

            # Do a check_for_empty_selection type step, if data remains.
            if (len(self.data) > 0
                    and not self.selection
                    and not self.allow_empty_selection):
                # Find a good index to select, if the deletion results in
                # no selection, which is common, as the selected item is
                # often the one deleted.
                if start_index < len(self.data):
                    new_sel_index = start_index
                else:
                    new_sel_index = start_index - 1
                v = self.get_view(new_sel_index)
                if v is not None:
                    print 'handling selection for', v.text
                    self.handle_selection(v)

    def bind_triggers_to_view(self, func):
        self.bind(sorted_keys=func)
        self.bind(data=func)

    # self.data is paramount to self.sorted_keys. If sorted_keys is reset to
    # mismatch data, force a reset of sorted_keys to data.keys(). So, in order
    # to do a complete reset of data and sorted_keys, data must be reset
    # first, followed by a reset of sorted_keys, if needed.
    def initialize_sorted_keys(self, *args):
        stale_sorted_keys = False
        for key in self.sorted_keys:
            if not key in self.data:
                stale_sorted_keys = True
                break
        if stale_sorted_keys:
            self.sorted_keys = sorted(self.data.keys())
        self.delete_cache()
        self.initialize_selection()

    # Override ListAdapter.update_for_new_data().
    def update_for_new_data(self, *args):
        self.initialize_sorted_keys()

    # Note: this is not len(self.data).
    def get_count(self):
        return len(self.sorted_keys)

    def get_data_item(self, index):
        if index < 0 or index >= len(self.sorted_keys):
            return None
        return self.data[self.sorted_keys[index]]

    # [TODO] Also make methods for scroll_to_sel_start, scroll_to_sel_end,
    #        scroll_to_sel_middle.

    def trim_left_of_sel(self, *args):
        '''Cut list items with indices in sorted_keys that are less than the
        index of the first selected item, if there is a selection.

        sorted_keys will be updated by update_for_new_data().
        '''
        if len(self.selection) > 0:
            selected_keys = [sel.text for sel in self.selection]
            first_sel_index = self.sorted_keys.index(selected_keys[0])
            desired_keys = self.sorted_keys[first_sel_index:]
            self.data = dict([(key, self.data[key]) for key in desired_keys])

    def trim_right_of_sel(self, *args):
        '''Cut list items with indices in sorted_keys that are greater than
        the index of the last selected item, if there is a selection.

        sorted_keys will be updated by update_for_new_data().
        '''
        if len(self.selection) > 0:
            selected_keys = [sel.text for sel in self.selection]
            last_sel_index = self.sorted_keys.index(selected_keys[-1])
            desired_keys = self.sorted_keys[:last_sel_index + 1]
            self.data = dict([(key, self.data[key]) for key in desired_keys])

    def trim_to_sel(self, *args):
        '''Cut list items with indices in sorted_keys that are les than or
        greater than the index of the last selected item, if there is a
        selection. This preserves intervening list items within the selected
        range.

        sorted_keys will be updated by update_for_new_data().
        '''
        if len(self.selection) > 0:
            selected_keys = [sel.text for sel in self.selection]
            first_sel_index = self.sorted_keys.index(selected_keys[0])
            last_sel_index = self.sorted_keys.index(selected_keys[-1])
            desired_keys = self.sorted_keys[first_sel_index:last_sel_index + 1]
            self.data = dict([(key, self.data[key]) for key in desired_keys])

    def cut_to_sel(self, *args):
        '''Same as trim_to_sel, but intervening list items within the selected
        range are also cut, leaving only list items that are selected.

        sorted_keys will be updated by update_for_new_data().
        '''
        if len(self.selection) > 0:
            selected_keys = [sel.text for sel in self.selection]
            self.data = dict([(key, self.data[key]) for key in selected_keys])
