import json
import os

class Persistencia:
    @staticmethod
    def load(filename: str) -> dict[str, list[str]]:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                dic: dict[str, list[str]] = json.loads(file.read())
                assert type(dic) is dict
                return dic
        else:
            return dict()

    @staticmethod
    def store(filename: str, dic: dict[str, list[str]]) -> None:
        with open(filename, 'w') as file:
            file.write(json.dumps(dic))
