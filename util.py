import numpy as np

def resample_line_strip_num_samples( line_strip, num_samples ):
    '''
    Given:
        line_strip: a sequence of points (length >= 2)
        num_samples: an integer >= 2
    Returns:
        a sequence `num_samples` points evenly spaced along `line_strip`
        according to arc length

    tested
    >>> line_strip = [ (0,0), (1,0), (1,1), (0,1), (0,0) ]
    >>> assert allclose( resample_line_strip_num_samples( line_strip, 5 ), line_strip )
    >>> assert allclose( resample_line_strip_num_samples( line_strip, 9 )[::2], line_strip )
    '''

    line_strip = np.asfarray( line_strip )
    ## `line_strip` should have shape N-by-dimension
    assert len( line_strip.shape ) == 2
    assert len( line_strip ) >= 2
    assert num_samples >= 2

    ### 1 Compute the fraction of total arc length of each line segment.
    ### 2 Find the line segment containing each 1/N sample points.
    ### 3 Compute the interpolation value between the start and end of the line segment.
    ###   t_desired = t_start + s*( t_end - t_start ) <=> s = ( t_desired - t_start )/( t_end - t_start )
    ### 4 Interpolate the containing line segments accordingly.
    ### 5 Assemble the results.

    ### 1
    line_segments = line_strip[1:] - line_strip[:-1]
    lengths = np.sqrt( ( line_segments**2 ).sum( axis = 1 ) )
    total_length = lengths.sum()
    cumulative_lengths = np.append( [0], lengths.cumsum() )/total_length
    # print( 'cumulative_lengths:', cumulative_lengths )

    ### 2
    ## Drop the first and last element in linspace, which are 0 and 1
    ts = np.linspace( 0, 1, num_samples )[1:-1]
    # print( 'ts:', ts )
    edge_starts = np.searchsorted( cumulative_lengths, ts )-1
    assert ( edge_starts >= 0 ).all()
    # print( 'edge_starts:', edge_starts )

    ### 3
    edge_interpolation_parameters = (
        ( ts - cumulative_lengths[ edge_starts ] )
        /
        ( cumulative_lengths[ edge_starts+1 ] - cumulative_lengths[ edge_starts ] )
    )

    ### 4
    middle = line_strip[ edge_starts ] + edge_interpolation_parameters[:,None]*( line_strip[ edge_starts+1 ] - line_strip[ edge_starts ] )

    ### 5
    ## Put the first and last elements back
    resampled = np.concatenate( ( line_strip[:1], middle, line_strip[-1:] ) )

    return resampled

def resample_line_strip_arc_length( line_strip, arc_length ):
    '''
    Given:
        line_strip: a sequence of points (length >= 2)
        arc_length: a positive number (floating point)
    Returns:
        a sequence points evenly spaced along `line_strip`
        whose arc length distance is approximately arc_length

    tested
    >>> line_strip = [ (0,0), (1,0), (1,1), (0,1), (0,0) ]
    >>> assert allclose( resample_line_strip_arc_length( line_strip, 1 ), line_strip )
    >>> assert allclose( resample_line_strip_arc_length( line_strip, 0.5 )[::2], line_strip )
    '''

    line_strip = np.asfarray( line_strip )
    ## `line_strip` should have shape N-by-dimension
    assert len( line_strip.shape ) == 2
    assert len( line_strip ) >= 2
    assert arc_length > 0

    ### 1 Compute the total length
    ### 2 Round 1 + the total length / arc length to the nearest integer >= 2.
    ###   The 1+ is for the initial point.
    ### 3 Call resample_line_strip_num_samples()

    ### 1
    line_segments = line_strip[1:] - line_strip[:-1]
    lengths = np.sqrt( ( line_segments**2 ).sum( axis = 1 ) )
    total_length = lengths.sum()

    ### 2
    num_samples = 1 + total_length / arc_length
    num_samples = max( 2, int( round( num_samples ) ) )

    ### 3
    return resample_line_strip_num_samples( line_strip, num_samples )