from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime

class MovieSchema:
    """
    Schema definition and validation for movie data.
    Handles data cleaning, type conversion, and standardization.
    """
    
    def __init__(self):
        self.required_columns = {
            'id': int,
            'title': str,
            'overview': str,
            'release_date': str,
            'vote_average': float,
            'vote_count': int,
            'popularity': float,
            'original_language': str,
            'runtime': int,
            'budget': int,
            'revenue': int,
            'genres': list,
            'production_companies': list,
            'cast': list,
            'crew': list,
            'keywords': list
        }
        
    def _clean_text(self, text: str) -> str:
        """Clean and standardize text fields."""
        if pd.isna(text) or not isinstance(text, str):
            return ""
        return text.strip()
        
    def _convert_date(self, date_str: str) -> str:
        """Convert and validate date strings."""
        try:
            if pd.isna(date_str):
                return None
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return None
            
    def _extract_names(self, items: List[Dict[str, Any]]) -> List[str]:
        """Extract names from list of dictionaries."""
        if not isinstance(items, list):
            return []
        return [item.get('name', '') for item in items if isinstance(item, dict)]
        
    def _clean_numeric(self, value: Any, type_: type) -> Any:
        """Clean and convert numeric values."""
        try:
            if pd.isna(value):
                return type_(0)
            return type_(value)
        except (ValueError, TypeError):
            return type_(0)
            
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply schema to DataFrame."""
        # Create copy to avoid modifying original
        df = df.copy()
        
        # Clean and standardize text fields
        text_columns = ['title', 'overview', 'original_language']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._clean_text)
                
        # Convert date fields
        if 'release_date' in df.columns:
            df['release_date'] = df['release_date'].apply(self._convert_date)
            
        # Clean numeric fields
        numeric_columns = {
            'vote_average': float,
            'vote_count': int,
            'popularity': float,
            'runtime': int,
            'budget': int,
            'revenue': int
        }
        for col, type_ in numeric_columns.items():
            if col in df.columns:
                df[col] = df[col].apply(lambda x: self._clean_numeric(x, type_))
                
        # Extract names from nested structures
        list_columns = {
            'genres': 'genres',
            'production_companies': 'production_companies',
            'keywords': 'keywords'
        }
        for col in list_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._extract_names)
                
        # Handle cast and crew separately
        if 'cast' in df.columns:
            df['cast'] = df['cast'].apply(lambda x: 
                [f"{p.get('name', '')} as {p.get('character', '')}" 
                 for p in (x if isinstance(x, list) else [])[:5]])
                
        if 'crew' in df.columns:
            df['crew'] = df['crew'].apply(lambda x: 
                [f"{p.get('name', '')} ({p.get('job', '')})" 
                 for p in (x if isinstance(x, list) else [])[:5]])
                
        # Add missing columns with default values
        for col, type_ in self.required_columns.items():
            if col not in df.columns:
                df[col] = type_() if type_ in (list, dict) else type_(0)
                
        return df[list(self.required_columns.keys())]
        
    def validate(self, df: pd.DataFrame) -> bool:
        """
        Validate that DataFrame meets schema requirements.
        Returns True if valid, False otherwise.
        """
        try:
            # Check all required columns exist
            missing_cols = set(self.required_columns.keys()) - set(df.columns)
            if missing_cols:
                print(f"Missing required columns: {missing_cols}")
                return False
                
            # Check data types
            for col, type_ in self.required_columns.items():
                if col in ['genres', 'production_companies', 'cast', 'crew', 'keywords']:
                    if not all(isinstance(x, list) for x in df[col].dropna()):
                        print(f"Invalid type in column {col}")
                        return False
                elif not all(isinstance(x, type_) for x in df[col].dropna()):
                    print(f"Invalid type in column {col}")
                    return False
                    
            return True
            
        except Exception as e:
            print(f"Validation error: {str(e)}")
            return False