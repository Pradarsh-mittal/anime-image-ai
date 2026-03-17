import os
import re
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import MessageMediaPhoto
from telethon.errors import UserAlreadyParticipantError
from openai import OpenAI


API_ID =           
API_HASH = ""    
INVITE_LINK = ""  

OPENAI_API_KEY = ""

DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

ai_client = OpenAI(api_key=OPENAI_API_KEY)

def clean_prompt_with_ai(raw_text: str) -> str:
    """
    Cleans Telegram caption into training-ready prompt
    """
    if not raw_text.strip():
        return ""

    response = ai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a dataset cleaning AI.\n"
                    "Convert raw Telegram captions into clean anime training prompts.\n"
                    "Rules:\n"
                    "- Remove emojis, timestamps, resolutions, metadata\n"
                    "- Keep subject, action, scene, mood, anime style\n"
                    "- Use comma-separated tags\n"
                    "- Do not add new concepts\n"
                    "- Output ONLY the cleaned prompt text"
                )
            },
            {
                "role": "user",
                "content": raw_text
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


client = TelegramClient("session", API_ID, API_HASH)


async def download_dataset():
    invite_hash = INVITE_LINK.split("+")[1]

    try:
        await client(ImportChatInviteRequest(invite_hash))
        print("Joined private channel")
    except UserAlreadyParticipantError:
        print("Already a member of the channel")


    channel = await client.get_entity(INVITE_LINK)

    count = 0

    # 3️⃣ Read messages using ENTITY (not invite hash)
    async for msg in client.iter_messages(channel):
        if msg.media and isinstance(msg.media, MessageMediaPhoto):
            count += 1

            image_path = os.path.join(DATASET_DIR, f"img_{count:04d}.jpg")
            text_path = os.path.join(DATASET_DIR, f"img_{count:04d}.txt")

            await msg.download_media(image_path)

            cleaned_prompt = clean_prompt_with_ai(msg.text or "")

            with open(text_path, "w", encoding="utf-8") as f:
                f.write(cleaned_prompt)

            print(f"[✔] Saved img_{count:04d}")

    print(f"\n🎉 DONE: {count} images processed")


with client:
    client.loop.run_until_complete(download_dataset())
