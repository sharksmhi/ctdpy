# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 13:35:11 2018

@author: a002028
"""


class StyleSheet:
    """
    Uses style object from pandas DataFrame and CSS formats to style an excel
    sheet..
    To be extended..    
    
    For HTML-colors: https://html-color-codes.info/?
    CSS styles: https://developer.mozilla.org/en-US/docs/Web/CSS/
    """
    def __init__(self):
        
        self._set_default()

    def _set_default(self, cell_color='#5FB404', column_color='#00B0F0',
                     row_color='#92d050', odd_row_color='#D8D8D8',
                     fontweight='bold', text_alignment='center',
                     border_style=None):
        """
        :param cell_color:
        :param column_color:
        :param row_color:
        :param odd_row_color:
        :param fontweight:
        :param text_alignment:
        :param border_style:
        :return:
        """
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
        """
        :param setting: str, Hex color
        :return: str, Hex color
        """
        self.cell_color = setting

    def set_column_color(self, setting):
        """
        :param setting: str, Hex color
        :return: str, Hex color
        """
        self.column_color = setting
        
    def set_row_color(self, setting):
        """
        :param setting: str, Hex color
        :return: str, Hex color
        """
        self.row_color = setting
        
    def set_odd_row_color(self, setting):
        """
        :param setting: str, Hex color
        :return: str, Hex color
        """
        self.odd_row_color = setting
        
    def set_fontweight(self, setting):
        """
        :param setting: str (e.g. normal|bold|bolder|lighter|100|200| etc..)
        :return: str
        """
        self.fontweight = setting
        
    def set_text_alignment(self, setting):
        """
        :param setting: str (e.g. left|right|center|justify|initial|inherit)
        :return:
        """
        self.text_alignment = setting
        
    def set_border_style(self, **setting):
        """
        :param setting: str (e.g. none|hidden|dotted|dashed|solid|double|groove|ridge|inset|outset|initial|inherit)
        :return:
        """
        for key, item in setting.items():
            setattr(self, key, item)
        
    def set_properties(self):
        """
        :return:
        """
        raise NotImplementedError
    
    def get_stylesheet(self, s):
        """
        :param s:
        :return:
        """
        raise NotImplementedError
        
    def highlight_cells(self):
        """
        :return: list with CSS background-color: (str, Hex color)
        """
        return ['background-color: '+self.cell_color]

    @staticmethod
    def highlight_column(style_object, color='#00B0F0'):
        """
        Highlight columns
        :param style_object:
        :param color: str, Hex color
        :return:
        """
        return ['background-color: '+color if v else '' for v in style_object]

    @staticmethod
    def highlight_row(style_object, color='#92d050'):
        """
        Highlight rows
        :param style_object:
        :param color: str, Hex color
        :return:
        """
        return ['background-color: '+color if v else '' for v in style_object]
        
    def highlight_odd_rows(self, style_object):
        """
        Highlight odd rows (1,3,5,7,9)
        :param style_object:
        :return:
        """
        return ['background-color: '+self.odd_row_color if self._is_odd(i) else '' for i, v in enumerate(style_object)]
    
    def add_fontweight(self, style_object):
        """
        Set fontweight to style object
        :param style_object:
        :return:
        """
        return ['font-weight: '+self.fontweight if v else '' for v in style_object]
    
    def alignment(self, style_object):
        """

        :param style_object:
        :return:
        """
        return ['text-align: '+self.text_alignment if v else '' for v in style_object]

    @staticmethod
    def cell_border_width(style_object, side='bottom', width='medium'):
        """

        :param style_object: style_object
        :param side: str
        :param width: str
        :return:
        """
        return ['border-'+side+'-width:'+width if v else '' for v in style_object]

    @staticmethod
    def cell_border(style_object, side='bottom', style='solid'):
        """

        :param style_object:
        :param side: str
        :param style: str
        :return:
        """
        return ['border-'+side+'-style:'+style if v else '' for v in style_object]

    @staticmethod
    def column_width(style_object, width='auto'):
        """

        :param style_object:
        :param width: str
        :return:
        """
        return ['table-layout:'+width if v else '' for v in style_object]

    def bold_cell_lines(self, style_object):
        """

        :param style_object:
        :return:
        """
        return style_object.set_properties(**{'border-left-style': self.border_left,
                                              'border-right-style': self.border_right,
                                              'border-top-style': self.border_top,
                                              'border-bottom-style': self.border_bottom})

    @staticmethod
    def _is_odd(num):
        """
        Check if num is an odd number
        :param num: int
        :return: False or True
        """
        return num & 0x1


# class WithStyle(StyleSheet):
#     """
#
#     """
#     def __init__(self):
