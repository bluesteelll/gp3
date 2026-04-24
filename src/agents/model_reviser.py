from tools.file_tools import list_files, read_file
from tools.python_exec import python_exec

NAME = "model_reviser"
MODEL = "claude-opus-4-7-think"
TOOLS = [read_file, list_files, python_exec]
