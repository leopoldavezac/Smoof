
from typing import List

def get_not_none_elements(elements:List) -> List:
    
    return [
        el for el in elements if el != None
        ]

def get_index_not_none_element(elements:List) -> int:

    for i, el in enumerate(elements):
        if el is not None:
            return i