from flask import Flask, jsonify, request
from classes import Map
from Maker import randomizeBoard, noNumberPairs, rerandomizeNumbersUntilNoPairs
import json

app = Flask(__name__)

def map_to_dict(map_obj):
    """Convert Map object to dictionary for JSON serialization"""
    tiles_data = []
    for tile in map_obj.tiles:
        if tile is not None:
            tile_data = {
                "number": tile.number,
                "resource": tile.resource,
                "coordinates": tile.coordinates,
                "adjacent": {
                    "TL": tile.adjacent.TL.coordinates if tile.adjacent.TL else None,
                    "TR": tile.adjacent.TR.coordinates if tile.adjacent.TR else None,
                    "R": tile.adjacent.R.coordinates if tile.adjacent.R else None,
                    "BR": tile.adjacent.BR.coordinates if tile.adjacent.BR else None,
                    "BL": tile.adjacent.BL.coordinates if tile.adjacent.BL else None,
                    "L": tile.adjacent.L.coordinates if tile.adjacent.L else None
                }
            }
            tiles_data.append(tile_data)
        else:
            tiles_data.append(None)
    
    return {
        "tiles": tiles_data,
        "coordinates": map_obj.coordinates,
        "resources": map_obj.resources,
        "numbers": map_obj.numbers
    }

@app.route('/')
def home():
    return jsonify({
        "message": "Catan Map Maker API",
        "endpoints": {
            "/generate": "Generate a random Catan map",
            "/generate-no-pairs": "Generate a map with no adjacent number pairs (6,8)",
            "/health": "Health check endpoint"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/generate', methods=['GET', 'POST'])
def generate_map():
    """Generate a basic random Catan map"""
    try:
        map_obj = Map()
        map_obj = randomizeBoard(map_obj)
        
        return jsonify({
            "success": True,
            "map": map_to_dict(map_obj)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/generate-no-pairs', methods=['GET', 'POST'])
def generate_map_no_pairs():
    """Generate a Catan map with no adjacent number pairs (6,8)"""
    try:
        # Get pairs from query parameters or use default
        pairs = request.args.get('pairs', '6,8').split(',')
        pairs = [int(p.strip()) for p in pairs]
        
        map_obj = Map()
        map_obj = randomizeBoard(map_obj)
        map_obj = noNumberPairs(map_obj, pairs)
        map_obj = rerandomizeNumbersUntilNoPairs(map_obj, pairs)
        
        return jsonify({
            "success": True,
            "map": map_to_dict(map_obj),
            "pairs_avoided": pairs
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/generate-custom', methods=['POST'])
def generate_custom_map():
    """Generate a map with custom parameters"""
    try:
        data = request.get_json() or {}
        pairs = data.get('pairs', [6, 8])
        max_attempts = data.get('max_attempts', 100)
        
        map_obj = Map()
        map_obj = randomizeBoard(map_obj)
        map_obj = noNumberPairs(map_obj, pairs)
        map_obj = rerandomizeNumbersUntilNoPairs(map_obj, pairs, max_attempts)
        
        return jsonify({
            "success": True,
            "map": map_to_dict(map_obj),
            "pairs_avoided": pairs,
            "max_attempts": max_attempts
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
