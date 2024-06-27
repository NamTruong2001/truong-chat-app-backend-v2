from fastapi import APIRouter
from pydantic import BaseModel


class TestRouter(APIRouter):
    def __init__(self, prefix: str):
        super().__init__(prefix=prefix)
        # self.prefix = prefix
        self.add_api_route("/test", self.test, methods=["GET"])

    async def test(self):
        class Laugh(BaseModel):
            message: str

        class Hehe(Laugh):
            how: str = "hehe"

        class Haha(Laugh):
            hic: str = "haha"

        laugh = Laugh(message="laugh")
        laugh2 = Hehe(message="cuoi hehe")
        laugh3 = Haha(message="cuoi haha")

        return [laugh, laugh2, laugh3]
