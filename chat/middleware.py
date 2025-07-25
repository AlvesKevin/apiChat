import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('api_requests')

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log basic request info
        logger.info(f"📥 {request.method} {request.path}")
        logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'N/A')}")
        logger.info(f"   User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')[:100]}")
        logger.info(f"   Content-Type: {request.META.get('CONTENT_TYPE', 'N/A')}")
        
        # Log headers (excluding sensitive ones)
        sensitive_headers = ['authorization', 'x-api-key', 'cookie']
        headers = {}
        for key, value in request.META.items():
            if key.startswith('HTTP_') and not any(sensitive in key.lower() for sensitive in sensitive_headers):
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
        
        if headers:
            logger.debug(f"   Headers: {headers}")
        
        # Log authentication info if present
        if 'HTTP_X_API_KEY' in request.META:
            token = request.META['HTTP_X_API_KEY']
            logger.debug(f"   Auth Token: {token[:10]}...")
        
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            status_emoji = "✅" if 200 <= response.status_code < 300 else "❌"
            logger.info(f"📤 {status_emoji} {request.method} {request.path} - {response.status_code} ({duration:.3f}s)")
            
            # Log response details for errors
            if response.status_code >= 400:
                try:
                    if hasattr(response, 'content') and response.content:
                        content = response.content.decode('utf-8')
                        if content.startswith('{'):  # JSON response
                            response_data = json.loads(content)
                            logger.warning(f"   Error Response: {response_data}")
                        else:
                            logger.warning(f"   Error Response: {content[:200]}")
                except:
                    logger.warning(f"   Error Response: Could not parse response content")
            
            # Log slow requests
            if duration > 1.0:
                logger.warning(f"🐌 Slow request: {request.method} {request.path} took {duration:.3f}s")
        
        return response
    
    def process_exception(self, request, exception):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.error(f"💥 Exception in {request.method} {request.path} after {duration:.3f}s: {exception}")
        else:
            logger.error(f"💥 Exception in {request.method} {request.path}: {exception}")
        
        return None