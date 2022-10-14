import threading

from grab_opencv import record


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


if __name__ == "__main__":

    while True:
        record()
