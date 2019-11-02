#!/usr/bin/env python3

## This example comes from: https://websockets.readthedocs.io/en/stable/

import asyncio
import websockets

async def echo( websocket, path ):
    async for message in websocket:
        print( message )
        await websocket.send( message )

start_server = websockets.serve( echo, "localhost", 9000 )

asyncio.get_event_loop().run_until_complete( start_server )
asyncio.get_event_loop().run_forever()
