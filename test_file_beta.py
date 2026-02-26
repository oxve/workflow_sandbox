class BetaProcessor:
    def __init__(self, items):
        self.items = items
        self.processed = []

    def run_stage_one(self):
<<<<<<< HEAD
        # Stage one for android
        for i in self.items:
            # Different base
            self.processed.append(i + 50)
=======
        # Stage one advanced
        for val in self.items:
            # Different logic base
            self.processed.append(val + 100)
>>>>>>> 5f3a124 (Introduce complex changes for conflict trigger (#24))

    def run_stage_two(self):
        # Stage two
        for i in range(len(self.processed)):
            self.processed[i] -= 2

    def get_results(self):
        return self.processed

if __name__ == "__main__":
    processor = BetaProcessor([1, 2, 3])
    processor.run_stage_one()
    processor.run_stage_two()
    print(processor.get_results())
