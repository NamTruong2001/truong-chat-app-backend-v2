from fastapi import APIRouter


class TestRouter(APIRouter):
    def __init__(self, prefix: str):
        super().__init__(prefix=prefix)
        # self.prefix = prefix
        self.add_api_route("/test", self.test, methods=["GET"])

    async def test(self):
        return "test APIRouter"