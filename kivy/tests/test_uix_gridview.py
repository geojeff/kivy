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
        self.assertEqual(len(grid_view.adapter.selection), 0)
        self.assertEqual(len(grid_view.adapter.data), 100)

    def test_simple_grid_view_explicit_simple_list_adapter(self):

        args_converter = \
            lambda row_index, rec: \
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
                                   allow_empty_selection=False,
                                   cls=GridRow)

        # Use the adapter in our GridView:
        grid_view = GridView(adapter=grid_adapter)

        self.assertEqual(type(grid_view.adapter), GridAdapter)
        self.assertEqual(len(grid_view.adapter.selection), 26)
        self.assertEqual(len(grid_view.adapter.data), 26)
        self.assertEqual(type(grid_view.adapter.get_view(0)), GridRow)

        # Select column with col_key 5.
        grid_cell_C_5 = grid_view.adapter.grid_cell_view('C', 5)
        grid_view.adapter.handle_selection(grid_cell_C_5)
        self.assertEqual(len(grid_view.adapter.selection), 26)
        self.assertEqual(
                [5 for i in xrange(26)],
                [cell.col_key for cell in grid_view.adapter.selection])

        # Unselecting column with col_key 5 should result in auto-selection
        # of the first column, because allow_empty_selection is False.
        grid_view.adapter.handle_selection(grid_cell_C_5)
        self.assertEqual(len(grid_view.adapter.selection), 26)
        self.assertEqual(
                [0 for i in xrange(26)],
                [cell.col_key for cell in grid_view.adapter.selection])

        # Change selection mode to row-single and select row W.
        # The selected column, the first column, should be unselected,
        # and row W selected.
        grid_view.adapter.selection_mode = 'row-single'
        self.assertEqual(grid_view.adapter.selection_mode, 'row-single')
        grid_cell_W_1 = grid_view.adapter.grid_cell_view('W', 1)
        grid_view.adapter.handle_selection(grid_cell_W_1)
        self.assertEqual(len(grid_view.adapter.selection), 10)
