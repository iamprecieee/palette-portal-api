from typing import List
from drf_spectacular.extensions import _SchemaType, OpenApiAuthenticationExtension
from drf_spectacular.openapi import AutoSchema


class PaletteTokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "user.models.PaletteTokenAuthentication"
    name = "PaletteTokenAuthentication"
    priority = 1
    
    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
        }
        
        
class GoogleOAuth2Authentication(OpenApiAuthenticationExtension):
    target_class = "drf_social_oauth2.authentication.SocialAuthentication"
    name = "GoogleOAuth2"
    priority = 1
    
    def get_security_definition(self, auto_schema):
        return {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "https://accounts.google.com/o/oauth2/auth",
                    "tokenUrl": "https://oauth2.googleapis.com/token",
                    "scopes": {
                        "email": "Email address",
                        "profile": "Profile info"
                    }
                }
            }
        }
        
        
class TwitterOAuth2Authentication(OpenApiAuthenticationExtension):
    target_class = "drf_social_oauth2.authentication.SocialAuthentication"
    name = "TwitterOAuth2"
    priority = -1
    
    def get_security_definition(self, auto_schema):
        return {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "https://api.twitter.com/oauth/authorize",
                    "tokenUrl": "https://api.twitter.com/oauth/access_token",
                    "scopes": {
                        "read": "Grants read access",
                    }
                }
            }
        }