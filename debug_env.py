
import sys

try:
    import numpy
    print(f"NumPy version: {numpy.__version__}")
except ImportError as e:
    print(f"NumPy import failed: {e}")

try:
    import rasa
    print(f"Rasa version: {rasa.__version__}")
except ImportError as e:
    print(f"Rasa import failed: {e}")

try:
    import langchain
    print(f"LangChain version: {langchain.__version__}")
except ImportError as e:
    print(f"LangChain import failed: {e}")
