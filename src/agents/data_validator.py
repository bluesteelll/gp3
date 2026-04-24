from tools.file_tools import list_files, read_file
from tools.python_exec import python_exec

NAME = "data_validator"
MODEL = "claude-sonnet-4-6"
TOOLS = [read_file, list_files, python_exec]
