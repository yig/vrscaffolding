#!/usr/bin/env python3

## This example comes from: https://websockets.readthedocs.io/en/stable/

import asyncio
import websockets
import json

import scaffold_sketch
import shape_sketch

async def scaffold_sketch_server( websocket, path ):
    state = scaffold_sketch.make_new_program_state()
    
    
    async for message in websocket:
        # print( message )
        # echo:
        ## await websocket.send( message )
        parsed = message.split( " ", 1 )
        command = parsed[0]
        parameters = None if len( parsed ) == 1 else parsed[1]
        
        if command == "reset":
            state = scaffold_sketch.make_new_program_state()
        elif command == "new-construction-line":
            input_curve = json.loads( parameters )
            new_line = scaffold_sketch.incorporate_new_raw_construction_line( state, input_curve )
            await websocket.send( "add-construction-line " + json.dumps( new_line.tolist() ) )
            # print(state)
        elif command == "undo":
            # will only undo for last construction line now 
            scaffold_sketch.undo( state )
        elif command == "key_points":
           
            key_points = scaffold_sketch.find_key_points( state )
            print(state)
            print(key_points)
            await websocket.send( "add-key-points " + json.dumps( key_points) )
        elif command == "beautify":
            input_curve = json.loads( parameters )
            new_shape = shape_sketch.incorporate_new_raw_shape_line( state, input_curve )
            await websocket.send( "add-shape-line " + json.dumps( new_shape.tolist() ) )
        else:
            print( "Unknown command: ", command )

start_server = websockets.serve( scaffold_sketch_server, "localhost", 9000 )
asyncio.get_event_loop().run_until_complete( start_server )
asyncio.get_event_loop().run_forever()
