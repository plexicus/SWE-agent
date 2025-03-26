#!/usr/bin/env python3

def grep_search(query, includes=None, case_insensitive=False, match_per_line=True):
    """
    Perform a text-based search in files.
    
    Args:
        query (str): Search pattern
        includes (list): Files or directories to search within
        case_insensitive (bool): Whether to ignore case
        match_per_line (bool): Whether to return matching lines or just file names
    
    Returns:
        dict: Search results with matching files and lines
    """
    # TODO: Implement grep search functionality
    pass

if __name__ == "__main__":
    import sys
    import json
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = grep_search(**args)
    print(json.dumps(result))
