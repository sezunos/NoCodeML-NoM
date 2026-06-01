import time
from collections import OrderedDict

import pandas as pd

from db import db


max_items = 50

class lru_session_datasets_cls:
    def __init__(self, max_items: int):
        self.max_items = max_items
        self.cache = OrderedDict()

    def _set_dataset(self, dataset_id, path_to_file: str):
        dataset = pd.read_csv(path_to_file)

        if len(self.cache) >= self.max_items:
            self.cache.popitem(last=False)
        
        self._update_dataset_la_time(dataset_id)
        self.cache[dataset_id] = dataset
        return self.cache[dataset_id]

    def _clear_cache(self, dataset_ids: list | tuple):
        for dataset_id in dataset_ids:
            self.cache.pop(dataset_id, None)
    
    def _get_dataset_from_fs(self, dataset_id: int):
        data = db.get_session_dataset_data(dataset_id)
        if data is None:
            return None

        path_to_file = data[2]
        return pd.read_csv(path_to_file)
    
    def _update_dataset_la_time(self, dataset_id: int):
        if dataset_id not in self.cache: return
        query = """
            UPDATE session_datasets
            SET last_action_time = (?)
            WHERE id = (?)
        """
        db._execute(query, (time.time(), dataset_id))

    def get_dataset(self, dataset_id: int):
        if dataset_id is None:
            return None

        if dataset_id in self.cache:
            self._update_dataset_la_time(dataset_id)
            self.cache.move_to_end(dataset_id, last=True)
            return self.cache[dataset_id]
        
        session_dataset = self._get_dataset_from_fs(dataset_id)
        if session_dataset is None:
            return None
        
        self._update_dataset_la_time(dataset_id)

        if len(self.cache) >= self.max_items:
            self.cache.popitem(last=False)

        self.cache[dataset_id] = session_dataset
        return self.cache[dataset_id]
    
    def update_dataset(self, dataset_id: int, dataset):
        data = db.get_session_dataset_data(dataset_id)
        path_to_file = data[2]
        dataset.to_csv(path_to_file, index=False)
        if dataset_id in self.cache:
            self.cache[dataset_id] = dataset

lru_session_datasets = lru_session_datasets_cls(max_items)