#!/usr/bin/env python3
"""
Native Messaging Host for Disk Space Checker Extension

This script communicates with the Chrome extension via native messaging.
It only runs when the extension needs to check disk space, making it
more efficient than a constantly-running Flask server.

Communication protocol:
- Reads JSON messages from stdin (4-byte length prefix + JSON)
- Writes JSON responses to stdout (4-byte length prefix + JSON)
- Exits after processing requests
"""

import sys
import json
import struct
import psutil
import os

# Configuration
DEFAULT_MIN_SIZE = 1 * 1000000000     # 1 GB (decimal)
RESERVED_SPACE   = 5 * 1000000000     # 5 GB (decimal)
   # Always keep 5 GB free

def bytes_to_gb(b):
    """Convert bytes to gigabytes"""
    return b / 1000000000

def normalize_path(path):
    """Normalize and validate a file path"""
    if not path or path == '':
        return os.path.expanduser('~') or '/'
    
    # If it's a file path, get its directory
    if os.path.isfile(path):
        path = os.path.dirname(path)
    
    # Resolve the path to get the actual mount point
    try:
        return os.path.realpath(path)
    except (OSError, ValueError):
        return os.path.expanduser('~') or '/'

def get_disk_info(path):
    """Get current disk space information"""
    try:
        resolved_path = normalize_path(path)
        usage = psutil.disk_usage(resolved_path)
        
        free = usage.free
        total = usage.total
        used = usage.used
        percent_used = (used / total) * 100 if total > 0 else 0
        
        return {
            "ok": True,
            "path": resolved_path,
            "total": total,
            "used": used,
            "free": free,
            "percent_used": round(percent_used, 2),
            "total_gb": round(bytes_to_gb(total), 2),
            "used_gb": round(bytes_to_gb(used), 2),
            "free_gb": round(bytes_to_gb(free), 2)
        }
    except (FileNotFoundError, PermissionError, OSError) as e:
        return {
            "ok": False,
            "error": f"Path '{path}' not accessible: {str(e)}"
        }

def check_space(size_bytes, path):
    """Check if there's enough space for a download"""
    try:
        # Validate size
        try:
            size = int(size_bytes) if size_bytes and int(size_bytes) > 0 else DEFAULT_MIN_SIZE
        except (ValueError, TypeError):
            size = DEFAULT_MIN_SIZE
        
        # Calculate required space
        required_space = size + RESERVED_SPACE
        
        # Get disk usage
        resolved_path = normalize_path(path)
        usage = psutil.disk_usage(resolved_path)
        
        free = usage.free
        total = usage.total
        used = usage.used
        
        # Check if enough space
        if free < required_space:
            msg = (f"Not enough space. Free: {bytes_to_gb(free):.2f} GB, "
            f"Required: {bytes_to_gb(required_space):.2f} GB")
            return {
                "ok": False,
                "total": total,
                "used": used,
                "free": free,
                "reserved": RESERVED_SPACE,
                "error": msg
            }
        else:
            return {
                "ok": True,
                "total": total,
                "used": used,
                "free": free,
                "reserved": RESERVED_SPACE
            }
    except (FileNotFoundError, PermissionError, OSError) as e:
        return {
            "ok": False,
            "error": f"Path '{path}' not accessible: {str(e)}"
        }

def send_message(message):
    """Send a JSON message to stdout with length prefix"""
    message_json = json.dumps(message)
    message_bytes = message_json.encode('utf-8')
    length = struct.pack('<I', len(message_bytes))
    sys.stdout.buffer.write(length + message_bytes)
    sys.stdout.buffer.flush()

def read_message():
    """Read a JSON message from stdin with length prefix"""
    # Read the 4-byte length prefix
    length_bytes = sys.stdin.buffer.read(4)
    if len(length_bytes) == 0:
        return None
    
    # Unpack the length (unsigned 32-bit integer, native byte order)
    length = struct.unpack('<I', length_bytes)[0]
    
    # Read the JSON message
    message_bytes = sys.stdin.buffer.read(length)
    message_json = message_bytes.decode('utf-8')
    
    return json.loads(message_json)

def main():
    """Main message processing loop"""
    try:
        while True:
            # Read message from extension
            message = read_message()
            if message is None:
                break
            
            # Process the message
            command = message.get('command')
            
            if command == 'info':
                # Get disk info
                path = message.get('path', '/')
                response = get_disk_info(path)
                send_message(response)
            
            elif command == 'check':
                # Check space
                size = message.get('size')
                path = message.get('path', '/')
                response = check_space(size, path)
                send_message(response)
            
            elif command == 'ping':
                # Health check
                send_message({"ok": True, "message": "pong"})
            
            else:
                send_message({
                    "ok": False,
                    "error": f"Unknown command: {command}"
                })
    
    except Exception as e:
        # Send error response
        send_message({
            "ok": False,
            "error": f"Internal error: {str(e)}"
        })
        sys.exit(1)

if __name__ == '__main__':
    main()

