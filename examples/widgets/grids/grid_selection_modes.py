from functools import partial

from kivy.adapters.gridadapter import GridAdapter
from kivy.uix.gridview import GridCell
from kivy.uix.gridview import GridRow
from kivy.uix.gridview import GridView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.properties import StringProperty, DictProperty

integers_dict = \
        { str(i): {'text': str(i), 'is_selected': False} for i in xrange(100)}


class MainView(BoxLayout):
    '''Uses :class:`GridRow` for grid row views comprised by two
    :class:`GridCell`s. Illustrates how to construct an args_converter used
    with :class:`GridRow`.
    '''

    selection_op = StringProperty('normal')

    shapes = DictProperty({})
    '''Keys are the origin cells; values are the shapes.
    '''

    def __init__(self, **kwargs):
        kwargs['orientation'] = 'vertical'
        kwargs['size_hint'] = (1.0, 1.0)
        super(MainView, self).__init__(**kwargs)

        spinners_labels = BoxLayout(size_hint_y=None, height=35)

        spinners_labels.add_widget(Label(text='Selection Mode'))
        spinners_labels.add_widget(Label(text='Selection Op'))
        spinners_labels.add_widget(Label(text='Allow Empty Selection'))
        spinners_labels.add_widget(Label(text='Data'))

        spinners_toolbar = BoxLayout(size_hint_y=None, height=35)

        selection_modes_spinner = Spinner(
                text='row-single',
                values=('row-single',
                        'row-multiple',
                        'column-single',
                        'column-multiple',
                        'cell-single',
                        'cell-multiple',
                        'none'))
                #size_hint=(None, None), size=(100, 44),
                #pos_hint={'center_x': .5, 'center_y': .5})

        selection_modes_spinner.bind(text=self.selection_mode_changed)

        spinners_toolbar.add_widget(selection_modes_spinner)

        selection_ops_spinner = Spinner(
                text='normal',
                values=('4-block',
                        '16-block',
                        'diagonal',
                        'nw-se-diagonal',
                        '10-nw-se-diagonal',
                        'ne-sw-diagonal',
                        '10-ne-sw-diagonal',
                        '16-border',
                        'checkerboard',
                        '16-checkerboard'))
                #size_hint=(None, None), size=(100, 44),
                #pos_hint={'center_x': .5, 'center_y': .5})

        selection_ops_spinner.bind(text=self.selection_op_changed)

        spinners_toolbar.add_widget(selection_ops_spinner)

        allow_empty_selection_spinner = Spinner(
                text='True',
                values=('True',
                        'False'))
                #size_hint=(None, None), size=(100, 44),
                #pos_hint={'center_x': .5, 'center_y': .5})

        allow_empty_selection_spinner.bind(text=self.allow_empty_selection_changed)

        spinners_toolbar.add_widget(allow_empty_selection_spinner)

        data_spinner = Spinner(
                text='Alphabet x 10',
                values=('Alphabet x 10',
                        'Alphabet x Alphabet',
                        '100 x 10',
                        '100 x 100',
                        '1000 x 100'))
                #size_hint=(None, None), size=(100, 44),
                #pos_hint={'center_x': .5, 'center_y': .5})

        data_spinner.bind(text=self.data_changed)

        spinners_toolbar.add_widget(data_spinner)

        args_converter = \
            lambda rec: \
                {'text': rec['text'],
                 'size_hint_y': None,
                 'height': 25,
                 'cls_dicts': [{'cls': GridCell,
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

        self.grid_adapter = GridAdapter(row_keys=row_keys,
                                        col_keys=col_keys,
                                        data=data,
                                        args_converter=args_converter,
                                        selection_mode='row-single',
                                        allow_empty_selection=True,
                                        cls=GridRow)

        # Use the adapter in our GridView:
        self.grid_view = GridView(adapter=self.grid_adapter,
                                  size_hint_y=1.0)

        self.add_widget(spinners_labels)
        self.add_widget(spinners_toolbar)
        self.add_widget(self.grid_view)

        self.grid_adapter.bind(on_selection_change=self.selection_changed)

    def existing_shape(self, specific_shape, origin_grid_cell):
        # selection search:
        #for sel in self.grid_adapter.selection:
        #    if hasattr(sel, 'specific-shape'):
        #        if (sel.specific_shape == '4-block' 
        #                and sel.origin_cell_block == origin_cell_block):
        #            return True
        if origin_grid_cell in self.shapes:
            if self.shapes[origin_grid_cell].specific_shape == specific_shape:
                return self.shapes[origin_grid_cell]
        return None

    def selection_changed(self, grid_adapter, objects_handled, *args):
        if (self.grid_adapter.selection_mode == 'cell-multiple' 
                and not self.selection_op == 'normal'
                and self.grid_adapter.has_selection()):

            selection = self.grid_adapter.selection

            # Look for a single click/touch on a cell, to add a shape, which
            # in this context triggers a shape action.
            origin_grid_cell = None
            if len(objects_handled) == 1:
                origin_grid_cell = objects_handled[0]

            if origin_grid_cell and self.selection_op == '4-block':
                existing_shape = self.existing_shape('4-block', origin_grid_cell)
                if existing_shape:
                    self.grid_adapter.remove_shape(origin_grid_cell, existing_shape)
                    del self.shapes[origin_grid_cell]
                else:
                    row_key = origin_grid_cell.row_key
                    col_key = origin_grid_cell.col_key

                    row_keys = self.grid_adapter.row_keys
                    col_keys = self.grid_adapter.col_keys

                    rows = len(row_keys)
                    cols = len(col_keys)

                    row_index = row_keys.index(row_key)
                    col_index = col_keys.index(col_key)

                    cells = []
                    cells.append((row_key, col_key))

                    if row_index < rows - 1 and col_index < cols - 1:
                        upper_right = (row_key,
                                       col_keys[col_index + 1])
                        lower_right = (row_keys[row_index + 1],
                                       col_keys[col_index + 1])
                        lower_left = (row_keys[row_index + 1],
                                      col_key)
                        cells.append(upper_right)
                        cells.append(lower_right)
                        cells.append(lower_left)

                        shape = self.grid_view.shape(origin_grid_cell,
                                                     'block',
                                                     '4-block',
                                                     cells)

                        self.shapes[origin_grid_cell] = shape

                        self.grid_adapter.add_shape(shape)
            elif self.selection_op == '16-block':
                print '16-block'
            elif self.selection_op == 'diagonal':
                print 'diagonal'
            elif self.selection_op == 'nw-se-diagonal':
                print 'nw-se-diagonal'
            elif self.selection_op == '10-nw-se-diagonal':
                print '10-nw-se-diagonal'
            elif self.selection_op == 'ne-sw-diagonal':
                print 'ne-sw-diagonal'
            elif self.selection_op == '10-ne-sw-diagonal':
                print '10-ne-sw-diagonal'
            elif self.selection_op == '16-border':
                print '16-border'
            elif self.selection_op == 'checkerboard':
                print 'checkerboard'
            elif self.selection_op == '16-checkerboard':
                print '16-checkerboard'

    def selection_mode_changed(self, spinner, text):
        self.grid_adapter.selection_mode = text

    def selection_op_changed(self, spinner, text):
        self.selection_op = text

    def allow_empty_selection_changed(self, spinner, text):
        self.grid_adapter.allow_empty_selection = \
                True if text.endswith('True') else False

    def args_converter(self, col_keys, rec):
        return {
            'text': rec['text'],
            'size_hint_y': None,
            'height': 25,
            'cls_dicts': [{'cls': GridCell,
                           'kwargs': {'text': rec[col_key]['text']}}
                          for col_key in col_keys]}

    def data_dict(self, row_keys, col_keys):
        data = {}
        for row_key in row_keys:
            data[row_key] = {'text': str(row_key)}
            for col_key in col_keys:
                data[row_key][col_key] = \
                    {'text': "{0}{1}".format(row_key, col_key)}
        return data

    def data_changed(self, spinner, text):
        if text == 'Alphabet x 10':
            row_keys = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            col_keys = [index for index in xrange(10)]
        elif text == 'Alphabet x Alphabet':
            row_keys = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            col_keys = row_keys[:]
        elif text == '100 x 10':
            row_keys = [index for index in xrange(100)]
            col_keys = [index for index in xrange(10)]
        elif text == '100 x 100':
            row_keys = [index for index in xrange(100)]
            col_keys = [index for index in xrange(100)]
        elif text == '1000 x 100':
            row_keys = [index for index in xrange(1000)]
            col_keys = [index for index in xrange(100)]

        self.grid_adapter.args_converter = \
                partial(self.args_converter, col_keys)

        self.grid_adapter.data = self.data_dict(row_keys, col_keys)


if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(MainView(width=800))
