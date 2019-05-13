import logging
import marshmallow as ma
from aiohttp import web
from json.decoder import JSONDecodeError

from .utils import error_response
from .store import CurrencyUploader


# FIXME: Validators
class UploadSchema(ma.Schema):
    source = ma.fields.String(load_from='from', required=True, validate=[ma.validate.Length(3)])
    target = ma.fields.String(load_from='to', required=True, validate=[ma.validate.Length(3)])
    rate = ma.fields.Float(required=True, validate=[ma.validate.Range(min=0)])

    @ma.validates_schema
    def source_isnt_target(self, data):
        print(data)
        source = data.get('source', 's').upper()
        target = data.get('target', 't').upper()
        if source == target:
            raise ma.ValidationError('Must use diffrent currency for from and to fields')


async def upload_view(request):
    schema = UploadSchema(many=True, strict=True)
    try:
        payload = schema.load(await request.json()).data
    except ma.ValidationError as exc:
        return error_response('Request validation error', exc.messages, status=400)
    except JSONDecodeError:
        return error_response('Malformed request body', status=400)

    try:
        replace_current = False
        uploader = CurrencyUploader(request.app['redis'], replace=replace_current)
        for record in payload:
            uploader.save(**record)
        await uploader.execute()
    except Exception as exc:
        logging.exception(exc)
        return error_response('Internal error while saving convertion rates', status=500)

    return web.json_response({'result': 'OK'})