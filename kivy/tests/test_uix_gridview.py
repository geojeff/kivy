'''
GridView tests
==============
'''

import unittest

from kivy.uix.label import Label
from kivy.adapters.gridadapter import GridAdapter
from kivy.uix.gridview import SelectableGridCellView
from kivy.uix.gridview import GridCell
from kivy.uix.gridview import GridShapeBase
from kivy.uix.gridview import GridRow
from kivy.uix.gridview import HeaderButton
from kivy.uix.gridview import GridView

class GridViewTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_simple_grid_view(self):

        grid_view = GridView(rows=100, cols=100)

        self.assertEqual(type(grid_view.adapter), GridAdapter)
        #self.assertFalse(hasattr(grid_view.adapter, 'selection'))
        self.assertEqual(len(grid_view.adapter.data), 100)

    def test_simple_grid_view_explicit_simple_list_adapter(self):

        args_converter = \
            lambda rec: \
                {'text': rec['text'],
                 'size_hint_y': None,
                 'height': 25,
                 'cell_args': [{'cls': GridCell,
                                'kwargs': {'text': rec[0]['text']}},
                               {'cls': GridCell,
                                'kwargs': {'text': rec[1]['text']}},
                               {'cls': GridCell,
                                'kwargs': {'text': rec[2]['text']}},
                               {'cls': GridCell,
                                'kwargs': {'text': rec[3]['text']}},
                               {'cls': GridCell,
                                'kwargs': {'text': rec[4]['text']}},
                               {'cls': GridCell,
                                'kwargs': {'text': rec[5]['text']}},
                               {'cls': GridCell,
                                'kwargs': {'text': rec[6]['text']}},
                               {'cls': GridCell,
                                'kwargs': {'text': rec[7]['text']}},
                               {'cls': GridCell,
                                'kwargs': {'text': rec[8]['text']}},
                               {'cls': GridCell,
                                'kwargs': {'text': rec[9]['text']}}]}

        row_keys = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        col_keys = [index for index in xrange(10)]
        data = {}
        for row_key in row_keys:
            data[row_key] = {'text': str(row_key)}
            for col_key in col_keys:
                data[row_key][col_key] = \
                        {'text': "{0}{1}".format(row_key, col_key)}

        grid_adapter = GridAdapter(row_keys=row_keys,
                                   col_keys=col_keys,
                                   data=data,
                                   args_converter=args_converter,
                                   selection_mode='column-single',
                                   allow_empty_selection=True,
                                   cls=GridRow)

        # Use the adapter in our GridView:
        grid_view = GridView(adapter=grid_adapter)

        self.assertEqual(type(grid_view.adapter), GridAdapter)
        #self.assertFalse(hasattr(grid_view.adapter, 'selection'))
        self.assertEqual(len(grid_view.adapter.data), 26)
        self.assertEqual(type(grid_view.adapter.get_view(0)), GridRow)
