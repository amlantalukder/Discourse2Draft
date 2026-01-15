import re
from enum import Enum
from typing import Any
import logging
from utils import print_func_name

print = logging.info

class FieldType(Enum):
    NAME = 'name'
    EMAIL = 'email'
    PASSWORD = 'password'

@print_func_name
def validateField(field_name: str, field_value: Any, type: FieldType, allow_empty=False):
    
    if not allow_empty and not field_value:
        return False, f'{field_name} cannot be empty'
    
    match type:
        case 'name':
            if not re.match(r"^[A-Za-z]+$", field_value):
                return False, 'Name must consist of letters only'
        case 'email':
            if not re.match(r"[^@]+@[^@]+\.[^@]+", field_value):
                return False, 'Invalid email format'
        case 'password':
            if len(field_value) < 8: 
                return False, 'Password must be at least 8 characters long'
            if not re.search(r"[A-Za-z]", field_value) or not re.search(r"\d", field_value) or not re.search(r"[!_@#$%^&*(),.?\":{}|<>]", field_value):
                return False, 'Password must contain at least one letter, one number, and one special character (!_@#$%^&*(),.?\":\{\}|<>)'
    
    return True, 'Validation successful'