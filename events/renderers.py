from rest_framework.renderers import JSONRenderer

class StandardResponseRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Default behavior for non-200-ish codes that might be returning None or weird stuff
        if data is None:
            data = {}

        # Check if the data is already standardized (from our api_response utility)
        if isinstance(data, dict):
            if 'status' in data and 'message' in data and ('data' in data or 'errors' in data):
                # Ensure 'data' key exists if missing (e.g. valid error response might just have status/message)
                if 'data' not in data:
                    data['data'] = None
                return super().render(data, accepted_media_type, renderer_context)

        # Get the response status code
        response = renderer_context.get('response')
        status_code = response.status_code if response else 200
        
        # Determine status
        status = 'success'
        if status_code >= 400:
            status = 'error'

        # Determine message
        message = "Success"
        if status == 'error':
            message = "An error occurred"
            if isinstance(data, dict):
                # DRF often returns {'detail': 'Error message'}
                if 'detail' in data:
                    message = str(data['detail'])
                # Or validation errors e.g. {'field': ['Error']}
                else:
                    message = "Validation Error"
            elif isinstance(data, list):
                message = "Validation Error"

        # Construct the standard response
        response_data = {
            "status": status,
            "message": message,
            "data": data
        }
        
        return super().render(response_data, accepted_media_type, renderer_context)
