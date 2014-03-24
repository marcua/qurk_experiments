import django_includes

from qurkexp.estimation.models import *

run_defs = {
    'complete_test_vars_change10': { # and change1,...
        'dataset': 'shape_blue_.1',
        'vals_to_estimate': ["blue", "green"],
        'num_batches': 5,
        'batch_size': 10,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'complete_test_gtav_vars_change6': { # and change1,...
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1,
        'batch_size': 100,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'complete_test_wgat_vars_change6': { # and change1,...
        'dataset': 'wgat_normal',
        'vals_to_estimate': ["IS", "ME", "QF"],
        'num_batches': 2,
        'batch_size': 100,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'complete_test_gtav_batch_vars_change7': { # and change1,...
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 5,
        'batch_size': 3,
        'display_style': 'batch',
        'assignments': 2,
        'price': 0.01
    },
    'shape_blue_.1_test10': { # and test1,...
        'dataset': 'shape_blue_.1',
        'vals_to_estimate': ["blue"],
        'num_batches': 5,
        'batch_size': 10,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },        
    'shape_bluered_test1': { # and test1,...
        'dataset': 'shape_blue_.1',
        'vals_to_estimate': ["blue", "red"],
        'num_batches': 20,
        'batch_size': 10,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'shape_bluered_.1_200_10_real1': { # REAL
        'dataset': 'shape_blue_.1',
        'vals_to_estimate': ["blue", "red"],
        'num_batches': 200,
        'batch_size': 10,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'shape_bluered_.1_200_100_real1': { # REAL
        'dataset': 'shape_blue_.1',
        'vals_to_estimate': ["blue", "red"],
        'num_batches': 200,
        'batch_size': 100,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'shape_bluered_.1_200_50_real1': { # REAL notdone
        'dataset': 'shape_blue_.1',
        'vals_to_estimate': ["blue", "red"],
        'num_batches': 200,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'shape_bluered_.5_200_50_real1': { # REAL notdone
        'dataset': 'shape_blue_.5',
        'vals_to_estimate': ["blue", "red"],
        'num_batches': 200,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'shape_bluered_.5_200_100_real1': { # REAL
        'dataset': 'shape_blue_.5',
        'vals_to_estimate': ["blue", "red"],
        'num_batches': 200,
        'batch_size': 100,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'shape_bluered_.5_200_10_real1': { # REAL notdone
        'dataset': 'shape_blue_.5',
        'vals_to_estimate': ["blue", "red"],
        'num_batches': 200,
        'batch_size': 10,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_male_real': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male"],
        'num_batches': 200,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_female_real': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["female"],
        'num_batches': 200,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_batch_real': { 
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 10,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male_.1_batch5_real': { 
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 5,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male_.1_male_real3': { # real2 messed up (ran in sandbox)
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 100,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_male_real4': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_male_real5': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 10,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    ##########################################################################
    # Experiments Friday March 23, 2012
    ##########################################################################
    'gtav_male_.1_size150': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 150,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_size125': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 125,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_size100': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 100,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_size75': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 75,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_size50': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_size25': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 25,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_size10': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 10,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_size5': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 5,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },

    'gtav_male_.1_batch_size10': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 10,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male_.1_batch_size10_noredundancy': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 10,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_batch_size5': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 5,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male_.1_batch_size5_noredundancy': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 5,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },

    'gtav_male_.01_size50': {
        'dataset': 'gtav_male_.01',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.25_size50': {
        'dataset': 'gtav_male_.25',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.5_size50': {
        'dataset': 'gtav_male_.5',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.75_size50': {
        'dataset': 'gtav_male_.75',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.9_size50': {
        'dataset': 'gtav_male_.9',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.99_size50': {
        'dataset': 'gtav_male_.99',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },

    # Monday morning 3/26
    'gtav_male_.1_batch_size20': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male_.1_batch_size20_noredundancy': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_batch_size15': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 15,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male_.1_batch_size15_noredundancy': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 15,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },


    # Tuesday 3/27
    'gtav_male_.1_size150_2': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 150,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male_.1_size125_2': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 125,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },

    # Wednesday, 3/28
    'wgat_normal_batch_size20': { #fluke
        'dataset': 'wgat_normal',
        'vals_to_estimate': ["IS", "ME", "QF"],
        'num_batches': 200,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'wgat_normal_batch_size5': { #good
        'dataset': 'wgat_normal',
        'vals_to_estimate': ["IS", "ME", "QF"],
        'num_batches': 200,
        'batch_size': 5,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'wgat_normal_batch_size5_noredundancy': { #fluke
        'dataset': 'wgat_normal',
        'vals_to_estimate': ["IS", "ME", "QF"],
        'num_batches': 1000,
        'batch_size': 5,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'wgat_normal_batch_size20_noredundancy': { #good
        'dataset': 'wgat_normal',
        'vals_to_estimate': ["IS", "ME", "QF"],
        'num_batches': 1000,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },

    # Thursday 3/29
    'wgat_normal_size50': { # i had to kill the last three of these because they had a comment in them:/
        'dataset': 'wgat_normal',
        'vals_to_estimate': ["IS", "ME", "QF"],
        'num_batches': 500,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'wgat_normal_size20': {
        'dataset': 'wgat_normal',
        'vals_to_estimate': ["IS", "ME", "QF"],
        'num_batches': 500,
        'batch_size': 20,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'wgat_normal_size5': {
        'dataset': 'wgat_normal',
        'vals_to_estimate': ["IS", "ME", "QF"],
        'num_batches': 500,
        'batch_size': 5,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'wgat_normal2_batch_size20_noredundancy': {
        'dataset': 'wgat_normal',
        'vals_to_estimate': ["IS", "ME", "QF"],
        'num_batches': 500,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'wgat_normal2_batch_size5_noredundancy': {
        'dataset': 'wgat_normal',
        'vals_to_estimate': ["IS", "ME", "QF"],
        'num_batches': 500,
        'batch_size': 5,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'shape_yellowoutline_.1_size50': {
        'dataset': 'shape_yellowoutline_.1',
        'vals_to_estimate': ["yellow", "orange"],
        'num_batches': 500,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'shape_triangle_.1_size50': {
        'dataset': 'shape_triangle_.1',
        'vals_to_estimate': ["triangle", "circle"],
        'num_batches': 500,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'shape_yellowoutline2_.1_size50': {
        'dataset': 'shape_yellowoutline_.1',
        'vals_to_estimate': ["yellow", "orange"],
        'num_batches': 500,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'shape_triangle2_.1_size50': {
        'dataset': 'shape_triangle_.1',
        'vals_to_estimate': ["triangle", "circle"],
        'num_batches': 500,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },



    'gtav_male2_.01_size50': {
        'dataset': 'gtav_male_.01',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.1_size50': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.25_size50': {
        'dataset': 'gtav_male_.25',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.5_size50': {
        'dataset': 'gtav_male_.5',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.75_size50': {
        'dataset': 'gtav_male_.75',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.9_size50': {
        'dataset': 'gtav_male_.9',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.99_size50': {
        'dataset': 'gtav_male_.99',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'shape_yellowoutline3_.1_size50': {
        'dataset': 'shape_yellowoutline_.1',
        'vals_to_estimate': ["yellow", "orange"],
        'num_batches': 500,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },
    'shape_triangle3_.1_size50': {
        'dataset': 'shape_triangle_.1',
        'vals_to_estimate': ["triangle", "circle"],
        'num_batches': 500,
        'batch_size': 50,
        'display_style': 'tile',
        'assignments': 1,
        'price': 0.01
    },

    # Friday March 30, 2012
    'gtav_male2_.01_batch_size20_noredundancy': {
        'dataset': 'gtav_male_.01',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.01_batch_size20': {
        'dataset': 'gtav_male_.01',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male2_.1_batch_size20_noredundancy': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.1_batch_size20': {
        'dataset': 'gtav_male_.1',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male2_.25_batch_size20_noredundancy': {
        'dataset': 'gtav_male_.25',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.25_batch_size20': {
        'dataset': 'gtav_male_.25',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male2_.5_batch_size20_noredundancy': {
        'dataset': 'gtav_male_.5',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.5_batch_size20': {
        'dataset': 'gtav_male_.5',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male2_.75_batch_size20_noredundancy': {
        'dataset': 'gtav_male_.75',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.75_batch_size20': {
        'dataset': 'gtav_male_.75',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male2_.9_batch_size20_noredundancy': {
        'dataset': 'gtav_male_.9',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.9_batch_size20': {
        'dataset': 'gtav_male_.9',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },
    'gtav_male2_.99_batch_size20_noredundancy': {
        'dataset': 'gtav_male_.99',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 1000,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 1,
        'price': 0.01
    },
    'gtav_male2_.99_batch_size20': {
        'dataset': 'gtav_male_.99',
        'vals_to_estimate': ["male", "female"],
        'num_batches': 200,
        'batch_size': 20,
        'display_style': 'batch',
        'assignments': 5,
        'price': 0.01
    },


}

def load_run(run_name):
    if run_name not in run_defs:
        raise Exception("run_name not in experiment list (runs.py)")
    ds = run_defs[run_name]
    return (run_name, ds['dataset'], ds['vals_to_estimate'], ds['num_batches'], ds['batch_size'], ds['display_style'], ds['assignments'], ds['price'])
