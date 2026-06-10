import re
import os
from typing import List, Dict

class TranscriptParser:
    """
    Utility class to parse SRT and timestamped TXT files.
    Returns a list of dictionaries: [{"start_time": float, "end_time": float, "text": str}]
    """
    
    @staticmethod
    def _time_to_seconds(time_str: str) -> float:
        """Converts HH:MM:SS,MMM or MM:SS to seconds float."""
        time_str = time_str.replace(',', '.').strip()
        parts = time_str.split(':')
        
        seconds = 0.0
        if len(parts) == 3: # HH:MM:SS.MMM
            seconds = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2: # MM:SS.MMM
            seconds = float(parts[0]) * 60 + float(parts[1])
        else:
            seconds = float(parts[0])
            
        return seconds

    @staticmethod
    def parse_srt(file_path: str) -> List[Dict[str, float | str]]:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Pattern to match SRT blocks: 
        # 1
        # 00:00:00,000 --> 00:00:02,000
        # Text line 1
        # Text line 2
        
        pattern = re.compile(r'\d+\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)', re.DOTALL)
        matches = pattern.findall(content)
        
        segments = []
        for start_str, end_str, text in matches:
            segments.append({
                "start_time": TranscriptParser._time_to_seconds(start_str),
                "end_time": TranscriptParser._time_to_seconds(end_str),
                "text": text.replace('\n', ' ').strip()
            })
        return segments

    @staticmethod
    def parse_txt(file_path: str) -> List[Dict[str, float | str]]:
        """
        Parses a generic text file assuming lines like:
        [00:01:05.000 - 00:01:10.000] Hello world
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        segments = []
        # basic pattern: [start - end] text
        pattern = re.compile(r'\[?(.*?)\s*-\s*(.*?)\]?\s+(.*)')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            match = pattern.match(line)
            if match:
                start_str, end_str, text = match.groups()
                try:
                    segments.append({
                        "start_time": TranscriptParser._time_to_seconds(start_str),
                        "end_time": TranscriptParser._time_to_seconds(end_str),
                        "text": text.strip()
                    })
                except ValueError:
                    # Ignore unparseable lines
                    pass
        return segments

    @staticmethod
    def parse(file_path: str) -> List[Dict[str, float | str]]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Transcript file not found: {file_path}")
            
        ext = file_path.lower().split('.')[-1]
        
        if ext == 'srt':
            return TranscriptParser.parse_srt(file_path)
        elif ext == 'txt':
            return TranscriptParser.parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported transcript format: {ext}")
