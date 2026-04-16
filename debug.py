import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-3B-Instruct"

tok = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, torch_dtype=torch.float16, device_map="cuda"
)

messages = [
    {
        "role": "user",
        "content": (
            "Janet's ducks lay 16 eggs per day. She eats three for breakfast every "
            "morning and bakes muffins for her friends every day with four. She sells "
            "the remainder at the farmers market daily for $2 per egg. How much does "
            "she make every day at the farmers market?"
        ),
    }
]

text = tok.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=False,
)

inputs = tok(text, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=False,
    )

prompt_len = inputs["input_ids"].shape[-1]
print(tok.decode(outputs[0][prompt_len:], skip_special_tokens=True))
