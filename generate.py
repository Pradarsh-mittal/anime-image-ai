import os
from openai import OpenAI

# ==============================
# CONFIG
# ==============================

OPENAI_API_KEY = ""
DATASET_DIR = "dataset"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = OpenAI(api_key=OPENAI_API_KEY)

# ==============================
# STEP 1: LOAD DATASET PROMPTS
# ==============================
def load_dataset_prompts(limit=200):
    prompts = []
    for file in os.listdir(DATASET_DIR):
        if file.endswith(".txt"):
            with open(os.path.join(DATASET_DIR, file), "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    prompts.append(text)
        if len(prompts) >= limit:
            break
    return prompts


# ==============================
# STEP 2: ANALYZE DATASET STYLE
# ==============================
def analyze_dataset_style(prompts):
    joined = "\n".join(prompts)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI that analyzes image dataset prompts.\n"
                    "Extract the common visual style, mood, themes, composition patterns.\n"
                    "Return a concise style description usable for image generation.\n"
                    "No explanations, only style summary."
                )
            },
            {
                "role": "user",
                "content": joined
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


# ==============================
# STEP 3: STYLE-AWARE PROMPT REWRITE
# ==============================
def rewrite_prompt(user_prompt, dataset_style):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI prompt engineer.\n"
                    "Rewrite the user prompt to match the dataset style.\n"
                    "Do NOT change the core idea.\n"
                    "Add style, mood, lighting, composition from dataset style.\n"
                    "Output ONLY the final prompt."
                )
            },
            {
                "role": "user",
                "content": f"""
DATASET STYLE:
{dataset_style}

USER PROMPT:
{user_prompt}
"""
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()


# ==============================
# STEP 4: IMAGE GENERATION
# ==============================
def generate_image(final_prompt):
    response = client.images.generate(
        model="gpt-image-1",
        prompt=final_prompt,
        size="1024x1024"
    )

    image_base64 = response.data[0].b64_json
    image_path = os.path.join(OUTPUT_DIR, "generated.png")

    with open(image_path, "wb") as f:
        f.write(__import__("base64").b64decode(image_base64))

    return image_path


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    print("📊 Loading dataset prompts...")
    dataset_prompts = load_dataset_prompts()

    print("🧠 Analyzing dataset style...")
    style_summary = analyze_dataset_style(dataset_prompts)
    print("\nSTYLE SUMMARY:\n", style_summary)

    user_prompt = input("\n📝 Enter your prompt: ")

    print("✍️ Rewriting prompt using dataset style...")
    final_prompt = rewrite_prompt(user_prompt, style_summary)
    print("\nFINAL PROMPT:\n", final_prompt)

    print("🎨 Generating image...")
    output_path = generate_image(final_prompt)

    print(f"\n✅ Image generated: {output_path}")


# import requests

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
#     # 'Accept-Encoding': 'gzip, deflate, br, zstd',
#     'sec-ch-ua-platform': '"macOS"',
#     'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
#     'sec-ch-ua-mobile': '?0',
#     'Sec-Fetch-Site': 'cross-site',
#     'Sec-Fetch-Mode': 'no-cors',
#     'Sec-Fetch-Dest': 'script',
#     'Sec-Fetch-Storage-Access': 'active',
#     'Referer': 'https://forms.logiforms.com/',
#     'Accept-Language': 'en-US,en-IN;q=0.9,en;q=0.8,hi;q=0.7',
# }

# params = {
#     'key': 'SAKTB4V55TXR4L48VF9Z',
#     'ip': 'local-ip',
#     'format': 'JSON',
#     'compact': 'Y',
#     'callback': 'jsonp_iplookup',
#     '_': '1767982706163',
# }

# response = requests.get('https://https-api.apigurus.com/iplocation/v1.8/locateip', params=params, headers=headers)

# print(response.text)
