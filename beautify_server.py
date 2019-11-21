#!/usr/bin/env python3

## This example comes from: https://websockets.readthedocs.io/en/stable/

import asyncio
import websockets
import json
import beautify

async def echo( websocket, path ):
    async for message in websocket:
        print( message )
        # echo:
        ## await websocket.send( message )
        
        command, body = message.split( " ", 1 )
        if command == "beautify":
            input_curve = json.loads( body )
            ## resample every 5 pixels
            input_curve = beautify.resample_line_strip_arc_length( input_curve, 10 )
            
            async def send_stroke( rotations, scales ):
                output_curve = beautify.transform_curve( input_curve, rotations, scales )
                await websocket.send( "curve-optimized " + json.dumps( output_curve.tolist() ) )
            
            beautify.optimize_save_test_case( input_curve )
            rotations, scales = beautify.optimize( input_curve )#, callback = send_stroke )
            await send_stroke( rotations, scales )
        else:
            print( "Unknown command: ", command )

start_server = websockets.serve( echo, "localhost", 9000 )

asyncio.get_event_loop().run_until_complete( start_server )
asyncio.get_event_loop().run_forever()
