from functools import partial

from kivy.adapters.gridadapter import GridAdapter
from kivy.uix.gridview import GridCell
from kivy.uix.gridview import GridRow
from kivy.uix.gridview import GridView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.gridview import GridShapeBase
from kivy.properties import StringProperty, DictProperty, OptionProperty

integers_dict = \
        { str(i): {'text': str(i), 'is_selected': False} for i in xrange(100)}


class GridColumn(GridShapeBase):
    ''':class:`~kivy.uix.gridview.GridColumn` is a secondary container of grid
    cells in a grid: the grid cells are stored across multiple grid rows.
    '''

    def __init__(self, **kwargs):
        kwargs['shape'] = 'column'
        super(GridColumn, self).__init__(**kwargs)


class GridBlock(GridShapeBase):
    ''':class:`~kivy.uix.gridview.GridBlock` is a secondary container of grid
    cells in a grid: the grid cells are stored across multiple grid rows.

    A block is a solid rectangular set of grid cells.
    '''

    def __init__(self, **kwargs):
        kwargs['shape'] = 'block'

        # [TODO]
        # Find the min and max, for rows and columns, for the cells, and add
        # cells if needed. A block can be specified with just two cells in two
        # opposite corners of the block.

        super(GridBlock, self).__init__(**kwargs)


class GridDiagonal(GridShapeBase):
    ''':class:`~kivy.uix.gridview.GridDiagonal` is a secondary container of
    grid cells in a grid: the grid cells are stored across multiple grid rows.

    A diagonal may be a diagonal segment, or it may extend corner to corner.
    '''

    def __init__(self, **kwargs):
        kwargs['shape'] = 'diagonal'

        # [TODO]
        # Find the end points, for rows and columns, for the cells and add
        # cells if needed. A diagonal can be specified with just two cells at
        # the ends.

        super(GridDiagonal, self).__init__(**kwargs)


class GridCheckerboard(GridShapeBase):
    ''':class:`~kivy.uix.gridview.GridCheckerboard` is a secondary container of
    grid cells in a grid: the grid cells are stored across multiple grid rows.

    A checkerboard may cover the whole grid or only a rectangular block within
    it.
    '''

    def __init__(self, **kwargs):
        kwargs['shape'] = 'checkerboard'

        # [TODO]
        # Find the min and max, for rows and columns, for the cells, and add or
        # remove cells if needed. A checkerboard can be specified with just two
        # cells in two opposite corners of the checkerboard.

        super(GridCheckerboard, self).__init__(**kwargs)


class GridBorder(GridShapeBase):
    ''':class:`~kivy.uix.gridview.GridBorderBox` is a secondary container of
    grid cells in a grid: the grid cells are stored across multiple grid rows.

    A border box is a set of cells making a rectangular border one cell wide.
    '''

    def __init__(self, **kwargs):
        kwargs['shape'] = 'border'

        # [TODO]
        # Find the min and max, for rows and columns, for the cells, and add or
        # remove cells if needed.
        #
        # Should there be a width property, or top, bottom, left, right
        # properties?

        super(GridBorder, self).__init__(**kwargs)


class GridCellSet(GridShapeBase):
    ''':class:`~kivy.uix.gridview.GridCellSet` is a secondary container of
    grid cells in a grid: the grid cells are stored across multiple grid rows.

    A grid cell set is a patchwork, or otherwise arbitrary set of cells.
    '''

    def __init__(self, **kwargs):
        kwargs['shape'] = 'set'

        # [TODO]
        # A cell set is a patchwork, or otherwise arbitrary set of cells. No
        # checks needed?

        super(GridCellSet, self).__init__(**kwargs)


class GridShape(GridShapeBase):
    ''':class:`~kivy.uix.gridview.GridShape` is a secondary container of
    grid cells in a grid: the grid cells are stored across multiple grid rows.

    A grid shape is a solid area of cells making a shape.
    '''

    def __init__(self, **kwargs):
        kwargs['shape'] = 'shape'

        # [TODO]
        # No checks needed?

        super(GridShape, self).__init__(**kwargs)


