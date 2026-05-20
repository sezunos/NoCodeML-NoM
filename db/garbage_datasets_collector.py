import db
import time
import os


def garbage_datasets_collector(kill_time: float, sleep_time: float):
    while True:
        threshold = time.time() - kill_time
        get_candidates_query = """
            SELECT path_to_file
            FROM session_datasets
            WHERE last_action_time <= (?)
        """

        candidates = db._execute(get_candidates_query, (threshold,))[0]
        deleted_paths = []
        for path in candidates:
            os.remove(path[0])
            deleted_paths.append(path[0])

        delete_query = f"""
            DELETE
            FROM session_datasets
            WHERE path_to_file in ({', '.join('?' for i in range(len(deleted_paths)))})
        """
        db._execute(delete_query, (*deleted_paths,))
        time.sleep(sleep_time)