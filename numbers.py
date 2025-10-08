from typing import Dict, Set, Optional, List, Tuple

def _assign_numbers_with_constraints(
    adj: Dict[int, Set[int]],
    inventory_init: Dict[int, int],
    hot_groups: List[Set[int]],  # e.g. [{6,8}, {2,12}]
    no_equal_adjacent: bool = False,
    precolored: Optional[Dict[int, int]] = None,
) -> Optional[Dict[int, int]]:
    """
    Inventory-aware numbering with generalized adjacency rules:
      - For each group G in hot_groups, no edge may have (x in G) adjacent to (y in G).
      - If no_equal_adjacent=True, also forbid x == y on an edge.
      - Duplicates otherwise are allowed if not forbidden by the above.
    Returns {vertex -> number} or None.
    """
    nums = sorted(inventory_init.keys())
    inv = dict(inventory_init)
    assign: Dict[int, Optional[int]] = {v: None for v in adj}
    deg = {v: len(adj[v]) for v in adj}

    # fast lookup: for any number x, which groups contain it?
    groups_by_num: Dict[int, List[int]] = {}
    for gi, G in enumerate(hot_groups):
        for x in G:
            groups_by_num.setdefault(x, []).append(gi)

    def conflicts(x: int, y: int) -> bool:
        """Return True if placing x next to y is forbidden."""
        if y is None:
            return False
        if no_equal_adjacent and x == y:
            return True
        # share any hot-group?
        if x in groups_by_num and y in groups_by_num:
            gx = set(groups_by_num[x])
            gy = set(groups_by_num[y])
            if gx & gy:
                return True
        return False

    def domain(v: int) -> List[int]:
        if assign[v] is not None:
            return [assign[v]]
        neigh_vals = [assign[u] for u in adj[v] if assign[u] is not None]
        out = []
        for x in nums:
            if inv.get(x, 0) <= 0:
                continue
            if any(conflicts(x, y) for y in neigh_vals):
                continue
            out.append(x)
        return out

    def do(v: int, x: int):
        assign[v] = x
        inv[x] -= 1

    def undo(v: int, x: int):
        assign[v] = None
        inv[x] += 1

    def pick_vertex() -> int:
        """MRV (smallest domain), tie-break by higher degree."""
        cand = [v for v in adj if assign[v] is None]
        # compute domains once for the key
        def key(v):
            d = domain(v)
            return (len(d), -deg[v])
        return min(cand, key=key)

    def hall_checks() -> bool:
        # non-empty domain & inventory sanity
        for v in adj:
            if assign[v] is None and not domain(v):
                return False
        if any(c < 0 for c in inv.values()):
            return False
        # counts must match
        rem_vertices = sum(1 for v in adj if assign[v] is None)
        rem_pieces = sum(inv.values())
        if rem_vertices != rem_pieces:
            return False
        # per-number Hall: enough candidate spots for each remaining count
        for x, need in inv.items():
            if need == 0:
                continue
            pot = sum(1 for v in adj if assign[v] is None and x in domain(v))
            if pot < need:
                return False
        return True

    # precolored
    precolored = precolored or {}
    for v, x in precolored.items():
        if v not in adj:
            continue
        if inv.get(x, 0) <= 0:
            return None
        # check local consistency before placing
        if any(conflicts(x, assign[u]) for u in adj[v] if assign[u] is not None):
            return None
        do(v, x)
    if not hall_checks():
        return None

    def search() -> bool:
        if all(assign[v] is not None for v in adj):
            return True
        v = pick_vertex()
        dom = domain(v)
        # try scarcer numbers first
        dom.sort(key=lambda x: (inv[x], x))
        for x in dom:
            do(v, x)
            if hall_checks() and search():
                return True
            undo(v, x)
        return False

    return {v: assign[v] for v in adj} if search() else None
