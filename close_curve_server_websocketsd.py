#!/usr/bin/env python3

## Run with:
# websocketd --address 127.0.0.1 --port 9000 python3 close_curve_server_websocketsd.py
## Debug with:
# echo 'beautify [ [ 0, 0 ], [ 1, 0 ], [ 2, 0 ], [ 3, 0 ] ]' | python3 close_curve_server_websocketsd.py

import sys
import json
import close_curve

for message in sys.stdin:
    print( message, file = sys.stderr )
    if len( message.strip() ) == 0: continue
    
    # echo:
    # print( message )
    
    command, body = message.split( " ", 1 )
    if command == "beautify":
        input_curve = json.loads( body )
        ## resample every 10 pixels
        input_curve = close_curve.resample_line_strip_arc_length( input_curve, 10 )
        if len( input_curve ) <= 2:
            print( "Curve too short.", file = sys.stderr )
            continue
        
        def send_stroke( rotations, scales ):
            output_curve = close_curve.transform_curve( input_curve, rotations, scales )
            ## The extra '\n' makes sure the websocketsd message goes out.
            sys.stdout.write( "curve-optimized " + json.dumps( output_curve.tolist() ) + "\n" )
            sys.stdout.flush()
        
        ## I wish I could use the callback to show progress.
        print( "Before optimize.", file = sys.stderr )
        rotations, scales = close_curve.optimize( input_curve, save_test_case = True, callback = send_stroke )
        send_stroke( rotations, scales )
    else:
        print( "Unknown command: ", command, file = sys.stderr )
