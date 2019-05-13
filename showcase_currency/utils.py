from aiohttp import web

def error_response(message, data=None, **kwargs):
    payload = {'error': {'message': message}}
    if data is not None:
        payload['error']['data'] = data
    return web.json_response(payload, **kwargs)