#!/usr/bin/env python

import asyncio
import websockets
import json
import sys

connections = set()
daily_users = []

async def gather_first(data, websocket):
    """Connects and logs device of first type"""
    return data

async def handle_first(ip, websocket):
    data = {
        'device': 'first',
        'ip': ip,
        'results': ''
    }
    try:
        data = await gather_first(data, websocket)
    except Exception as e:
        print(e)
    finally:
        return data
        
async def gather_second(data, websocket):
    """Connects and logs device of second type"""
    return data
        
async def handle_second(ip, websocket):
    data = {
        'device': 'second',
        'ip': ip,
        'results': ''
    }
    try:
        data = await gather_second(data, websocket)
    except Exception as e:
        print(e)
    finally:
        return
        
async def get_ip(device, _arg*):
    return device

async def get_device_type(_arg*):
    return
    
async def confirm_device_type(device, _argv*):
    return
    
async def handle_method0(device, websocket, ip, _arg*):
    if device == 'unknown':
        await websocket.send(json.dumps({'type': 'update', 'message': 'Server responded. Looking up device information...'}))
        device = await get_device_type(ip)
    elif secondary == False:
        await websocket.send(json.dumps({'type': 'update', 'message': 'Server responded. Confirming device type...'}))
        if await confirm_device_type(device) == False:
            await websocket.send(json.dumps({'type': 'update', 'message': 'Confirmation of device type failed, returning power to client...'}))
            return False
        await websocket.send(json.dumps({'type': 'update', 'message': 'Device type confirmed. Polling device information...'}))
    if device == 'first':
        data = await handle_first(ip, websocket)
        if data['device'] != 'failed':
            await websocket.send(json.dumps({'type': 'update', 'message': 'Data polling succeeded. Sending you stats...'}))
        else:
            await websocket.send(json.dumps({'type': 'update', 'message': 'Data polling failed. Please reload page...'}))
        return data
    elif device == 'second':
        data = await handle_second(ip, websocket)
        if data['device'] != 'failed':
            await websocket.send(json.dumps({'type': 'update', 'message': 'Data polling succeeded. Sending you stats...'}))
        else:
            await websocket.send(json.dumps({'type': 'update', 'message': 'Data polling failed. Please reload page...'}))
        return data
    else:
        data = {'type': 'results', 'device': 'failed'}
        return data
    
async def handle_method1(device, websocket, _arg*):
    if device == 'unknown':
        await websocket.send(json.dumps({'type': 'update', 'message': 'Server responded. Looking up device information...'}))
        device = await get_device_type(_arg[0])
    else:
        await websocket.send(json.dumps({'type': 'update', 'message': 'Server responded. Confirming device type...'}))
        if await confirm_device_type(device, _arg[0]) == False:
            await websocket.send(json.dumps({'type': 'update', 'message': 'Confirmation of device type failed, returning power to client...'}))
            return False
    await websocket.send(json.dumps({'type': 'update', 'message': 'Device type confirmed. Getting ip, slot, port information...'}))
    ip = await get_ip(device, _arg[0])
    await websocket.send(json.dumps({'type': 'update', 'message': 'Login information gathered. Polling device information...'}))
    data = await handle_method0(device, websocket, ip)
    return data
    
async def handle_method2(device, websocket, _arg*):
    if device == 'unknown':
        await websocket.send(json.dumps({'type': 'update', 'message': 'Server responded. Looking up device information...'}))
        device = await get_device_type(_arg[0])
    else:
        await websocket.send(json.dumps({'type': 'update', 'message': 'Server responded. Confirming device type...'}))
        if await confirm_device_type(device, _arg[0]) == False:
            await websocket.send(json.dumps({'type': 'update', 'message': 'Confirmation of device type failed, returning power to client...'}))
            return False
    await websocket.send(json.dumps({'type': 'update', 'message': 'Device type confirmed. Getting ip, slot, port information...'}))
    ip = await get_ip(device, _arg[0])
    await websocket.send(json.dumps({'type': 'update', 'message': 'Login information gathered. Polling device information...'}))
    data = await handle_method0(device, websocket, ip)
    return data

async def update_users(websocket, _arg*):
    if connections:
        await asyncio.wait([c.send(json.dumps({'type': 'cusers', 'value': len(connections)})) for c in connections])
        if _arg[0]:
            daily_users.append(websocket)
            await asyncio.wait([c.send(json.dumps({'type': 'dusers', 'value': len(daily_users)})) for c in connections])

    
async def register(websocket):
    await websocket.send(json.dumps({'type': 'connection', 'value': 'Connected'}))
    connections.add(websocket)
    await update_users(websocket, True)
    print("Clients: %s" % str(len(connections)))

async def unregister(websocket, _arg*):
    if _arg[0] == False:
        connections.remove(websocket)
        await update_users(websocket, False)
    if _arg[0] == True:
        await websocket.send(json.dumps({'type': 'connection', 'value': 'Disconnected'}))
        await websocket.close()
    print("Clients: %s" % str(len(connections)))

async def handle_admin(websocket, cmd):
    if cmd == 'disconnect':
        await unregister(websocket, True)

async def connection_handler(websocket, path):
    await register(websocket)
    try:
        async for in_msg in websocket:
            in_data = json.loads(in_msg)
            if in_data['type'] == 'admin':
                if in_data['cmd'] == 'close':
                    sys.exit()
                await handle_admin(websocket, in_data['cmd'])
            if in_data['type'] == 'method1':
                out_data = await handle_method1(in_data['device'], in_data['method1'], websocket)
                await websocket.send(json.dumps(out_data))
            if in_data['type'] == 'method2':
                out_data = await handle_method2(in_data['device'], in_data['method2'], websocket)
                await websocket.send(json.dumps(out_data))
            elif in_data['type'] == 'method0':
                out_data = await handle_method0(in_data['device'], in_data['method0'], websocket)
                await websocket.send(json.dumps(out_data))
    finally:
        await unregister(websocket)

loop = asyncio.get_event_loop()
loop.run_until_complete(
    websockets.serve(connection_handler, '', '0000'))
loop.run_forever()
