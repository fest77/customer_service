from pathlib import Path


def load_prompt(name: str) -> str:
    file = Path(__file__).parent / 'jinja2' / f'{name}.jinja2'
    return file.read_text(encoding='utf-8')
