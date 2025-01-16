# rcsa-6529

A collection of Python scripts for asynchronously downloading media files (images and animations) from 6529 NFT collections. The scripts handle concurrent downloads with built-in rate limiting and automatic retries for failed requests.

## Features

- Asynchronous downloads using `aiohttp` with connection pooling
- Smart retry mechanism with configurable attempts and delay
- Progress tracking with `tqdm` progress bars
- Intelligent file handling:
  - Skips existing files to avoid redundant downloads
  - Preserves original file extensions
  - Zero-padded file naming for proper sorting
- Error handling and recovery:
  - Automatic retry for failed downloads
  - Failed download logging for retry in subsequent runs
  - Empty file detection
- Collection-specific optimisations:
  - Pebbles: Configurable media type selection (images/animations)
  - Memes: Automatic file extension detection
- Rate limiting to prevent API overload (10 concurrent connections)
- Automatic directory creation and organization

## Scripts

### rcsa_pebs.py
Downloads media files from the Pebbles NFT collection. 

**Usage:**
```bash
# Download both images and animations
python rcsa_pebs.py

# Download only images
python rcsa_pebs.py --images

# Download only animations
python rcsa_pebs.py --animations
```

**Expected Output:**
```
Found 5 failed downloads from previous run
Processing failed downloads from previous run...

Fetching new items from API...
Processing downloads: 100%|██████████| 1000/1000 [05:23<00:00, 3.09it/s]

Download Summary:
Total files processed: 1000
Already downloaded (skipped): 850
Successfully downloaded: 145
Failed downloads: 5

Failed downloads have been logged to failed_downloads_pebs.txt
```

### rcsa_memes.py
Downloads media files from the Memes NFT collection.

**Usage:**
```bash
python rcsa_memes.py
```

**Expected Output:**
```
Fetching new items from API...
Processing downloads: 100%|██████████| 500/500 [02:45<00:00, 3.02it/s]

Download Summary:
Total files processed: 500
Already downloaded (skipped): 420
Successfully downloaded: 78
Failed downloads: 2

Failed downloads have been logged to failed_downloads_memes.txt
```

## Project Structure

```
├── meme_animations/    # Directory for downloaded meme animations
├── meme_images/       # Directory for downloaded meme images
├── peb_animations/    # Directory for downloaded PEBS animations
├── peb_images/       # Directory for downloaded PEBS images
├── rcsa_memes.py     # Memes collection downloader script
├── rcsa_pebs.py      # PEBS collection downloader script
├── requirements.txt   # Python dependencies
├── .gitignore        # Git ignore configuration
├── LICENSE.txt       # License file
└── README.md         # Project documentation
```

## Output Structure
```
project_directory/
├── meme_images/
│   ├── 0001.JPEG
│   ├── 0002.PNG
│   └── ...
├── meme_animations/
│   ├── 0001.MP4
│   ├── 0002.HTML
│   └── ...
├── peb_images/
│   ├── 001.png
│   ├── 002.png
│   └── ...
├── peb_animations/
│   ├── 001.html
│   ├── 002.html
│   └── ...
├── failed_downloads_pebs.txt
├── failed_downloads_memes.txt
├── rcsa_memes.py
└── rcsa_pebs.py
```


## Technical Details

### Download Manager Class
Both scripts use a `DownloadManager` class that handles:
- Session management with connection pooling
- File download and retry logic
- Progress tracking and reporting
- Failed download logging and recovery

### API Endpoints
- Pebbles Collection: `https://api.6529.io/api/nfts/nextgen/media`
- Memes Collection: `https://api.6529.io/api/nfts/0x33FD426905F149f8376e227d0C9D3340AaD17aF1/media`

### File Naming Conventions
- Pebbles: Three-digit suffix (e.g., `001.png`, `002.html`)
- Memes: Four-digit padded ID with original extension (e.g., `0001.png`, `0002.mp4`)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd rcas-6529
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies

Required Python packages and versions:
```
aiohttp>=3.8.0
asyncio>=3.4.3
tqdm>=4.65.0
```

Python version requirement: >= 3.7 (for asyncio support)

## Error Handling

The scripts handle various error scenarios:
- Network timeouts (3-second retry delay)
- Empty file downloads
- Invalid API responses
- File system errors
- Rate limiting responses

Failed downloads are logged to:
- `failed_downloads_pebs.txt` for Pebbles collection
- `failed_downloads_memes.txt` for Memes collection

## Troubleshooting

Common issues and solutions:

1. **Rate Limiting**
   - Error: Too many concurrent requests
   - Solution: The scripts automatically handle this with connection pooling (10 concurrent connections)

2. **Network Timeouts**
   - Error: Connection timed out
   - Solution: The script will retry up to 3 times with increasing delays

3. **Disk Space**
   - Error: No space left on device
   - Solution: Ensure sufficient disk space for downloaded files
   - Approximate space needed: 7.8GB for full Pebbles collection, 11GB for Memes collection

4. **Permission Issues**
   - Error: Permission denied creating directories
   - Solution: Run the script with appropriate permissions or adjust directory permissions

## License

See LICENSE.txt file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
