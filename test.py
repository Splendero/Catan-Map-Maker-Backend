from classes import Map
from Maker import randomizeBoard
from app import apply_constraints

def check_no_adjacent_pairs(map_obj, pairs):
    """Check if any adjacent tiles have numbers in the pairs list"""
    violations = []
    for tile in map_obj.tiles:
        if tile is not None and tile.number in pairs:
            for adj in tile.adjacent.to_list_no_none():
                # Handle both Tile objects and integers
                adj_number = adj.number if hasattr(adj, 'number') else map_obj.tiles[adj].number if isinstance(adj, int) else None
                if adj_number in pairs:
                    violations.append(f"Found adjacent {tile.number} and {adj_number} at {tile.coordinates}")
    if violations:
        return False, "\n    ".join(violations)
    return True, "OK"

def check_no_adjacent_same_number(map_obj):
    """Check if any adjacent tiles have the same number"""
    violations = []
    for tile in map_obj.tiles:
        if tile is not None and tile.number is not None and tile.number != 0:
            for adj in tile.adjacent.to_list_no_none():
                adj_number = adj.number if hasattr(adj, 'number') else map_obj.tiles[adj].number if isinstance(adj, int) else None
                if adj_number == tile.number and adj_number != 0:
                    violations.append(f"Found adjacent same number {tile.number} at {tile.coordinates}")
    if violations:
        return False, "\n    ".join(violations)
    return True, "OK"

def check_no_adjacent_same_resource(map_obj):
    """Check if any adjacent tiles have the same resource"""
    violations = []
    for tile in map_obj.tiles:
        if tile is not None and tile.resource is not None:
            for adj in tile.adjacent.to_list_no_none():
                adj_resource = adj.resource if hasattr(adj, 'resource') else map_obj.tiles[adj].resource if isinstance(adj, int) else None
                if adj_resource == tile.resource:
                    violations.append(f"Found adjacent same resource {tile.resource} at {tile.coordinates}")
    if violations:
        return False, "\n    ".join(violations)
    return True, "OK"

def test_constraint(constraint_name, constraints_list, checks):
    """Test a specific constraint configuration"""
    print(f"\n{'='*80}")
    print(f"Testing: {constraint_name}")
    print(f"Constraints: {constraints_list}")
    print(f"{'='*80}")
    
    try:
        map_obj = Map()
        if "noResources" not in constraints_list:
            map_obj = randomizeBoard(map_obj)
        map_obj = apply_constraints(map_obj, constraints_list)
        
        # Print the map
        map_obj.printMap()
        
        print("\nValidation Results:")
        print("-" * 80)
        
        # Run checks
        all_passed = True
        for check_name, check_func, check_args in checks:
            passed, message = check_func(map_obj, *check_args) if check_args else check_func(map_obj)
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {check_name}")
            if not passed:
                print(f"    {message}")
                all_passed = False
        
        if not checks:
            print("✓ Map generated successfully (no specific constraints to check)")
            all_passed = True
        
        return all_passed
        
    except Exception as e:
        print(f"✗ FAIL: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*80)
    print("CATAN MAP MAKER - CONSTRAINT TESTING")
    print("="*80)
    
    results = []
    
    # Test 1: Basic generation (no constraints)
    print("\n\n" + "▼" * 80)
    results.append(("Basic (no constraints)", test_constraint(
        "Basic generation (no constraints)",
        [],
        []
    )))
    
    # Test 2: eightSix constraint only
    print("\n\n" + "▼" * 80)
    results.append(("eightSix only", test_constraint(
        "No adjacent 6-8 pairs",
        ["eightSix"],
        [("No adjacent 6-8", check_no_adjacent_pairs, ([6, 8],))]
    )))
    
    # Test 3: twoTwelve constraint only
    print("\n\n" + "▼" * 80)
    results.append(("twoTwelve only", test_constraint(
        "No adjacent 2-12 pairs",
        ["twoTwelve"],
        [("No adjacent 2-12", check_no_adjacent_pairs, ([2, 12],))]
    )))
    
    # Test 4: Both hot constraints
    print("\n\n" + "▼" * 80)
    results.append(("eightSix + twoTwelve", test_constraint(
        "No adjacent 6-8 OR 2-12 pairs",
        ["eightSix", "twoTwelve"],
        [
            ("No adjacent 6-8", check_no_adjacent_pairs, ([6, 8],)),
            ("No adjacent 2-12", check_no_adjacent_pairs, ([2, 12],))
        ]
    )))
    
    # Test 5: noTwoNumber constraint
    print("\n\n" + "▼" * 80)
    results.append(("noTwoNumber only", test_constraint(
        "No adjacent same numbers",
        ["noTwoNumber"],
        [("No adjacent same number", check_no_adjacent_same_number, ())]
    )))
    
    # Test 6: noResources constraint
    print("\n\n" + "▼" * 80)
    results.append(("noResources only", test_constraint(
        "No adjacent same resources",
        ["noResources"],
        [("No adjacent same resource", check_no_adjacent_same_resource, ())]
    )))
    
    # Test 7: noResources + eightSix
    print("\n\n" + "▼" * 80)
    results.append(("noResources + eightSix", test_constraint(
        "No adjacent same resources + no adjacent 6-8",
        ["noResources", "eightSix"],
        [
            ("No adjacent same resource", check_no_adjacent_same_resource, ()),
            ("No adjacent 6-8", check_no_adjacent_pairs, ([6, 8],))
        ]
    )))
    
    # Test 8: All constraints combined
    print("\n\n" + "▼" * 80)
    results.append(("All constraints", test_constraint(
        "All constraints combined",
        ["noResources", "eightSix", "twoTwelve", "noTwoNumber"],
        [
            ("No adjacent same resource", check_no_adjacent_same_resource, ()),
            ("No adjacent 6-8", check_no_adjacent_pairs, ([6, 8],)),
            ("No adjacent 2-12", check_no_adjacent_pairs, ([2, 12],)),
            ("No adjacent same number", check_no_adjacent_same_number, ())
        ]
    )))
    
    # Print summary
    print("\n\n" + "="*80)
    print("FINAL TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("="*80)

if __name__ == "__main__":
    main()