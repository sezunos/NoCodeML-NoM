import db
import time
import os
from utils.lru_session_datasets import lru_session_datasets


def garbage_datasets_collector(kill_time: float, sleep_time: float):
    while True:
        threshold = time.time() - kill_time
        get_candidates_query = """
            SELECT id, path_to_file
            FROM session_datasets
            WHERE last_action_time <= (?)
        """
        candidates = db._execute(get_candidates_query, (threshold,))[0]
        candidates_ids = [candidate[0] for candidate in candidates]

        lru_session_datasets._clear_cache(candidates_ids)

        deleted_paths = []
        for candidate in candidates:
            os.remove(candidate[1])
            deleted_paths.append(candidate[1])

        delete_query = f"""
            DELETE
            FROM session_datasets
            WHERE path_to_file in ({', '.join('?' for i in range(len(deleted_paths)))})
        """
        db._execute(delete_query, (*deleted_paths,))
        time.sleep(sleep_time)