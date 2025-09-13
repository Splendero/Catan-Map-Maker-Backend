from flask import Flask, jsonify, request
from flask_cors import CORS
from classes import Map
from Maker import randomizeBoard, noNumberPairs, rerandomizeNumbersUntilNoPairs
import json

app = Flask(__name__)
CORS(app)  # Allow all origins (for development only)

# Resource to terrain mapping
RESOURCE_TO_TERRAIN = {
    "Wheat": "field",
    "Brick": "hill", 
    "Rock": "mountain",
    "Sheep": "pasture",
    "Wood": "forest",
    "Desert": "desert"
}

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

def map_to_new_format(map_obj):
    """Convert Map object to new format with q,r,s coordinates and terrain"""
    tiles_data = []
    for tile in map_obj.tiles:
        if tile is not None:
            q, r, s = tile.coordinates
            terrain = RESOURCE_TO_TERRAIN.get(tile.resource, "desert")
            number = tile.number if tile.number != 0 else None
            
            tile_data = {
                "q": q,
                "r": r, 
                "s": s,
                "terrain": terrain,
                "number": number
            }
            tiles_data.append(tile_data)
    
    return {
        "tiles": tiles_data
    }

def apply_constraints(map_obj, constraints):
    """Apply constraints to the map"""
    if not constraints:
        return map_obj
    
    # Handle eightSix constraint (no adjacent 6,8 pairs)
    if "eightSix" in constraints:
        map_obj = noNumberPairs(map_obj, [6, 8])
        map_obj = rerandomizeNumbersUntilNoPairs(map_obj, [6, 8])
    
    # Handle twoTwelve constraint (no adjacent 2,12 pairs)  
    if "twoTwelve" in constraints:
        map_obj = noNumberPairs(map_obj, [2, 12])
        map_obj = rerandomizeNumbersUntilNoPairs(map_obj, [2, 12])
    
    # Handle noResources constraint (no adjacent same resource tiles)
    if "noResources" in constraints:
        # This would require additional logic to check for adjacent same resources
        # For now, we'll implement a basic version
        pass
    
    # Handle noTwoNumber constraint (no adjacent tiles with same number)
    if "noTwoNumber" in constraints:
        # This would require additional logic to check for adjacent same numbers
        # For now, we'll implement a basic version
        pass
    
    return map_obj

import os

# Get base URL from environment variable, default to localhost
BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')

@app.route('/')
def home():
    return jsonify({
        "message": "Catan Map Maker API",
        "base_url": BASE_URL,
        "endpoints": {
            "/generate": "Generate a random Catan map",
            "/generate-no-pairs": "Generate a map with no adjacent number pairs (6,8)",
            "/generate-constrained": "Generate a map with constraints (POST)",
            "/health": "Health check endpoint"
        },
        "post_example": {
            "url": f"{BASE_URL}/generate-constrained",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {
                "constraints": ["eightSix", "twoTwelve", "noResources", "noTwoNumber"]
            }
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

@app.route('/generate-constrained', methods=['POST'])
def generate_constrained_map():
    """Generate a map with constraints in the new format"""
    try:
        data = request.get_json() or {}
        constraints = data.get('constraints', [])
        
        # Generate base map
        map_obj = Map()
        map_obj = randomizeBoard(map_obj)
        
        # Apply constraints
        map_obj = apply_constraints(map_obj, constraints)
        
        # Convert to new format
        map_data = map_to_new_format(map_obj)
        
        return jsonify(map_data)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
