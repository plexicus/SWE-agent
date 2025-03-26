#!/usr/bin/env python3
from typing import List
from sweagent.agent.history_processors import HistoryProcessor

class CodexRemediumHistoryProcessor(HistoryProcessor):
    """Process command history for Codex Remedium.
    
    This processor enhances the command history by:
    1. Maintaining context of code analysis
    2. Tracking file modifications
    3. Preserving important code snippets
    """
    
    def __init__(self):
        super().__init__()
        self.code_context = {}
        self.file_modifications = []
    
    def __call__(self, history: List[str]) -> List[str]:
        """Process the command history.
        
        Args:
            history: List of history entries
            
        Returns:
            List[str]: Processed history
        """
        processed_history = []
        
        for entry in history:
            # Extract and store code context
            if "```" in entry:
                self._update_code_context(entry)
            
            # Track file modifications
            if "MODIFIED:" in entry:
                self._track_modification(entry)
            
            # Add entry with enhanced context
            processed_entry = self._enhance_entry(entry)
            processed_history.append(processed_entry)
        
        return processed_history
    
    def _update_code_context(self, entry: str) -> None:
        """Update code context from entry."""
        # Extract code blocks and their context
        code_blocks = entry.split("```")
        for i in range(1, len(code_blocks), 2):
            if i < len(code_blocks):
                lang = code_blocks[i].split("\n")[0]
                code = "\n".join(code_blocks[i].split("\n")[1:])
                self.code_context[code] = lang
    
    def _track_modification(self, entry: str) -> None:
        """Track file modifications."""
        self.file_modifications.append(entry)
    
    def _enhance_entry(self, entry: str) -> str:
        """Enhance history entry with context."""
        # Add file modification context if relevant
        if any(mod in entry for mod in self.file_modifications):
            entry = f"[CONTEXT: File previously modified] {entry}"
        
        # Add code context if relevant
        for code, lang in self.code_context.items():
            if code in entry:
                entry = f"[CONTEXT: Code in {lang}] {entry}"
        
        return entry
