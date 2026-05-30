import time
import os

from db import db


def garbage_temp_models_collector(kill_time: float):
    try:
        threshold = time.time() - kill_time
        get_candidates_query = """
            SELECT id, path_to_file
            FROM models
            WHERE dataset_id IS NULL AND train_date <= (?)
        """
        candidates = db._execute(get_candidates_query, (threshold,))[0]
            
        deleted_paths = []
        for candidate in candidates:
            os.remove(candidate[1])
            deleted_paths.append(candidate[1])
            
        if deleted_paths:
            delete_query = f"""
                DELETE
                FROM models
                WHERE path_to_file in ({', '.join('?' for i in range(len(deleted_paths)))})
            """
            db._execute(delete_query, (*deleted_paths,))
    except:
        pass