"""
Created on 2021-03-12 14:04
@author: johannes
"""
import sys
sys.path.append('C:\\Utveckling\\ctdvis')
from ctdvis.session import Session
from ctdvis.sources.data import setup_data_source


if __name__ == "__main__":
    data_dir = 'C:/Arbetsmapp/datasets/Profile/2019/SHARK_Profile_2019_SMHI/processed_data'
    # data_dir = 'C:\\Arbetsmapp\\datasets\\Profile\\2018\\SHARK_Profile_2018_BAS_SMHI\\processed_data'

    """ Filters are advised to be implemented if the datasource is big, (~ >3 months of SMHI-EXP-data) """
    # filters = None
    filters = dict(
        # month_list=[1, 2, 3],
        month_list=[5],
        # month_list=[7, 8, 9],
        # month_list=[10, 11, 12],
        # ship_list=['77SE', '34AR']
        # serno_min=311,
        # serno_max=355,
    )

    s = Session(visualize_setting='smhi_vis', data_directory=data_dir, filters=filters)
    s.setup_datahandler()

    import numpy as np

    ds = setup_data_source(
        s.dh.df[s.settings.selected_keys],
        pmap=s.settings.plot_parameters_mapping,
        key_list=np.unique(s.dh.df['KEY']),
        parameter_list=s.settings.data_parameters_with_units +
                       s.settings.q_colors +
                       s.settings.q_parameters +
                       s.settings.q0_parameters
    )
