using HTTP
using JSON

include("fit_line.jl")

HTTP.WebSockets.listen("127.0.0.1", UInt16(9000)) do ws
    while !eof(ws)
        message = String(readavailable(ws))
        command, body = split( message, " ", limit = 2 )
        if command == "line-fit" || command == "beautify"
            input_curve = JSON.parse( body )
            ## Convert to a 2D array:
            input_curve = hcat(input_curve...)'
            segment = fit_line_segment_to_points( input_curve, save_test_case = true )
            ## Surprise! We must transpose the segment when converting to JSON,
            ## because Julia transposes its data for JavaScript as
            ## a result of being column-major versus row-major.
            ## From: https://github.com/JuliaIO/JSON.jl/issues/93
            reply = string( "curve-optimized ", JSON.json( segment' ) ) 
            write( ws, reply )
        else
            println( "Unknown command: ", command )
        end
    end
end
