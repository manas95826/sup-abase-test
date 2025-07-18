import aiohttp
import asyncio
import os
import magic
from urllib.parse import urlparse
from pathlib import Path
from tqdm import tqdm

# List of URLs to download
urls = [
    ...
]

def get_extension_from_content_type(content_type):
    """Get file extension from content type."""
    content_type = content_type.lower()
    if 'pdf' in content_type:
        return '.pdf'
    elif 'jpeg' in content_type or 'jpg' in content_type:
        return '.jpg'
    elif 'png' in content_type:
        return '.png'
    elif 'tiff' in content_type:
        return '.tiff'
    elif 'gif' in content_type:
        return '.gif'
    return None

def get_extension_from_magic(content):
    """Get file extension using python-magic."""
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(content)
    
    if 'pdf' in mime_type:
        return '.pdf'
    elif 'jpeg' in mime_type:
        return '.jpg'
    elif 'png' in mime_type:
        return '.png'
    elif 'tiff' in mime_type:
        return '.tiff'
    elif 'gif' in mime_type:
        return '.gif'
    return None

async def download_file(session, url, download_dir):
    # Extract filename from URL (last part of the path)
    filename = url.split('/')[-1]
    
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                
                # Try to get extension from Content-Type header
                content_type = response.headers.get('Content-Type', '')
                extension = get_extension_from_content_type(content_type)
                
                # If no extension found from Content-Type, try using python-magic
                if not extension:
                    extension = get_extension_from_magic(content)
                
                # If still no extension, use .bin as fallback
                if not extension:
                    extension = '.bin'
                
                # Create final filename with extension
                final_filename = f"{filename}{extension}"
                filepath = download_dir / final_filename
                
                with open(filepath, 'wb') as f:
                    f.write(content)
                print(f"Downloaded: {final_filename}")
                return True
            else:
                print(f"Failed to download {filename}: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
        return False

async def download_all_files():
    # Create downloads directory
    download_dir = Path('downloads')
    download_dir.mkdir(exist_ok=True)
    
    # Initialize progress bar
    progress = tqdm(total=len(urls), desc="Downloading files")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(download_file(session, url, download_dir))
            tasks.append(task)
        
        # Wait for all downloads to complete and update progress
        for coro in asyncio.as_completed(tasks):
            await coro
            progress.update(1)
    
    progress.close()

if __name__ == "__main__":
    print(f"Starting download of {len(urls)} files...")
    asyncio.run(download_all_files())
    print("Download complete!")
