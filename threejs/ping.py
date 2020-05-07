#!/usr/bin/env python3

## This example comes from: https://websockets.readthedocs.io/en/stable/

import asyncio
import websockets
import json

import scaffold_sketch
import fit_line

async def ping_server( websocket, path ):
    state = scaffold_sketch.make_new_program_state()
    
    async for message in websocket:

        parsed = message.split( " ", 1 )
        command = parsed[0]
        parameters = None if len( parsed ) == 1 else parsed[1]
        
        if command == "construction-stroke":
            input_curve = json.loads( parameters )
            
            new_line = scaffold_sketch.incorporate_new_raw_construction_line( state, input_curve )
            
            # echo:
            await websocket.send( "new-straight-line " + json.dumps( new_line.tolist() ) )
        elif command == "shape-stroke":
            input_curve = json.loads(parameters)
            print( input_curve )

start_server = websockets.serve( ping_server, "localhost", 9000 )
asyncio.get_event_loop().run_until_complete( start_server )
asyncio.get_event_loop().run_forever()
