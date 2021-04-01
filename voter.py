class Voter:
    # iemand die stemt
    def __init__(self, name: str, ranking: list):
        self.name = name
        self.ranking = ranking

    def from_file(self, filename: str):
        # leest shit uit csv bestand en maakt een voter aan
        pass
