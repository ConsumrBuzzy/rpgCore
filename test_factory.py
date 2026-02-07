from model_factory import get_model
import os

try:
    print("Testing ModelFactory...")
    model = get_model("llama3.2:1b")
    print(f"Model created: {model}")
    print("Test Passed")
except Exception as e:
    print(f"Test Failed: {e}")
    import traceback
    traceback.print_exc()
