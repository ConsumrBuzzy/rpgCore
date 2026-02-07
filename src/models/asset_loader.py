"""
Specialized asset loader following Single Responsibility Principle.

Handles only the loading and validation of binary assets from disk.
"""

import mmap
import struct
import gzip
import pickle
from pathlib import Path
from typing import Dict, Any, Optional

from loguru import logger

from .interfaces import IAssetLoader, AssetMetadata, LoadResult


class BinaryAssetLoader(IAssetLoader):
    """
    Loads and validates binary DGT asset files.
    
    Single responsibility: Asset loading and format validation.
    """
    
    def __init__(self):
        self._mmap_handle: Optional[mmap.mmap] = None
        self._file_handle: Optional[Any] = None
        self._asset_data: Optional[Dict[str, Any]] = None
        
    def load_assets(self, asset_path: Path) -> bool:
        """
        Load assets from binary file with memory mapping.
        
        Args:
            asset_path: Path to the assets.dgt binary file
            
        Returns:
            True if loading succeeded, False otherwise
        """
        try:
            logger.info(f"📦 Loading binary assets from {asset_path}")
            
            # Open file for memory mapping
            self._file_handle = open(asset_path, 'rb')
            self._mmap_handle = mmap.mmap(
                self._file_handle.fileno(), 
                0, 
                access=mmap.ACCESS_READ
            )
            
            # Validate and parse header
            metadata = self._parse_header()
            if not metadata:
                return False
            
            # Read and decompress asset data
            self._asset_data = self._read_asset_data(metadata.data_offset)
            
            logger.info(f"✅ Successfully loaded {metadata.asset_count} assets")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load assets: {e}")
            self.cleanup()
            return False
    
    def validate_asset_format(self, data: bytes) -> bool:
        """
        Validate binary asset format.
        
        Args:
            data: Raw binary data to validate
            
        Returns:
            True if format is valid, False otherwise
        """
        try:
            if len(data) < 40:
                return False
            
            magic = data[:4]
            return magic == b'DGT\x01'
            
        except Exception:
            return False
    
    def get_asset_data(self) -> Optional[Dict[str, Any]]:
        """Get loaded asset data."""
        return self._asset_data
    
    def get_metadata(self) -> Optional[AssetMetadata]:
        """Get asset metadata from loaded file."""
        try:
            if not self._mmap_handle:
                return None
            
            header_data = self._mmap_handle[:40]
            magic = header_data[:4]
            version = struct.unpack('<I', header_data[4:8])[0]
            build_time = struct.unpack('<d', header_data[8:16])[0]
            checksum = header_data[16:32]
            asset_count = struct.unpack('<I', header_data[32:36])[0]
            data_offset = struct.unpack('<I', header_data[36:40])[0]
            
            if magic != b'DGT\x01':
                return None
            
            return AssetMetadata(
                version=version,
                build_time=build_time,
                checksum=checksum.hex(),
                asset_count=asset_count,
                data_offset=data_offset
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to parse metadata: {e}")
            return None
    
    def cleanup(self) -> None:
        """Clean up memory-mapped resources."""
        if self._mmap_handle:
            self._mmap_handle.close()
            self._mmap_handle = None
        
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
        
        self._asset_data = None
        logger.info("🧹 AssetLoader cleaned up")
    
    def _parse_header(self) -> Optional[AssetMetadata]:
        """Parse and validate file header."""
        try:
            metadata = self.get_metadata()
            if not metadata:
                logger.error("❌ Invalid file format or corrupted header")
                return None
            
            logger.info(f"✅ Validated DGT binary v{metadata.version}")
            logger.info(f"📊 Assets: {metadata.asset_count}")
            logger.info(f"🔤 Checksum: {metadata.checksum}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to parse header: {e}")
            return None
    
    def _read_asset_data(self, data_offset: int) -> Optional[Dict[str, Any]]:
        """Read and decompress asset data."""
        try:
            # Read compressed data
            raw_data = self._mmap_handle[data_offset:]
            
            # Find gzip start
            gzip_start = raw_data.find(b'\x1f\x8b')
            if gzip_start == -1:
                raise ValueError("No gzip data found in file")
            
            compressed_data = raw_data[gzip_start:]
            asset_data = pickle.loads(gzip.decompress(compressed_data))
            
            logger.debug("✅ Asset data decompressed successfully")
            return asset_data
            
        except Exception as e:
            logger.error(f"❌ Failed to read asset data: {e}")
            return None


class LoadResultFactory:
    """Factory for creating LoadResult objects."""
    
    @staticmethod
    def success(metadata: AssetMetadata) -> LoadResult:
        """Create successful load result."""
        return LoadResult(success=True, metadata=metadata)
    
    @staticmethod
    def failure(error: str) -> LoadResult:
        """Create failed load result."""
        return LoadResult(success=False, error=error)
