from flask import Blueprint, request
import time
import json

# create a blueprint instance
api_bp = Blueprint('api_bp', __name__)

# Handle Request (Non-DB)
@api_bp.route('/api', methods=['GET', 'POST'])
async def handle_request():
    text = str(request.args.get('input'))  # ?input=a
    character_count = len(text)
    data_set = {'input': text, 'timestamp': time.time(), 'character_count': character_count}
    json_dump = json.dumps(data_set)
    return json_dump
    
