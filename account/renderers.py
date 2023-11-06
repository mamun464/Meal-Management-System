from rest_framework import renderers
import json

class UserRenderer(renderers.JSONRenderer):
    charset = 'utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = ''
        # print("Inside Render funtion")
        if 'ErrorDetail' in str(data):
            # print("Inside ErrorDetails funtion")
            response = json.dumps({'errors':data})
        else:
            response = json.dumps(data)
            # print("Inside Else funtion")

        return response