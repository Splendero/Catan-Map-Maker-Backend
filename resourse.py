from typing import Dict, Set, Optional, List, Tuple
import random

# ---- DSATUR + global inventory (multiset of colors) ----

def _color_with_inventory(
    adj: Dict[int, Set[int]],
    inventory_init: Dict[str, int],
    precolored: Optional[Dict[int, str]] = None,
) -> Optional[Dict[int, str]]:

    colors: List[str] = list(inventory_init.keys())
    inventory = dict(inventory_init)
    color: Dict[int, Optional[str]] = {v: None for v in adj}
    nbh_used: Dict[int, Set[str]] = {v: set() for v in adj}
    degree = {v: len(adj[v]) for v in adj}

    # forbid self-loops (shouldn't exist)
    for v in adj:
        if v in adj[v]:
            raise ValueError(f"Self-loop at vertex {v}")

    # helpers
    def domain(v: int) -> List[str]:
        if color[v] is not None:
            return [color[v]]
        forbidden = nbh_used[v]
        return [c for c in colors if c not in forbidden and inventory[c] > 0]

    def assign(v: int, c: str):
        color[v] = c
        inventory[c] -= 1
        for u in adj[v]:
            nbh_used[u].add(c)

    def unassign(v: int, c: str):
        color[v] = None
        inventory[c] += 1
        for u in adj[v]:
            nbh_used[u].discard(c)

    def pick_vertex() -> int:
        # DSATUR: highest saturation, tie by degree, then MRV (smallest domain)
        candidates = [v for v in adj if color[v] is None]
        # Add random tie-breaker
        return max(
            candidates,
            key=lambda v: (len(nbh_used[v]), degree[v], -len(domain(v)), random.random())
        )

    def forward_checks_ok() -> bool:
        # every uncolored vertex keeps a possible color
        for u in adj:
            if color[u] is None and not domain(u):
                return False
        # inventory never negative
        if any(inventory[c] < 0 for c in colors):
            return False
        # Hall-style pigeonhole: enough candidate spots for each color
        for c in colors:
            need = inventory[c]
            if need == 0:
                continue
            potential = sum(1 for u in adj if color[u] is None and c not in nbh_used[u])
            if potential < need:
                return False
        # remaining pieces must equal remaining vertices
        remaining_vertices = sum(1 for v in adj if color[v] is None)
        remaining_pieces = sum(inventory.values())
        return remaining_vertices == remaining_pieces

    # apply precoloring if provided
    precolored = precolored or {}
    for v, c in precolored.items():
        if c not in inventory:
            raise ValueError(f"Unknown color in precoloring: {c}")
        assign(v, c)
    if not forward_checks_ok():
        return None

    # search
    def search() -> bool:
        if all(color[v] is not None for v in adj):
            return True
        v = pick_vertex()
        dom = domain(v)
        # Add randomization: shuffle then sort by scarcity (with some randomness)
        random.shuffle(dom)  # Add this line
        dom.sort(key=lambda c: (inventory[c], random.random()))  # Add random tie-breaker
        for c in dom:
            assign(v, c)
            if forward_checks_ok() and search():
                return True
            unassign(v, c)
        return False

    if search():
        return {v: color[v] for v in adj}
    return None