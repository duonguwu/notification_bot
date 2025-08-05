#!/usr/bin/env python3
"""
Script to update all model imports to use the new registry pattern.
"""

import os
import re
from pathlib import Path

# Files to update
FILES_TO_UPDATE = [
    "api/message.py",
    "api/customer.py", 
    "api/notification.py",
    "api/tasks.py",
    "tasks/send_notification.py",
    "tasks/import_customers.py",
    "services/memory_manager.py"
]

# Import mappings
IMPORT_MAPPINGS = {
    "from models.user import User": "from models import get_user",
    "from models.customer import Customer": "from models import get_customer", 
    "from models.notification import NotificationConfig": "from models import get_notification_config",
    "from models.notification import Notification": "from models import get_notification",
    "from models.chat import Chat": "from models import get_chat",
    "from models.chat import Message": "from models import get_message",
    "from models.task import Task": "from models import get_task"
}

# Model usage patterns
MODEL_USAGE_PATTERNS = [
    (r"User\.", "User = get_user()\n    "),
    (r"Customer\.", "Customer = get_customer()\n    "),
    (r"NotificationConfig\.", "NotificationConfig = get_notification_config()\n    "),
    (r"Notification\.", "Notification = get_notification()\n    "),
    (r"Chat\.", "Chat = get_chat()\n    "),
    (r"Message\.", "Message = get_message()\n    "),
    (r"Task\.", "Task = get_task()\n    ")
]

def update_file(file_path):
    """Update a single file."""
    print(f"Updating {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update imports
    for old_import, new_import in IMPORT_MAPPINGS.items():
        content = content.replace(old_import, new_import)
    
    # Update model usage
    for pattern, replacement in MODEL_USAGE_PATTERNS:
        # Find all lines that use the model
        lines = content.split('\n')
        updated_lines = []
        
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                # Check if we already added the getter in this function
                function_start = i
                while function_start > 0 and not lines[function_start].strip().startswith('def '):
                    function_start -= 1
                
                # Check if getter already exists in this function
                has_getter = False
                for j in range(function_start, i):
                    if replacement.strip() in lines[j]:
                        has_getter = True
                        break
                
                if not has_getter:
                    # Add getter at function start
                    indent = len(lines[function_start]) - len(lines[function_start].lstrip())
                    getter_line = ' ' * (indent + 4) + replacement.strip()
                    lines.insert(function_start + 1, getter_line)
                    i += 1  # Adjust index after insertion
            
            updated_lines.append(lines[i])
        
        content = '\n'.join(updated_lines)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {file_path}")

def main():
    """Main function."""
    base_dir = Path(__file__).parent
    
    for file_path in FILES_TO_UPDATE:
        full_path = base_dir / file_path
        if full_path.exists():
            update_file(full_path)
        else:
            print(f"⚠ File not found: {file_path}")

if __name__ == "__main__":
    main() 