#!/usr/bin/env python3

## This example comes from: https://websockets.readthedocs.io/en/stable/

import asyncio
import websockets
import json

import scaffold_sketch

async def ping_server( websocket, path ):
    state = scaffold_sketch.make_new_program_state()
    
    async for message in websocket:

        parsed = message.split( " ", 1 )
        command = parsed[0]
        parameters = None if len( parsed ) == 1 else parsed[1]

        if command == "new-stroke":
            input_curve = json.loads( parameters )
            print( command )
            print( input_curve )
        # echo:
        await websocket.send( message )

start_server = websockets.serve( ping_server, "localhost", 9000 )
asyncio.get_event_loop().run_until_complete( start_server )
asyncio.get_event_loop().run_forever()
