import aiohttp
import asyncio
import json
import os
from tqdm import tqdm
import urllib.parse
import time
from datetime import datetime
import argparse

class DownloadManager:
    def __init__(self, download_images=False, download_animations=False):
        self.failed_downloads = set()
        self.log_file = "failed_downloads_pebs.txt"
        self.download_images = download_images
        self.download_animations = download_animations
        
    def load_failed_downloads(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                failed_items = {line.strip() for line in f if line.strip()}
            print(f"\nFound {len(failed_items)} failed downloads from previous run")
            os.remove(self.log_file)
            return failed_items
        return set()

    def extract_id_from_url(self, url):
        # Extract the number from the end of the URL
        path = urllib.parse.urlparse(url).path
        number = path.split('/')[-1]
        # Get the last 3 digits, pad with zeros if necessary
        return number.zfill(3)[-3:]

    async def download_file(self, session, url, filename, max_retries=3, retry_delay=1):
        if not url:
            return None, None
        
        # Check if file exists and is not empty
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            return "skipped", None
        
        for attempt in range(max_retries):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        if len(content) > 0:
                            with open(filename, 'wb') as f:
                                f.write(content)
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
        
        self.failed_downloads.add(f"{url}|{filename}")
        return "failed", (url, filename)

    def save_failed_downloads(self):
        if self.failed_downloads:
            with open(self.log_file, 'w') as f:
                for failed_item in self.failed_downloads:
                    f.write(f"{failed_item}\n")
            print(f"\nFailed downloads have been logged to {self.log_file}")

    async def process_downloads(self):
        if self.download_images:
            os.makedirs('peb_images', exist_ok=True)
        if self.download_animations:
            os.makedirs('peb_animations', exist_ok=True)
        
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
            async with session.get('https://api.6529.io/api/nfts/nextgen/media') as response:
                data = await response.json()
            
            for item in data:
                if self.download_images and item['image']:
                    id_suffix = self.extract_id_from_url(item['image'])
                    image_filename = os.path.join('peb_images', f"{id_suffix}.png")
                    tasks.append(self.download_file(session, item['image'], image_filename))
                
                if self.download_animations and item['animation']:
                    id_suffix = self.extract_id_from_url(item['animation'])
                    animation_filename = os.path.join('peb_animations', f"{id_suffix}.html")
                    tasks.append(self.download_file(session, item['animation'], animation_filename))
            
            # Process all tasks
            skipped = 0
            success = 0
            failed = 0
            
            with tqdm(total=len(tasks), desc="Processing downloads") as pbar:
                for task in asyncio.as_completed(tasks):
                    status, error = await task
                    if status == "skipped":
                        skipped += 1
                    elif status == "success":
                        success += 1
                    else:
                        failed += 1
                    pbar.update(1)
            
            # Save failed downloads and print summary
            self.save_failed_downloads()
            
            print(f"\nDownload Summary:")
            print(f"Total files processed: {len(tasks)}")
            print(f"Already downloaded (skipped): {skipped}")
            print(f"Successfully downloaded: {success}")
            print(f"Failed downloads: {failed}")

def main():
    parser = argparse.ArgumentParser(description='Download NFT images and animations. By default, downloads both.')
    parser.add_argument('--images', action='store_true', help='Download only images')
    parser.add_argument('--animations', action='store_true', help='Download only animations')
    
    args = parser.parse_args()
    
    # If no specific flag is provided, download both
    if not args.images and not args.animations:
        download_images = True
        download_animations = True
    else:
        # If any flag is provided, only download what was specifically requested
        download_images = args.images
        download_animations = args.animations
    
    download_manager = DownloadManager(
        download_images=download_images,
        download_animations=download_animations
    )
    asyncio.run(download_manager.process_downloads())

if __name__ == "__main__":
    main()