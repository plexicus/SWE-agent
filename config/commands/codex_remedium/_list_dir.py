#!/usr/bin/env python3

def list_dir(directory_path):
    """
    List contents of a directory with metadata.
    
    Args:
        directory_path (str): Path to directory to list
    
    Returns:
        dict: Directory contents with metadata (size, type, etc.)
    """
    # TODO: Implement directory listing functionality
    pass

if __name__ == "__main__":
    import sys
    import json
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = list_dir(**args)
    print(json.dumps(result))
