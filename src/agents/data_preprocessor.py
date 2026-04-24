from tools.file_tools import list_files, read_file, write_file
from tools.python_exec import python_exec

NAME = "data_preprocessor"
MODEL = "gpt-5.4-mini"
TOOLS = [read_file, write_file, list_files, python_exec]
