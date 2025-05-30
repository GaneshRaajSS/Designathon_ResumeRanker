class RankingService:
    def __init__(self, min_threshold=30):
        self.min_threshold = min_threshold

    def rank_profiles(self, similarities):
        return sorted(
            [s for s in similarities if s['score'] >= self.min_threshold],
            key=lambda x: x['score'],
            reverse=True
        )
