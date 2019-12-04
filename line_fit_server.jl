using HTTP
using JSON

include("line_fit.jl")

HTTP.WebSockets.listen("127.0.0.1", UInt16(9000)) do ws
    while !eof(ws)
        message = String(readavailable(ws))
        command, body = split( message, " ", limit = 2 )
        if command == "line-fit" || command == "beautify"
            input_curve = JSON.parse( body )
            segment = fit_line_segment_to_points( input_curve )
            write( ws, JSON.json( segment ) )
        else
            println( "Unknown command: ", command )
        end
    end
end
