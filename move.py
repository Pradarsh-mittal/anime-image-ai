
import asyncio
import os
import time
from telethon import TelegramClient


API_ID =          
API_HASH = "" 
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

client = TelegramClient("session", API_ID, API_HASH)


start_time = None

def progress(current, total):
    global start_time

    if start_time is None:
        start_time = time.time()

    elapsed = time.time() - start_time
    speed = current / elapsed if elapsed > 0 else 0

    percent = (current / total) * 100

    downloaded_mb = current / (1024 * 1024)
    total_mb = total / (1024 * 1024)
    speed_mb = speed / (1024 * 1024)

    print(
        f"\rDownloading: {percent:.2f}% | "
        f"{downloaded_mb:.2f}MB / {total_mb:.2f}MB | "
        f"Speed: {speed_mb:.2f} MB/s",
        end=""
    )


async def download_movie():

    async for msg in client.iter_messages("me"):

        if msg.video or msg.document:

            filename = msg.file.name or "movie.mkv"
            filepath = os.path.join(DOWNLOAD_DIR, filename)

            print("Movie found:", filename)
            print("Starting download...\n")

            await msg.download_media(
                file=filepath,
                progress_callback=progress
            )

            print("\n\nDownload complete:", filepath)
            break


with client:
    client.loop.run_until_complete(download_movie())
