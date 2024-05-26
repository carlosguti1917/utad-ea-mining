# Import the DataPrepare class
from owlready2 import *
import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from app.src.utils import open_api_util


test = open_api_util.split_url("http://192.168.0.15:8000/sandbox/handle-claim/v1")
print(f"test: {test}")

teste = open_api_util.split_url('https://api.staging.example.com/handle-claim/v1')
print(f"teste: {teste}")

teste = open_api_util.split_url('/handle-claim/v1')
print(f"teste: {teste}")

print(" executed with success")
