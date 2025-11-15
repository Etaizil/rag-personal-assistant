from . import text_adapter  # registers on import
from . import pdf_adapter
from . import html_adapter
from . import csvtsv_adapter
from . import json_adapter

from .registry import pick_adapter, all_adapters
