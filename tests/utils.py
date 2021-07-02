import os
import ast

script_dir = os.path.dirname(__file__)

def load_test_data_from_file(filename):
    with open(os.path.join(script_dir, filename), "r") as test_data:
        return ast.literal_eval(test_data.read())