#!/usr/bin/env python3
"""
Bible Visualization Server with streaming Edge TTS.
Uses aiohttp for proper chunked streaming to browsers.
"""

import asyncio
import os
import socket
import webbrowser
from aiohttp import web
import edge_tts

VOICE = "en-IE-EmilyNeural"

def find_open_port(start=8000, end=9000):
    """Find an available port in the given range."""
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No open port found in range {start}-{end}")

async def handle_tts(request):
    """Stream TTS audio as it's generated."""
    try:
        data = await request.json()
        text = data.get('text', '')
        
        if not text:
            return web.Response(status=400, text="No text provided")
        
        print(f"TTS streaming audio for {len(text)} chars...")
        
        response = web.StreamResponse(
            status=200,
            headers={
                'Content-Type': 'audio/mpeg',
                'Cache-Control': 'no-cache',
                'Access-Control-Allow-Origin': '*',
            }
        )
        await response.prepare(request)
        
        communicate = edge_tts.Communicate(text, VOICE)
        bytes_sent = 0
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                await response.write(chunk["data"])
                bytes_sent += len(chunk["data"])
        
        print(f"TTS sent {bytes_sent} bytes")
        await response.write_eof()
        return response
        
    except Exception as e:
        print(f"TTS Error: {e}")
        import traceback
        traceback.print_exc()
        return web.Response(status=500, text=str(e))

async def handle_options(request):
    """Handle CORS preflight."""
    return web.Response(
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
    )

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port = find_open_port()
    
    app = web.Application()
    app.router.add_post('/api/tts', handle_tts)
    app.router.add_options('/api/tts', handle_options)
    app.router.add_static('/', '.', show_index=True)
    
    url = f"http://localhost:{port}/visualization.html"
    print(f"Bible Visualization Server running at http://localhost:{port}")
    print(f"TTS Voice: {VOICE} (streaming)")
    print("Press Ctrl+C to stop")
    
    webbrowser.open(url)
    web.run_app(app, host='localhost', port=port, print=None)

if __name__ == '__main__':
    run_server()
