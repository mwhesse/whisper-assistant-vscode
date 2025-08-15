"""
Request logging service for tracking API requests and responses
"""
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class RequestLog:
    """Data class for storing request/response information"""
    timestamp: str
    method: str
    path: str
    query_params: Dict[str, Any]
    headers: Dict[str, str]
    request_body: Optional[str]
    response_status: int
    response_body: Optional[str]
    response_headers: Dict[str, str]
    processing_time_ms: float
    client_ip: str
    user_agent: str
    request_id: str

class RequestLogger:
    """Service for logging and retrieving API requests/responses"""
    
    def __init__(self, max_logs: int = 1000):
        """Initialize the request logger with a maximum number of logs to keep"""
        self.max_logs = max_logs
        self.logs: deque = deque(maxlen=max_logs)
        self._request_counter = 0
    
    def log_request(self, 
                   method: str,
                   path: str,
                   query_params: Dict[str, Any],
                   headers: Dict[str, str],
                   request_body: Optional[str],
                   response_status: int,
                   response_body: Optional[str],
                   response_headers: Dict[str, str],
                   processing_time_ms: float,
                   client_ip: str,
                   user_agent: str) -> str:
        """Log a request/response pair"""
        
        self._request_counter += 1
        request_id = f"req_{self._request_counter}_{int(time.time())}"
        
        # Filter sensitive headers
        filtered_headers = self._filter_sensitive_headers(headers)
        filtered_response_headers = self._filter_sensitive_headers(response_headers)
        
        # Truncate large bodies
        truncated_request_body = self._truncate_body(request_body)
        truncated_response_body = self._truncate_body(response_body)
        
        log_entry = RequestLog(
            timestamp=datetime.now().isoformat(),
            method=method,
            path=path,
            query_params=query_params,
            headers=filtered_headers,
            request_body=truncated_request_body,
            response_status=response_status,
            response_body=truncated_response_body,
            response_headers=filtered_response_headers,
            processing_time_ms=processing_time_ms,
            client_ip=client_ip,
            user_agent=user_agent,
            request_id=request_id
        )
        
        self.logs.append(log_entry)
        logger.debug(f"Logged request {request_id}: {method} {path} -> {response_status}")
        
        return request_id
    
    def get_logs(self, limit: Optional[int] = None, 
                 method_filter: Optional[str] = None,
                 path_filter: Optional[str] = None,
                 status_filter: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get logged requests with optional filtering"""
        
        logs = list(self.logs)
        
        # Apply filters
        if method_filter:
            logs = [log for log in logs if log.method.upper() == method_filter.upper()]
        
        if path_filter:
            logs = [log for log in logs if path_filter in log.path]
        
        if status_filter:
            logs = [log for log in logs if log.response_status == status_filter]
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            logs = logs[:limit]
        
        # Convert to dictionaries
        return [asdict(log) for log in logs]
    
    def get_log_by_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific log entry by request ID"""
        for log in self.logs:
            if log.request_id == request_id:
                return asdict(log)
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about logged requests"""
        if not self.logs:
            return {
                "total_requests": 0,
                "avg_processing_time_ms": 0,
                "status_codes": {},
                "methods": {},
                "paths": {}
            }
        
        logs = list(self.logs)
        total_requests = len(logs)
        
        # Calculate average processing time
        avg_processing_time = sum(log.processing_time_ms for log in logs) / total_requests
        
        # Count status codes
        status_codes = {}
        for log in logs:
            status_codes[log.response_status] = status_codes.get(log.response_status, 0) + 1
        
        # Count methods
        methods = {}
        for log in logs:
            methods[log.method] = methods.get(log.method, 0) + 1
        
        # Count paths
        paths = {}
        for log in logs:
            paths[log.path] = paths.get(log.path, 0) + 1
        
        return {
            "total_requests": total_requests,
            "avg_processing_time_ms": round(avg_processing_time, 2),
            "status_codes": status_codes,
            "methods": methods,
            "paths": dict(sorted(paths.items(), key=lambda x: x[1], reverse=True)[:10])  # Top 10 paths
        }
    
    def clear_logs(self) -> int:
        """Clear all logs and return the number of logs that were cleared"""
        count = len(self.logs)
        self.logs.clear()
        self._request_counter = 0
        logger.info(f"Cleared {count} request logs")
        return count
    
    def _filter_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Filter out sensitive headers from logging"""
        sensitive_headers = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token', 
            'x-access-token', 'x-csrf-token', 'x-session-id'
        }
        
        filtered = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                filtered[key] = "[REDACTED]"
            else:
                filtered[key] = value
        
        return filtered
    
    def _truncate_body(self, body: Optional[str], max_length: int = 10000) -> Optional[str]:
        """Truncate request/response bodies if they're too long"""
        if body is None:
            return None
        
        if len(body) <= max_length:
            return body
        
        return body[:max_length] + f"... [TRUNCATED - Original length: {len(body)} chars]"

# Global instance
request_logger = RequestLogger()