from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import time

from manager import ThreadPoolManager


path: Path = Path(__file__).parent
shared_file_path = f"{path}/shared_file.txt"


pool = ThreadPoolManager(min_threads=5, max_threads=100)


def process_task(message):
    """Simulate processing of the message with thread-safe file writing."""
    time.sleep(5)      
    # Acquire the lock before writing to the shared file
    with pool.lock:
        with open(shared_file_path, "a") as f:
            f.write(f"Processed message: {message}\n")
    print(f"Processed message: {message}")


class Message(BaseModel):
    message: str

app = FastAPI()

@app.post("/messages")
async def push_message(message: Message, background_tasks: BackgroundTasks):
    """Handle POST request to process a message."""
    background_tasks.add_task(pool.add_task, process_task, message.message)
    return {"status": "Message received"}


@app.get("/statistics")
async def get_statistics():
    """Return the current statistics (active instances and total invocations)."""
    stats = pool.get_statistics()
    return stats
