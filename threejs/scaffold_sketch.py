from __future__ import print_function, division



'''
This module stores the state for the scaffold sketching program.
The state is a dictionary with certain keys.
Call `make_new_program_state()` to create one.
'''

def make_new_program_state():
    '''
    Returns a dictionary for storing the state of a scaffold sketching
    program. The dictionary has two keys whose values are lists:
        'construction_lines'
        'shape_curves'
    '''
    
    state = { 'construction_lines': [], 'shape_curves': [], 'key_points': [] }
    return state

