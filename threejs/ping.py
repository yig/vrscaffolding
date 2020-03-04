#!/usr/bin/env python3

## This example comes from: https://websockets.readthedocs.io/en/stable/

import asyncio
import websockets

async def ping_server( websocket, path ):
    async for message in websocket:
        ## print( message )
        # echo:
        await websocket.send( message )

start_server = websockets.serve( ping_server, "localhost", 9000 )
asyncio.get_event_loop().run_until_complete( start_server )
asyncio.get_event_loop().run_forever()
