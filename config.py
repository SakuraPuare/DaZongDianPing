import pathlib
from typing import Dict

import yaml


class Config:
    def __init__(self, path: pathlib.Path = pathlib.Path('config.yaml')):
        self.config = self.load(path)

        for key, value in self.config.items():
            setattr(self, key, value)

    def load(self, path) -> Dict[str, str]:
        with open(path, 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        return self.config

    def get(self, key):
        return self.config[key]

    def __str__(self):
        # return all attributes
        return str(self.__dict__)


if __name__ == '__main__':
    cfg = Config()
    print(cfg)
