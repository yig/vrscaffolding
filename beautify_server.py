#!/usr/bin/env python3

## This example comes from: https://websockets.readthedocs.io/en/stable/

import asyncio
import websockets
import json
import beautify

async def beautify_server( websocket, path ):
    async for message in websocket:
        print( message )
        # echo:
        ## await websocket.send( message )
        
        command, body = message.split( " ", 1 )
        if command == "beautify":
            input_curve = json.loads( body )
            ## resample every 10 pixels
            input_curve = beautify.resample_line_strip_arc_length( input_curve, 10 )
            
            async def send_stroke( rotations, scales ):
                output_curve = beautify.transform_curve( input_curve, rotations, scales )
                await websocket.send( "curve-optimized " + json.dumps( output_curve.tolist() ) )
            
            ## Our scipy minimize() callback can't make an async call.
            ## Let's send the curve in progress synchronously.
            ## From: https://github.com/aaugustin/websockets/issues/71
            ## UPDATE: Doesn't work, because we are inside an event loop.
            def send_stroke_sync( rotations, scales ):
                asyncio.new_event_loop().run_until_complete( send_stroke( rotations, scales ) )
            
            ## I wish I could use the callback to show progress.
            rotations, scales = beautify.optimize( input_curve, save_test_case = True )#, callback = send_stroke_sync )
            await send_stroke( rotations, scales )
        else:
            print( "Unknown command: ", command )

start_server = websockets.serve( beautify_server, "localhost", 9000 )

asyncio.get_event_loop().run_until_complete( start_server )
asyncio.get_event_loop().run_forever()
