class Voter:
    # someone casting a vote
    def __init__(self, name: str, ranking: list):
        self.name = name
        self.ranking = ranking

    def prefers_over(self, route1, route2) -> bool:
        # whether this voter prefers route1 over route2
        if route1 not in self.ranking:
            return False
        if route2 not in self.ranking:
            return True
        return self.ranking.index(route1) < self.ranking.index(route2)
