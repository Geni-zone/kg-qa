import time

def exec_retry(func : function, max_retries : int, task_name : str):
    for i in range(max_retries):
        try:
            result = func()
            return result
        except Exception as e:
            print(f"While completing, {task_name}, Error occurred: {e}")
            print(f"Retrying in 1 second... ({i+1}/{max_retries})")
            time.sleep(1)
    raise Exception(f"{task_name} failed after {max_retries} retries")
