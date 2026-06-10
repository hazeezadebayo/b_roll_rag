import os
import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

# At the top of your broll_fetcher.py file
from b_roll_rag.utils.keyword_extractor import KeywordExtractor

class BRollFetcher:
    """
    Utility to fetch B-roll footage from Pexels based on search queries.
    Upgraded with MoneyPrinterTurbo architecture: API Key cycling, 
    concurrent multi-threading, exponential backoff retries, and strict timeouts.
    """

    @staticmethod
    def _get_api_key() -> Optional[str]:
        """
        Retrieves a Pexels API key. Supports multiple keys separated by commas
        to distribute load and bypass aggressive rate limits.
        """
        keys_env = os.environ.get("PEXELS_API_KEY", "")
        if not keys_env:
            return None
            
        # Split by comma and remove empty spaces
        keys = [k.strip() for k in keys_env.split(",") if k.strip()]
        if not keys:
            return None
            
        # Randomly select a key for this request to balance API usage
        return random.choice(keys)

    @staticmethod
    def _download_video_task(url: str, filepath: str, max_retries: int = 3) -> Optional[str]:
        """
        Worker function to download a single video with retry logic and timeout quantization.
        """
        for attempt in range(max_retries):
            try:
                # 10s connection timeout, 60s read timeout
                with requests.get(url, stream=True, timeout=(10, 60)) as r:
                    r.raise_for_status()
                    with open(filepath, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
                return filepath
            except Exception as e:
                print(f"Download attempt {attempt + 1} failed for {os.path.basename(filepath)}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt) # Exponential backoff (1s, 2s, 4s...)
                else:
                    print(f"Failed to download {filepath} after {max_retries} attempts.")
                    return None

    @staticmethod
    def fetch_videos(query: str, max_videos: int = 5, orientation: str = "portrait", output_dir: str = "/app/b_roll_rag/data/output/broll") -> List[str]:
        api_key = BRollFetcher._get_api_key()
        if not api_key:
            print("Error: PEXELS_API_KEY environment variable not set (or empty). Cannot fetch B-rolls.")
            return []

        # EXTRACT KEYWORDS HERE
        optimized_query = KeywordExtractor.extract(query)
        print(f"Original: '{query}' -> Optimized for Pexels: '{optimized_query}'")
      
        url = "https://api.pexels.com/videos/search"
        
        # Cleanly pass parameters (MoneyPrinterTurbo style)
        params = {
            "query": optimized_query,
            # Fetch extra in case some links are dead or unsupported formats
            "per_page": max_videos * 2 
        }
        if orientation in ["landscape", "portrait", "square"]:
            params["orientation"] = orientation
            
        headers = {"Authorization": api_key}
        
        try:
            print(f"Searching Pexels for query: '{query}'...")
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Pexels API Error: {e}")
            return []
            
        videos = response.json().get("videos", [])
        
        if not videos:
            print(f"No videos found on Pexels for query: '{query}'")
            return []
            
        os.makedirs(output_dir, exist_ok=True)
        safe_query = query.replace(" ", "_").lower()
        
        # 1. Prepare download tasks
        download_tasks = []
        
        for idx, vid in enumerate(videos):
            if len(download_tasks) >= max_videos:
                break
                
            video_files = vid.get("video_files", [])
            if not video_files:
                continue
                
            # Strict format filtering (must be mp4)
            valid_files = [f for f in video_files if f.get("file_type") == "video/mp4"]
            if not valid_files:
                continue
                
            # Sort by highest resolution
            valid_files = sorted(valid_files, key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
            download_url = valid_files[0].get("link")
            
            filename = f"{safe_query}_rank{idx+1}_{vid.get('id')}.mp4"
            filepath = os.path.join(output_dir, filename)
            
            download_tasks.append((download_url, filepath))

        downloaded_paths = []
        
        # 2. Execute Concurrent Downloading
        print(f"Starting concurrent download of {len(download_tasks)} videos...")
        
        # Open a thread pool to download multiple videos simultaneously
        with ThreadPoolExecutor(max_workers=min(5, len(download_tasks))) as executor:
            future_to_url = {
                executor.submit(BRollFetcher._download_video_task, url, path): path
                for url, path in download_tasks
            }
            
            for future in as_completed(future_to_url):
                result = future.result()
                if result:
                    downloaded_paths.append(result)
                    print(f"Successfully downloaded: {os.path.basename(result)}")
                
        return downloaded_paths