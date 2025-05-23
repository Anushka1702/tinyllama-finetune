# -*- coding: utf-8 -*-
"""tinyllama-finetune

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rKlcsjWp-kZdiVl12nWcXFxO3Zd0pWvt
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install transformers datasets peft accelerate trl sentencepiece

from datasets import load_dataset

# Load the Alpaca-cleaned dataset
dataset = load_dataset("yahma/alpaca-cleaned")
print(dataset["train"][0])  # Check the first example in the training set

!apt-get install git-lfs

from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Model and tokenizer loaded successfully!")

from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import get_peft_model, LoraConfig, TaskType
from transformers import Trainer, DataCollatorForLanguageModeling
from datasets import load_dataset

# Load model and tokenizer
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
dataset = load_dataset("yahma/alpaca-cleaned")["train"]
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# Tokenize the dataset
def tokenize(example):
    return tokenizer(f"### Instruction:\n{example['instruction']}\n### Input:\n{example['input']}\n### Response:\n{example['output']}", padding="max_length", truncation=True, max_length=512)

tokenized_dataset = dataset.map(tokenize)

# Load the model
model = AutoModelForCausalLM.from_pretrained(model_name)

# Set up LoRA configuration
config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)
model = get_peft_model(model, config)

# Training arguments (disable W&B logging)
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    warmup_steps=10,
    max_steps=500,  # Limit total steps to 500 for quick testing
    learning_rate=2e-4,
    fp16=True,
    logging_steps=20,
    save_steps=250,
    save_total_limit=2,
    logging_dir="./logs",
    report_to="none",  # Disable W&B for now to simplify
)


# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# Fine-tune the model
trainer.train()



from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Path to your Hugging Face model repository or local files
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Or the local path to the model
tokenizer_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Or the local path to the tokenizer

# Load tokenizer and model from Hugging Face (or use local paths if the model is saved locally)
tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)

# Prepare for inference
model.eval()
if torch.cuda.is_available():
    model.to("cuda")

prompt = "### Instruction:\nExplain the concept of quantum computing in simple terms.\n### Input:\n\n### Response:\n"
inputs = tokenizer(prompt, return_tensors="pt")

# Move inputs to the GPU if available
if torch.cuda.is_available():
    inputs = {k: v.to("cuda") for k, v in inputs.items()}

# Generate output
outputs = model.generate(
    **inputs,
    max_new_tokens=150,
    do_sample=True,
    temperature=0.7,
    top_p=0.9
)

# Decode and print
print(tokenizer.decode(outputs[0], skip_special_tokens=True))