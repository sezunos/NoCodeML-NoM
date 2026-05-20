from db import db
from collections import OrderedDict


max_items = 50

class lru_session_datasets_cls:
    def __init__(self, max_items: int):
        self.max_items = max_items
        self.cache = OrderedDict()
    
    def _get_dataset_from_fs(self, id: int):
        with open(db.get_session_dataset_data(id)[2], 'r') as file:
            dataset = file.read()
        return dataset
    
    def _with_path(self, path_to_file: str):
        with open(path_to_file, 'r') as file:
            dataset = file.read()
        return dataset

    def get_dataset(self, id: int):
        if id in self.cache:
            self.cache.move_to_end(id, last=True)
            return self.cache[id]
        
        if len(self.cache) >= self.max_items:
            self.cache.popitem(last=False)
        
        self.cache[id] = self._get_dataset_from_fs(id)
        return self.cache[id]
    
lru_session_datasets = lru_session_datasets_cls(max_items)