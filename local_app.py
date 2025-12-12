from flask import Flask, jsonify, request
import psutil
import datetime
import socket
import os

app = Flask(__name__)

# Enable CORS for localhost requests
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Configuration
DEFAULT_MIN_SIZE = 1 * 1024**3          # 1 GB assumed if unknown
RESERVED_SPACE = 5 * 1024**3            # Always keep 5 GB free
PORT = 5000

@app.route('/info')
def get_disk_info():
    """Get current disk space information without checking a specific size"""
    path = request.args.get('path', '/')
    
    # Normalize the path
    if path and os.path.isfile(path):
        path = os.path.dirname(path)
    
    if not path or path == '':
        path = os.path.expanduser('~') or '/'
    
    try:
        resolved_path = os.path.realpath(path)
        usage = psutil.disk_usage(resolved_path)
    except (FileNotFoundError, PermissionError, OSError) as e:
        error_msg = f"Path '{path}' not accessible: {str(e)}"
        log(error_msg)
        return jsonify(ok=False, error=error_msg), 400
    
    free = usage.free
    total = usage.total
    used = usage.used
    percent_used = (used / total) * 100 if total > 0 else 0
    
    return jsonify(
        ok=True,
        path=resolved_path,
        total=total,
        used=used,
        free=free,
        percent_used=round(percent_used, 2),
        total_gb=round(bytes_to_gb(total), 2),
        used_gb=round(bytes_to_gb(used), 2),
        free_gb=round(bytes_to_gb(free), 2)
    )

@app.route('/check')
def check_space():
    # Optional parameters
    size_str = request.args.get('size')
    path = request.args.get('path', '/')

    # If size is known, use it, else fall back to default
    try:
        size = int(size_str) if size_str and int(size_str) > 0 else DEFAULT_MIN_SIZE
    except ValueError:
        size = DEFAULT_MIN_SIZE

    # Calculate required space: requested size + reserved buffer
    required_space = size + RESERVED_SPACE

    # Normalize the path - if it's a file path, get its directory
    if path and os.path.isfile(path):
        path = os.path.dirname(path)
    
    # If path is empty or invalid, use home directory or root
    if not path or path == '':
        path = os.path.expanduser('~') or '/'

    # Get disk usage for given path
    try:
        # Resolve the path to get the actual mount point
        resolved_path = os.path.realpath(path)
        usage = psutil.disk_usage(resolved_path)
    except (FileNotFoundError, PermissionError, OSError) as e:
        error_msg = f"Path '{path}' not accessible: {str(e)}"
        log(error_msg)
        return jsonify(ok=False, error=error_msg), 400

    free = usage.free
    total = usage.total
    used = usage.used

    # Log info
    log(f"Checked path: {path}")
    log(f"Total space: {bytes_to_gb(total):.2f} GB")
    log(f"Used space: {bytes_to_gb(used):.2f} GB")
    log(f"Free space: {bytes_to_gb(free):.2f} GB")
    log(f"Requested download size: {bytes_to_gb(size):.2f} GB")
    log(f"Required (including reserved): {bytes_to_gb(required_space):.2f} GB")

    # Compare
    if free < required_space:
        msg = (f" Not enough space. Free: {bytes_to_gb(free):.2f} GB, "
               f"Required: {bytes_to_gb(required_space):.2f} GB")
        log(msg)
        return jsonify(
            ok=False,
            total=total,
            used=used,
            free=free,
            reserved=RESERVED_SPACE,
            error=msg
        )
    else:
        msg = f" Enough space. Free: {bytes_to_gb(free):.2f} GB"
        log(msg)
        return jsonify(
            ok=True,
            total=total,
            used=used,
            free=free,
            reserved=RESERVED_SPACE
        )

def bytes_to_gb(b):
    return b / 1024**3

def log(msg):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    hostname = socket.gethostname()
    print(f"[{now}][{hostname}] {msg}")

if __name__ == "__main__":
    log(f"🚀 Starting local disk monitor on port {PORT}...")
    app.run(host='127.0.0.1', port=PORT)
