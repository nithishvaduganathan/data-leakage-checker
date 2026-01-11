"""
Dataset Analyzer Module
Analyzes dataset structure and detects column types
"""
import pandas as pd
import numpy as np
from datetime import datetime


class DatasetAnalyzer:
    """Analyzes dataset structure and column types"""
    
    def __init__(self, df):
        self.df = df
        self.analysis_result = {}
    
    def analyze(self):
        """Perform comprehensive dataset analysis"""
        self.analysis_result = {
            'row_count': len(self.df),
            'column_count': len(self.df.columns),
            'missing_values': self._get_missing_values(),
            'duplicate_count': self.df.duplicated().sum(),
            'columns': self._analyze_columns(),
            'data_types': self._get_data_types()
        }
        return self.analysis_result
    
    def _get_missing_values(self):
        """Calculate missing values per column"""
        missing = self.df.isnull().sum()
        return {col: int(count) for col, count in missing.items() if count > 0}
    
    def _get_data_types(self):
        """Get data types for all columns"""
        return {col: str(dtype) for col, dtype in self.df.dtypes.items()}
    
    def _analyze_columns(self):
        """Analyze each column and detect its type"""
        columns_info = {}
        
        for col in self.df.columns:
            col_type = self._detect_column_type(col)
            columns_info[col] = {
                'type': col_type,
                'dtype': str(self.df[col].dtype),
                'unique_count': int(self.df[col].nunique()),
                'missing_count': int(self.df[col].isnull().sum()),
                'sample_values': self._get_sample_values(col)
            }
        
        return columns_info
    
    def _detect_column_type(self, col):
        """Detect if column is numerical, categorical, datetime, or ID"""
        col_data = self.df[col]
        
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(col_data):
            return 'datetime'
        
        # Try to convert to datetime
        if col_data.dtype == 'object':
            try:
                pd.to_datetime(col_data.dropna().head(100))
                return 'datetime'
            except:
                pass
        
        # Check for ID columns (unique identifiers)
        unique_ratio = col_data.nunique() / len(col_data)
        if unique_ratio > 0.95 and len(col_data) > 100:
            # High uniqueness suggests ID column
            if 'id' in col.lower() or 'key' in col.lower() or 'code' in col.lower():
                return 'id'
        
        # Check for numerical
        if pd.api.types.is_numeric_dtype(col_data):
            return 'numerical'
        
        # Check for categorical
        if col_data.dtype == 'object' or pd.api.types.is_categorical_dtype(col_data):
            # If unique values are less than 50% of total, consider categorical
            if unique_ratio < 0.5 or col_data.nunique() < 20:
                return 'categorical'
        
        return 'categorical'  # Default to categorical
    
    def _get_sample_values(self, col):
        """Get sample values from column"""
        sample = self.df[col].dropna().head(5).tolist()
        return [str(val) for val in sample]
    
    def get_numerical_columns(self):
        """Get list of numerical columns"""
        if not self.analysis_result:
            self.analyze()
        return [col for col, info in self.analysis_result['columns'].items() 
                if info['type'] == 'numerical']
    
    def get_categorical_columns(self):
        """Get list of categorical columns"""
        if not self.analysis_result:
            self.analyze()
        return [col for col, info in self.analysis_result['columns'].items() 
                if info['type'] == 'categorical']
    
    def get_datetime_columns(self):
        """Get list of datetime columns"""
        if not self.analysis_result:
            self.analyze()
        return [col for col, info in self.analysis_result['columns'].items() 
                if info['type'] == 'datetime']
    
    def get_id_columns(self):
        """Get list of ID columns"""
        if not self.analysis_result:
            self.analyze()
        return [col for col, info in self.analysis_result['columns'].items() 
                if info['type'] == 'id']