class GridPath(GridShapeBase):
    ''':class:`~kivy.uix.gridview.GridPath` is a secondary container of
    grid cells in a grid: the grid cells are stored across multiple grid rows.

    A grid cell path is a set of cells that would be painted for a vector path.
    '''

    def __init__(self, **kwargs):
        kwargs['shape'] = 'path'

        # [TODO]
        # Input could be a path? Do the cell "painting" selection here?

        super(GridPath, self).__init__(**kwargs)


class MainView(BoxLayout):
    '''Uses :class:`GridRow` for grid row views comprised by two
    :class:`GridCell`s. Illustrates how to construct an args_converter used
    with :class:`GridRow`.
    '''

    shape_op = OptionProperty('4-block', options=('none',
                                                 '4-block',
                                                 '16-block',
                                                 'diagonal',
                                                 'nw-se-diagonal',
                                                 '10-nw-se-diagonal',
                                                 'ne-sw-diagonal',
                                                 '10-ne-sw-diagonal',
                                                 '16-border',
                                                 'checkerboard',
                                                 '16-checkerboard'))
    '''The shape_op is the shape drawing mode, if active. In order for a shape
    op to be in effect, the selection mode must be set to cell-multiple.

    :data:`shape_op` is an :class:`~kivy.properties.OptionProperty`,
    default to '4-block'.
    '''

    shape_op_args = DictProperty({})
    '''The shape_op_args property contains optional arguments to the active
    shape_op.

    :data:`shape_op_args` is an :class:`~kivy.properties.DictProperty`,
    default to {}.
    '''

    shapes = DictProperty({})
    '''The shapes dict has keys that are the origin cells, and values that are
    the shapes. Origin cells are the ones clicked or touched to create the
    shapes.

    :data:`shapes` is an :class:`~kivy.properties.DictProperty`,
    default to {}.
    '''

    def __init__(self, **kwargs):
        kwargs['orientation'] = 'vertical'
        kwargs['size_hint'] = (1.0, 1.0)
        super(MainView, self).__init__(**kwargs)

        spinners_labels = BoxLayout(size_hint_y=None, height=35)

        spinners_labels.add_widget(Label(text='Selection Mode'))
        spinners_labels.add_widget(Label(text='Shape Op'))
        spinners_labels.add_widget(Label(text='Allow Empty Selection'))
        spinners_labels.add_widget(Label(text='Data'))

        spinners_toolbar = BoxLayout(size_hint_y=None, height=35)

        selection_modes_spinner = Spinner(
                text='cell-multiple',
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

        shape_ops_spinner = Spinner(
                text='4-block',
                values=('none',
                        '4-block',
                        '16-block',
                        'nw-se-diagonal',
                        '10-nw-se-diagonal',
                        'ne-sw-diagonal',
                        '10-ne-sw-diagonal',
                        '16-border',
                        '16-checkerboard'))
                #size_hint=(None, None), size=(100, 44),
                #pos_hint={'center_x': .5, 'center_y': .5})

        shape_ops_spinner.bind(text=self.shape_op_changed)

        spinners_toolbar.add_widget(shape_ops_spinner)

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
                                        selection_mode='cell-multiple',
                                        allow_empty_selection=True,
                                        cls=GridRow)

        # Use the adapter in our GridView:
        self.grid_view = GridView(adapter=self.grid_adapter,
                                  size_hint_y=1.0)

        self.add_widget(spinners_labels)
        self.add_widget(spinners_toolbar)
        self.add_widget(self.grid_view)

        self.grid_adapter.bind(on_selection_change=self.selection_changed)

    def selection_mode_changed(self, spinner, text):
        self.grid_adapter.selection_mode = text

    def shape_op_changed(self, spinner, text):
        op = 'none'
        op_args = text.split('-')
        args_dict = {}

        if text.endswith('block'):
            args_dict['size'] = int(op_args[0])
        elif text.endswith('diagonal'):
            if len(op_args) == 3:
                args_dict['length'] = int(op_args[0])
                args_dict['orientation'] = \
                        "{0}-{1}".format(op_args[1], op_args[2])
            else:
                args_dict['orientation'] = \
                        "{0}-{1}".format(op_args[0], op_args[1])
        elif text.endswith('border'):
            args_dict['size'] = int(op_args[0])
            args_dict['width'] = int(op_args[1])
        elif text.endswith('checkerboard'):
            args_dict['size'] = int(op_args[0])

        #self.shape_op = op_args[-1]
        self.shape_op = text
        self.shape_op_args = args_dict

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

    def shape(self, origin_grid_cell, shape, specific_shape, cell_keys):
        if shape == 'row':
            print 'GridRow shape not yet implemented (as a shape).'
        elif shape == 'column':
            print 'GridColumn shape not yet implemented.'
        elif shape == 'block':
            return GridBlock(origin_grid_cell=origin_grid_cell,
                             specific_shape=specific_shape,
                             adapter=self.grid_adapter,
                             cell_keys=cell_keys)
        elif shape == 'diagonal':
            print 'GridDiagonal shape not yet implemented.'
        elif shape == 'checkerboard':
            print 'GridCheckerboard shape not yet implemented.'
        elif shape == 'border':
            print 'GridBorder shape not yet implemented.'
        elif shape == 'path':
            print 'GridPath shape not yet implemented.'
        elif shape == 'shape':
            print 'GridShape shape not yet implemented.'
        elif shape == 'set':
            print 'GridCellSet shape not yet implemented.'

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
                and not self.shape_op == 'none'
                and self.grid_adapter.has_selection()):

            selection = self.grid_adapter.selection

            # Look for a single click/touch on a cell, to add a shape, which
            # in this context triggers a shape action.
            origin_grid_cell = None
            if len(objects_handled) == 1:
                origin_grid_cell = objects_handled[0]

            if origin_grid_cell and self.shape_op == '4-block':
                existing_shape = self.existing_shape('4-block', origin_grid_cell)
                if existing_shape:
                    self.remove_shape(origin_grid_cell, existing_shape)
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

                        shape = self.shape(origin_grid_cell,
                                                     'block',
                                                     '4-block',
                                                     cells)

                        self.shapes[origin_grid_cell] = shape

                        self.add_shape(shape)
            elif self.shape_op == '16-block':
                print '16-block'
            elif self.shape_op == 'diagonal':
                print 'diagonal'
            elif self.shape_op == 'nw-se-diagonal':
                print 'nw-se-diagonal'
            elif self.shape_op == '10-nw-se-diagonal':
                print '10-nw-se-diagonal'
            elif self.shape_op == 'ne-sw-diagonal':
                print 'ne-sw-diagonal'
            elif self.shape_op == '10-ne-sw-diagonal':
                print '10-ne-sw-diagonal'
            elif self.shape_op == '16-border':
                print '16-border'
            elif self.shape_op == 'checkerboard':
                print 'checkerboard'
            elif self.shape_op == '16-checkerboard':
                print '16-checkerboard'

    def add_shape(self, shape):
        # The selection machinery works on the basis of mode, and on whether or
        # not the clicked or touched cell, the one given to handle_selection(),
        # is presently selected or not. On this basis, handle_selection()
        # decides whether the mode is select or deselect, then calls
        # do_selection_op(). So, since the call to add_shape() comes after the
        # clicked or touched cell has already been selected, we must remove it
        # from the shape cells to be selected here.
        view_list = [cell for cell in shape.cells() if not cell.is_selected]

        self.grid_adapter.select_list(view_list, extend=True)

        # We do not add the shape itself to self.selection, only its cells.
        # Management of shapes is considered the responsibility of the system
        # using this adapter.

    def remove_shape(self, origin_grid_cell, shape):
        view_list = [cell for cell in shape.cells() if cell.is_selected]

        self.grid_adapter.deselect_list(view_list)


if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(MainView(width=800))
