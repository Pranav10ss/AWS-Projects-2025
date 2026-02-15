"""
Configuration settings for VPC Flow Log Analyzer
"""

import os
from typing import Optional

class Config:
    """Configuration class for the VPC Flow Log Analyzer"""
    
    # AWS Configuration
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-east-1')
    AWS_PROFILE: Optional[str] = os.getenv('AWS_PROFILE')
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID: str = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
    
    # Flow Log Configuration
    DEFAULT_HOURS_BACK: int = int(os.getenv('DEFAULT_HOURS_BACK', '24'))
    MAX_LOG_ENTRIES: int = int(os.getenv('MAX_LOG_ENTRIES', '1000'))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings"""
        required_vars = []
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            print(f"Missing required environment variables: {missing_vars}")
            return False
        
        return True
