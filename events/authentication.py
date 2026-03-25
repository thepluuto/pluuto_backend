from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from django.core.cache import cache

class PluutoJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except (AuthenticationFailed, InvalidToken) as e:
            # List of endpoints that tolerate invalid tokens (fallback to AnonymousUser)
            # so the public feed still loads rather than returning 401
            tolerated_paths = [
                '/api/home/',
                '/api/search/',
                '/api/host-categories/',
                '/api/artists/',
                '/api/venues/',
                '/api/experience-providers/',
                '/api/categories/',
                '/api/events/user/upcoming/',
                '/api/events/user/past/',
                '/api/events/admin-created/'
            ]
            
            path = request.path
            
            # Allow fallback for GET requests to the specific endpoints, 
            # or the generic /api/events/ list / detail, /api/hosts/ detail
            is_public_get = False
            if request.method == 'GET':
                if path in tolerated_paths:
                    is_public_get = True
                elif path.startswith('/api/events/') and '/action/' not in path and '/update' not in path and '/collaborate/' not in path and '/my/' not in path:
                    is_public_get = True
                elif path.startswith('/api/hosts/') and '/requests/' not in path:
                    is_public_get = True
                    
            if is_public_get:
                return None
                
            # If not a public GET route, throw the real unauthorized error
            raise e

    def get_validated_token(self, raw_token):
        validated_token = super().get_validated_token(raw_token)
        
        # Check standard memory cache to see if access token was explicitly logged out
        jti = validated_token.get('jti')
        if jti and cache.get(f"blacklisted_token_{jti}"):
            raise AuthenticationFailed('Token has been blacklisted / logged out.')
            
        return validated_token
