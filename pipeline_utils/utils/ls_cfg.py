import yaml
from types import SimpleNamespace 
from pathlib import Path

class IterableSimpleNamespace(SimpleNamespace):
    """IterableSimpleNamespace is an extension class of SimpleNamespace that adds iterable functionality and
    enables usage with dict() and for loops.
    """
    def __iter__(self):
        """Return an iterator of key-value pairs from the namespace's attributes."""
        return iter(vars(self).items())

    def __str__(self):
        """Return a human-readable string representation of the object."""
        return '\n'.join(f'{k}={v}' for k, v in vars(self).items())

    def __getattr__(self, attr):
        """Custom attribute access error message with helpful information."""
        name = self.__class__.__name__
        raise AttributeError(f"""
            '{name}' object has no attribute '{attr}'. This may be caused by a modified or out of date yaml file.
            \nPlease update your code and if necessary replace 
            """)

    def get(self, key, default=None):
        """Return the value of the specified key if it exists; otherwise, return the default value."""
        return getattr(self, key, default)

def load_config(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return IterableSimpleNamespace(**data)


FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
CONFIG_FOLDER=ROOT/'cfg/'
LS_CONFIG_DIR=ROOT/'cfg/labelstudio_config.yaml'
LS_CFG = load_config(LS_CONFIG_DIR)
# GPT_KEY = ROOT/'ls_config/gpt_key.json'