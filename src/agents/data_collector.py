from tools.file_tools import write_file
from tools.python_exec import python_exec
from tools.web_search import tavily_search

NAME = "data_collector"
MODEL = "DeepSeek-V3.1-Fast"
TOOLS = [tavily_search, write_file, python_exec]
