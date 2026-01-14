import yaml

def load_config(config_path: str):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
    
from src.utils import load_config
config = load_config("config/config.yaml")
input_path = config['paths']['input_data']
contact_rate = config['contact_rate']['default']