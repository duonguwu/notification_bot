import re
from typing import List, Dict, Any
import pandas as pd


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Remove spaces, dashes, parentheses
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it's a valid phone number (10-15 digits)
    return bool(re.match(r'^\+?[0-9]{10,15}$', phone))


def validate_csv_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate CSV structure and required columns."""
    required_columns = ['email', 'full_name']
    optional_columns = ['phone', 'company', 'position', 'address', 'city', 'country', 'language', 'tags']
    
    missing_required = [col for col in required_columns if col not in df.columns]
    
    if missing_required:
        return {
            "valid": False,
            "error": f"Missing required columns: {missing_required}",
            "required_columns": required_columns,
            "found_columns": list(df.columns)
        }
    
    return {
        "valid": True,
        "required_columns": required_columns,
        "optional_columns": optional_columns,
        "found_columns": list(df.columns)
    }


def clean_customer_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and validate customer data."""
    cleaned = {}
    
    # Required fields
    if 'email' in data:
        email = str(data['email']).strip().lower()
        if validate_email(email):
            cleaned['email'] = email
        else:
            raise ValueError(f"Invalid email format: {email}")
    
    if 'full_name' in data:
        full_name = str(data['full_name']).strip()
        if full_name:
            cleaned['full_name'] = full_name
        else:
            raise ValueError("Full name cannot be empty")
    
    # Optional fields
    if 'phone' in data and pd.notna(data['phone']):
        phone = str(data['phone']).strip()
        if phone and validate_phone(phone):
            cleaned['phone'] = phone
    
    if 'company' in data and pd.notna(data['company']):
        cleaned['company'] = str(data['company']).strip()
    
    if 'position' in data and pd.notna(data['position']):
        cleaned['position'] = str(data['position']).strip()
    
    if 'address' in data and pd.notna(data['address']):
        cleaned['address'] = str(data['address']).strip()
    
    if 'city' in data and pd.notna(data['city']):
        cleaned['city'] = str(data['city']).strip()
    
    if 'country' in data and pd.notna(data['country']):
        cleaned['country'] = str(data['country']).strip()
    
    if 'language' in data and pd.notna(data['language']):
        cleaned['language'] = str(data['language']).strip()
    
    if 'tags' in data and pd.notna(data['tags']):
        if isinstance(data['tags'], str):
            tags = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
        elif isinstance(data['tags'], list):
            tags = [str(tag).strip() for tag in data['tags'] if tag and str(tag).strip()]
        else:
            tags = []
        cleaned['tags'] = tags
    
    return cleaned


def validate_notification_template(template: str, data: Dict[str, Any]) -> bool:
    """Validate notification template with provided data."""
    try:
        # Try to format template with data
        template.format(**data)
        return True
    except KeyError as e:
        # Missing required variable
        return False
    except Exception:
        # Other formatting errors
        return False


def extract_template_variables(template: str) -> List[str]:
    """Extract variable names from template string."""
    import string
    formatter = string.Formatter()
    variables = []
    
    for literal_text, field_name, format_spec, conversion in formatter.parse(template):
        if field_name is not None:
            variables.append(field_name)
    
    return list(set(variables))  # Remove duplicates 