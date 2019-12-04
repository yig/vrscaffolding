using Statistics: mean
using LinearAlgebra: svd

"""
Given:
    points: a sequence of points (length >= 2)
Returns:
    A length-2 sequence of points which are the endpoints of a line segment approximating
    `points`
"""
function fit_line_segment_to_points( points; save_test_case = false )
    if save_test_case
        fit_line_segment_to_points_test_case( points )
    end
    
    @assert length( points ) >= 2
    @assert ndims( points ) == 2
    
    ## points is n-by-dimension. Make sure it's a Float.
    points = convert( Array{Float64}, points )
    
    ### We'll fit a line by PCA.
    ### 1 Center the points.
    ### 2 Project the centered points along the first axis.
    ### 3 Take the min and max projections as the endpoints.
    ### 4 Rotate back.
    
    ### 1
    center = mean( points, dims = 1 )
    points = points .- center
    
    ### 2
    F = svd( points )
    curve_rot = F.Vt[1:1,:] * points'
    size(curve_rot)
    
    ### 3
    first = minimum( curve_rot )
    last = maximum( curve_rot )
    
    ### 4
    F.Vt[1:1,:]
    F.Vt[1:1,:] * first
    segment_unrot = [ F.Vt[1:1,:] * first; F.Vt[1:1,:] * last ]
    size(segment_unrot)
    segment_unrot .+= center
    return segment_unrot
end

function fit_line_segment_to_points_test_case( points, path = "" )
    if length(path) == 0
        path = "fit_line_debug.jl"
    end
    
    open( path, "w" ) do io
        write( io, string(
"""
include("fit_line.jl")
@show points = """, repr(points), "\n",
"""
@show segment = fit_line_segment_to_points( points )
""" ) )
    end
    
    println( "Saved: ", path )
end

function test_fit_line_segment_to_points()
    ## curve = asfarray( [ ( 0,0 ), ( 1,0 ), ( 1,1 ), ( 0,1 ), ( 0,0 ) ] )
    ## curve = [ 0 0; 2 0; 2 1; 0 1; 0 0 ]
    curve = [ 0 0; 0.1 0.1; 1 1 ]
    ## curve = random.random( ( 10, 2 ) )
    println( curve )
    
    segment = fit_line_segment_to_points( curve, save_test_case = true )
    println( "first:", segment[1,:] )
    println( "last:", segment[2,:] )
end

# test_fit_line_segment_to_points()
