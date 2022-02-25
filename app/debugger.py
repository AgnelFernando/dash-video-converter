# debugger.py
from os import getenv

def initialize_celery_worker_debugger_if_needed():
    if getenv("DEBUGGER") == "True":
        import multiprocessing

        if multiprocessing.current_process().pid > 1:
            import debugpy

            debugpy.listen(("0.0.0.0", 10001))
            print("⏳ VS Code debugger can now be attached for celery worker, press F5 in VS Code ⏳", flush=True)
            debugpy.wait_for_client()
            print("🎉 VS Code debugger attached for celery worker, enjoy debugging 🎉", flush=True)

def initialize_fast_api_server_debugger_if_needed():
    if getenv("DEBUGGER") == "True":
        import multiprocessing

        if multiprocessing.current_process().pid > 1:
            import debugpy

            debugpy.listen(("0.0.0.0", 10002))
            print("⏳ VS Code debugger can now be attached for fast api, press F5 in VS Code ⏳", flush=True)
            debugpy.wait_for_client()
            print("🎉 VS Code debugger attached for fast api, enjoy debugging 🎉", flush=True)            