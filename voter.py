from typing import List


class Voter:
    # someone casting a vote
    def __init__(self, name: str, ranking: List[str]):
        self.name = name
        self.ranking = ranking

    def prefers_over(self, route1: str, route2: str) -> bool:
        # whether this voter prefers route1 over route2
        if route1 not in self.ranking:
            return False
        if route2 not in self.ranking:
            return True
        return self.ranking.index(route1) < self.ranking.index(route2)
