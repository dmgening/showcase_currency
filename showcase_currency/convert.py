from aiohttp import web
import marshmallow as ma

from .store import currency_convert
from .utils import error_response


class ConvertQuerySchema(ma.Schema):
    source = ma.fields.String(load_from='from', required=True, validate=[ma.validate.Length(3)])
    target = ma.fields.String(load_from='to', required=True, validate=[ma.validate.Length(3)])
    amount = ma.fields.Float(required=True, validate=[ma.validate.Range(min=0)])


async def convert_view(request):
    schema = ConvertQuerySchema(strict=True)
    try:
        query = schema.load(request.rel_url.query).data
    except ma.ValidationError as exc:
        return error_response('Request validation error', exc.messages, status=400)

    try:
        result = await currency_convert(request.app['redis'], **query)
    except Exception as exc:
        logging.exception(exc)
        return error_response('Internal error while conversion', status=500)
    
    return web.json_response({'result': result})
