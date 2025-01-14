import aiohttp
import asyncio
import json
import os
from tqdm import tqdm
import urllib.parse
import time
from datetime import datetime

class DownloadManager:
    def __init__(self):
        self.failed_downloads = set()  # Use a set to prevent duplicates
        self.log_file = "failed_downloads_memes.txt"
        self.processed_files = {'skipped': 0, 'success': 0}
        
    def load_failed_downloads(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                # Use a set to store unique failed downloads
                failed_items = {line.strip() for line in f if line.strip()}
            print(f"\nFound {len(failed_items)} failed downloads from previous run")
            # Delete the file after reading
            os.remove(self.log_file)
            return failed_items
        return set()

    async def download_file(self, session, url, filename, max_retries=3, retry_delay=1):
        if not url:
            return None, None
        
        # Check if file exists and is not empty
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            self.processed_files['skipped'] += 1
            return "skipped", None
        
        for attempt in range(max_retries):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        if len(content) > 0:
                            with open(filename, 'wb') as f:
                                f.write(content)
                            self.processed_files['success'] += 1
                            return "success", None
                        else:
                            print(f"Empty content received for {url}")
                    else:
                        print(f"Status {response.status} for {url}")
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
        
        # Add to set instead of list to prevent duplicates
        self.failed_downloads.add(f"{url}|{filename}")
        return "failed", (url, filename)

    def save_failed_downloads(self):
        if self.failed_downloads:
            with open(self.log_file, 'w') as f:
                for failed_item in self.failed_downloads:
                    f.write(f"{failed_item}\n")
            print(f"\nFailed downloads have been logged to {self.log_file}")

    async def process_downloads(self):
        os.makedirs('meme_images', exist_ok=True)
        os.makedirs('meme_animations', exist_ok=True)
        
        timeout = aiohttp.ClientTimeout(total=3600)
        connector = aiohttp.TCPConnector(limit=10)
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            tasks = []
            
            # First process any failed downloads from previous run
            failed_items = self.load_failed_downloads()
            if failed_items:
                print("Processing failed downloads from previous run...")
                for item in failed_items:
                    url, filename = item.split('|')
                    tasks.append(self.download_file(session, url, filename))
            
            # Then process the full list from API
            print("\nFetching new items from API...")
            async with session.get('https://api.6529.io/api/nfts/0x33FD426905F149f8376e227d0C9D3340AaD17aF1/media') as response:
                data = await response.json()
            
            for item in data:
                # Format the ID with zero padding to 4 digits
                padded_id = f"{int(item['id']):04d}"
                
                if item['image']:
                    image_ext = os.path.splitext(urllib.parse.urlparse(item['image']).path)[1]
                    image_filename = os.path.join('meme_images', f"{padded_id}{image_ext}")
                    tasks.append(self.download_file(session, item['image'], image_filename))
                
                if item['animation']:
                    anim_ext = os.path.splitext(urllib.parse.urlparse(item['animation']).path)[1]
                    animation_filename = os.path.join('meme_animations', f"{padded_id}{anim_ext}")
                    tasks.append(self.download_file(session, item['animation'], animation_filename))
            
            # Process all tasks
            with tqdm(total=len(tasks), desc="Processing downloads") as pbar:
                for task in asyncio.as_completed(tasks):
                    await task
                    pbar.update(1)
            
            # Save failed downloads and print summary
            self.save_failed_downloads()
            
            print(f"\nDownload Summary:")
            print(f"Total files processed: {len(tasks)}")
            print(f"Already downloaded (skipped): {self.processed_files['skipped']}")
            print(f"Successfully downloaded: {self.processed_files['success']}")
            print(f"Failed downloads: {len(self.failed_downloads)}")  # Using set length for unique count

def main():
    download_manager = DownloadManager()
    asyncio.run(download_manager.process_downloads())

if __name__ == "__main__":
    main()