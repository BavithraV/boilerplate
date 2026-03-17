from app.repositories.sample_repository import SampleRepository


class SampleService:
    def __init__(self):
        self.repo = SampleRepository()

    def process(self, name: str):
        return self.repo.get_message(name)
