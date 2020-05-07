from __future__ import print_function, division

import fit_line

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
    
    state = { 'construction_lines': [], 'shape_curves': [], 'construction_lines_snap_points': [] }
    return state

def incorporate_new_raw_construction_line( state, pts ):
    '''
    Given:
        state: a state as returned by `make_new_program_state`
        pts: raw points from the GUI as a sequence of (x,y,z?) triplets.
    Returns:
        line: a part of points which are the start and end of the new construction line
    
    Modified `state` to add a new construction line based off
    of the raw GUI input `pts`.
    '''
    
    ### 1 Fit a line to the points.
    ### 2 Snap the fit line to existing construction lines.
    ### 3 Store the snapped line as a new construction line in state.
    
    
    ### 1
    line = fit_line.line_fitting( pts )

    ### 2
    snapped_line = fit_line.snap_line_to_other_lines( line, state['construction_lines'],  state['construction_lines_snap_points'])

    ### 3
    state['construction_lines'].append( snapped_line )
    
    ### 4 add snap points for new_line
    snapped_points = fit_line.generate_snap_points_for_line( snapped_line, state['construction_lines_snap_points'] )
    state['construction_lines_snap_points'] = snapped_points

    return snapped_line
