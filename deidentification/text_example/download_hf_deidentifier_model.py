"""
Download the hugging face model
"""
import transformers
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForTokenClassification

transformers_model = "StanfordAIMI/stanford-deidentifier-base"

print("Downloading model from Hugging Face...")
snapshot_download(repo_id=transformers_model)

# Instantiate to make sure it's downloaded during installation and not runtime
AutoTokenizer.from_pretrained(transformers_model)
AutoModelForTokenClassification.from_pretrained(transformers_model)