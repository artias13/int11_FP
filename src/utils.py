import os
from typing import List, NoReturn, Union
from pathlib import Path
import py7zr
import requests
from src.logging_config import logger
import shutil

from tqdm import tqdm


def download_file(year: str, month: str, day: str) -> Union[str, None]:
    logger.info(f"Starting download for {year}.{month}.{day}")
    
    url = f"https://samples.vx-underground.org/Samples/VirusSign%20Collection/{year}.{month}/Virussign.{year}.{month}.{day}.7z"
    logger.info(f"Checking availability at URL: {url}")
    
    # Perform a HEAD request to check if the resource exists
    head_response = requests.head(url)
    
    if head_response.status_code == 200:
        logger.info("Resource found. Proceeding with download.")
        
        # Now proceed with the actual download
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        file_name = f"{year}.{month}.{day}.7z"
        with open(file_name, 'wb') as file, tqdm(
            desc=file_name,
            unit='B',
            total=total_size,
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for data in response.iter_content(chunk_size=8192):
                size = file.write(data)
                progress_bar.update(size)
        
        logger.info(f"Download completed successfully")
        return os.path.join(os.getcwd(), file_name)
    else:
        logger.warning(f"Resource not found or inaccessible (Status code: {head_response.status_code})")
        return None


def extract_files(zip_path: Path) -> List[str]:
    logger.info("Starting extraction process")
    
    try:
        # Get the size of the archive
        archive_size = os.path.getsize(zip_path)
        
        with tqdm(total=archive_size, desc="Extracting files") as pbar:
            with py7zr.SevenZipFile(zip_path, mode='r', password="infected") as archive:
                extraction_path = os.path.join(os.getcwd(), "tmp")
                archive.extractall(extraction_path)
                
                # Calculate the total size of extracted files
                extracted_size = sum(os.path.getsize(os.path.join(extraction_path, f)) 
                                    for f in archive.getnames())
                
                # Update progress bar with actual extracted size
                pbar.update(extracted_size)
        
        logger.info(f"Successfully extracted {len(os.listdir(extraction_path))} files")
        return [os.path.join(extraction_path, f) for f in os.listdir(extraction_path)]
    except Exception as e:
        logger.error(f"An error occurred during extraction: {str(e)}")
        return None

# After extraction, remove the original archive
def cleanup_extraction(zip_path: Path) -> NoReturn:
    try:
        # Remove the original archive
        if os.path.exists(zip_path):
            os.remove(zip_path)
            logger.info(f"Original archive {zip_path} has been removed")
        else:
            logger.warning(f"Archive {zip_path} not found. Cannot remove.")

        # Remove the tmp folder
        tmp_folder = Path(os.path.join(os.getcwd(), "tmp"))
        if tmp_folder.is_dir():
            try:
                shutil.rmtree(tmp_folder)
                logger.info(f"Temporary folder {tmp_folder} has been removed")
            except PermissionError:
                logger.warning(f"Permission denied when trying to remove {tmp_folder}")
            except Exception as e:
                logger.error(f"Failed to remove {tmp_folder}: {str(e)}")
        else:
            logger.info(f"{tmp_folder} already removed or doesn't exist")

    except Exception as e:
        logger.error(f"Unexpected error during cleanup: {str(e)}")





