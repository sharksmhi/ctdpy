# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 13:35:11 2018

@author: a002028
"""


class StyleSheet:
    """Uses style object from pandas DataFrame and CSS formats to style an excel sheet.

    For HTML-colors: https://html-color-codes.info/?
    CSS styles: https://developer.mozilla.org/en-US/docs/Web/CSS/

    To be extended.
    """

    def __init__(self):
        """Set default style settings."""
        self._set_default()

    def _set_default(self, cell_color='#5FB404', column_color='#00B0F0',
                     row_color='#92d050', odd_row_color='#D8D8D8',
                     fontweight='bold', text_alignment='center',
                     border_style=None):
        """Set default setings."""
        if not border_style:
            border_style = {'border_left': 'solid', 'border_right': 'solid',
                            'border_top': 'solid', 'border_bottom': 'solid'}
        self.set_cell_color(cell_color)
        self.set_column_color(column_color)
        self.set_row_color(row_color)
        self.set_odd_row_color(odd_row_color)

        self.set_fontweight(fontweight)
        self.set_text_alignment(text_alignment)
        self.set_border_style(**border_style)

    def set_cell_color(self, setting):
        """Set cell_color."""
        self.cell_color = setting

    def set_column_color(self, setting):
        """Set column_color."""
        self.column_color = setting

    def set_row_color(self, setting):
        """Set row_color."""
        self.row_color = setting

    def set_odd_row_color(self, setting):
        """Set odd_row_color."""
        self.odd_row_color = setting

    def set_fontweight(self, setting):
        """Set fontweight.

        Args:
            setting (str): eg. normal|bold|bolder|lighter|100|200|
        """
        self.fontweight = setting

    def set_text_alignment(self, setting):
        """Set text_alignment.

        Args:
            setting (str): eg. left|right|center|justify|initial|inherit
        """
        self.text_alignment = setting

    def set_border_style(self, **setting):
        """Set values to border_style attributes.

        Args:
            setting (dict): with info such as:
                            none|hidden|dotted|dashed|solid|double|groove|ridge|inset|outset|initial|inherit
        """
        for key, item in setting.items():
            setattr(self, key, item)

    def set_properties(self):
        """Dummie method."""
        raise NotImplementedError

    def get_stylesheet(self, s):
        """Dummie method."""
        raise NotImplementedError

    def highlight_cells(self):
        """Return list with CSS background-color: (str, hex color)."""
        return ['background-color: ' + self.cell_color]

    @staticmethod
    def highlight_column(style_object, color='#00B0F0'):
        """Highlight columns."""
        return ['background-color: ' + color if v else '' for v in style_object]

    @staticmethod
    def highlight_row(style_object, color='#92d050'):
        """Highlight rows."""
        return ['background-color: ' + color if v else '' for v in style_object]

    def highlight_odd_rows(self, style_object):
        """Highlight odd rows (1,3,5,7,9)."""
        return ['background-color: ' + self.odd_row_color if self._is_odd(i) else '' for i, v in enumerate(style_object)]

    def add_fontweight(self, style_object):
        """Set fontweight to style object."""
        return ['font-weight: ' + self.fontweight if v else '' for v in style_object]

    def alignment(self, style_object):
        """Set text alignment."""
        return ['text-align: ' + self.text_alignment if v else '' for v in style_object]

    @staticmethod
    def cell_border_width(style_object, side='bottom', width='medium'):
        """Get cell_border_width."""
        return ['border-' + side + '-width:' + width if v else '' for v in style_object]

    @staticmethod
    def cell_border(style_object, side='bottom', style='solid'):
        """Get cell_border."""
        return ['border-' + side + '-style:' + style if v else '' for v in style_object]

    @staticmethod
    def column_width(style_object, width='auto'):
        """Get column_width."""
        return ['table-layout:' + width if v else '' for v in style_object]

    def bold_cell_lines(self, style_object):
        """Get style object with adjusted border style."""
        return style_object.set_properties(**{'border-left-style': self.border_left,
                                              'border-right-style': self.border_right,
                                              'border-top-style': self.border_top,
                                              'border-bottom-style': self.border_bottom})

    @staticmethod
    def _is_odd(num):
        """Check if num is an odd number"""
        return num & 0x1
