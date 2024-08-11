""" 
__init__.py for the prompts folder
"""

from .generate_answer_node_prompts import template_chunks, template_no_chunks, template_merge, template_chunks_md, template_no_chunks_md, template_merge_md
from .generate_answer_node_csv_prompts import template_chunks_csv, template_no_chunks_csv, template_merge_csv  
from .generate_answer_node_pdf_prompts import template_chunks_pdf, template_no_chunks_pdf, template_merge_pdf
from .generate_answer_node_omni_prompts import template_chunks_omni, template_no_chunk_omni, template_merge_omni
from .merge_answer_node_prompts import template_combined
from .robots_node_prompts import template_robot
from .search_internet_node_prompts import search_internet_template
from .search_link_node_prompts import prompt_relevant_links