from tools.file_tools import list_files, read_file, write_file
from tools.python_exec import python_exec

NAME = "trainer"
MODEL = "gpt-5.4-nano"
TOOLS = [read_file, write_file, list_files, python_exec]
