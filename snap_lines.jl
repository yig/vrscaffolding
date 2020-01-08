using LinearAlgebra

"""
Given:
    segment: an array of two d-dimensional points (a 2-by-d array)
    other_segments: an array of N arrays of two d-dimensional points (an N-by-2-by-d array)
    threshold_cosangle: snapping threshold in cos(angle).
    orthogonal (optional): if true, also consider perpendicular snapping (default: false)
Returns:
    `segment` updated to be aligned with a segment in other_segments
"""
function snap_line_segment_to_line_segments( segment, other_segments, threshold_cosangle; orthogonal = false )
    ## Make sure we have the right multi-dimensional array.
    segment = convert( Array{Float64,2}, segment )
    @assert size( segment, 1 ) == 2
    
    ## Make sure we have the right multi-dimensional array.
    other_segments = convert( Array{Float64,3}, other_segments )
    @assert size( other_segments, 2 ) == 2
    N = size( other_segments, 1 )
    
    ## The dimensions must match.
    @assert size( segment, 2 ) == size( other_segments, 3 )
    d = size( segment, 2 )
    
    ### 1 Compute angles between segment and all other segments.
    ### 2 Find the closest angle.
    ###   If orthogonal is true, then also consider perpendicular angles.
    ### 3 If it is less than threshold_cosangle, then rotate the
    ###   segment about its midpoint to be parallel.
    
    segment_dir = normalize( segment[2,:] - segment[1,:] )
    
    angles = zeros( N )
    other_dirs = zeros( N, d )
    
    ### 1
    for i in 1:N
        other_start = other_segments[i,1,:]
        other_end = other_segments[i,2,:]
        
        other_dirs[i,:] = normalize( other_end - other_start )
        angles[i] = segment_dir ⋅ other_dirs[i,:]
    end
    
    @show angles
    @show other_dirs
    
    ### 2
    @show best_snap = argmax( angles )
    
    ### 3
    ## A larger cosine threshold means the angles are closer.
    if angles[ best_snap ] < threshold_cosangle
        return segment
    end
    
    ## Rotate to parallel by simply translating and scaling the desired unit direction
    ## appropriately.
    segment_length = norm( segment[2,:] - segment[1,:] )
    segment_midpoint = .5 * ( segment[2,:] + segment[1,:] )
    snap_dir = other_dirs[best_snap,:]
    @show snap_dir
    return [
        segment_midpoint + segment_length * snap_dir,
        segment_midpoint - segment_length * snap_dir
        ]
end

function test_snap_line_segment_to_line_segments()
    segment = [ -1 -.1; 1 .1 ]
    other_segments = permutedims( cat( [ 0 0; 1 0 ], [ 0 0; 0 1 ], dims = 3 ), [ 3, 1, 2 ] )
    
    @show snap_line_segment_to_line_segments( segment, other_segments, cos(pi/2) )
end

test_snap_line_segment_to_line_segments()
