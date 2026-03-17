import torch
from diffusers import StableDiffusionPipeline
from peft import LoraConfig, get_peft_model

device = "mps"

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float32
).to(device)

lora_config = LoraConfig(
    r=4,
    lora_alpha=8,
    target_modules=["to_k", "to_q", "to_v"],
    lora_dropout=0.05,
    bias="none",
)

pipe.unet = get_peft_model(pipe.unet, lora_config)
pipe.unet.train()

print("LoRA training started (Mac test)...")
