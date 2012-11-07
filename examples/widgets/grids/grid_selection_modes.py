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

    def __init__(self, **kwargs):
        kwargs['orientation'] = 'vertical'
        kwargs['size_hint'] = (1.0, 1.0)
        super(MainView, self).__init__(**kwargs)

        spinners_labels = BoxLayout(size_hint_y=None, height=35)

        spinners_labels.add_widget(Label(text='Selection Mode'))
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

    def selection_mode_changed(self, spinner, text):
        self.grid_adapter.selection_mode = text

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
