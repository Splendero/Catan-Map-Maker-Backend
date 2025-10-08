from flask import Flask, jsonify, request
from flask_cors import CORS
from classes import Map
from Maker import randomizeBoard

app = Flask(__name__)
CORS(app, origins=[
    'http://localhost:3000', 
    'http://127.0.0.1:3000',
    'https://catan-map-maker-frontend.vercel.app'  # Add your actual frontend domain
])


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
    if not constraints:
        return map_obj

    if "noResources" in constraints:
        import random
        random.shuffle(map_obj.resources)
        map_obj.create_from_scratch(assign_numbers=False)
    else:
        # When using randomizeBoard, we need to set up coord_to_index
        # for assign_numbers_with_constraints to work
        map_obj.coord_to_index = {tile.coordinates: i for i, tile in enumerate(map_obj.tiles) if tile}
    
    # Handle pairs - collect hot groups
    hot_groups = []
    if "eightSix" in constraints:
        hot_groups.append({6, 8})
    if "twoTwelve" in constraints:
        hot_groups.append({2, 12})
    
    # Apply number constraints if any were specified
    if hot_groups:
        no_equal_adjacent = "noTwoNumber" in constraints
        map_obj.assign_numbers_with_constraints(
            hot_groups=hot_groups,
            no_equal_adjacent=no_equal_adjacent
        )
    elif "noTwoNumber" in constraints:
        # Only noTwoNumber constraint, no hot pairs
        map_obj.assign_numbers_with_constraints(
            hot_groups=[],
            no_equal_adjacent=True
        )
    
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

# Add this for Vercel compatibility
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
else:
    # This is what Vercel will use
    application = app