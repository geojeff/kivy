from kivy.adapters.gridadapter import GridAdapter
from kivy.uix.gridview import GridCell
from kivy.uix.gridview import GridRow
from kivy.uix.gridview import GridView
from kivy.uix.gridlayout import GridLayout

integers_dict = \
        { str(i): {'text': str(i), 'is_selected': False} for i in xrange(100)}


class MainView(GridLayout):
    '''Uses :class:`GridRow` for grid row views comprised by two
    :class:`GridCell`s. Illustrates how to construct an args_converter used
    with :class:`GridRow`.
    '''

    def __init__(self, **kwargs):
        kwargs['cols'] = 2
        kwargs['size_hint'] = (1.0, 1.0)
        super(MainView, self).__init__(**kwargs)

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

        grid_adapter = GridAdapter(row_keys=row_keys,
                                   col_keys=col_keys,
                                   data=data,
                                   args_converter=args_converter,
                                   selection_mode='single',
                                   allow_empty_selection=False,
                                   cls=GridRow)

        # Use the adapter in our GridView:
        grid_view = GridView(adapter=grid_adapter)

        self.add_widget(grid_view)


if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(MainView(width=800))
