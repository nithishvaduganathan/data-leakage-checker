"""
Leakage Detection Module
Detects various types of data leakage in datasets
"""
import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression


class LeakageDetector:
    """Detects various types of data leakage"""
    
    def __init__(self, df, target_column=None):
        self.df = df
        self.target_column = target_column
        self.leakage_report = []
    
    def detect_all_leakage(self):
        """Perform comprehensive leakage detection"""
        self.leakage_report = []
        
        if self.target_column and self.target_column in self.df.columns:
            self._detect_target_leakage()
        
        self._detect_duplicate_leakage()
        self._detect_id_leakage()
        self._detect_temporal_leakage()
        
        return self.leakage_report
    
    def _detect_target_leakage(self):
        """Detect target leakage through high correlation"""
        target_data = self.df[self.target_column]
        
        # Skip if target is non-numeric
        if not pd.api.types.is_numeric_dtype(target_data):
            # Try to encode it
            try:
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                target_data = pd.Series(le.fit_transform(target_data.fillna('missing')))
            except:
                return
        
        for col in self.df.columns:
            if col == self.target_column:
                continue
            
            # Check for perfect or near-perfect correlation
            if pd.api.types.is_numeric_dtype(self.df[col]):
                corr = abs(self.df[col].corr(target_data))
                if pd.notna(corr) and corr > 0.95:
                    self.leakage_report.append({
                        'type': 'Target Leakage',
                        'severity': 'high' if corr > 0.98 else 'medium',
                        'affected_columns': [col],
                        'description': f'Column "{col}" has very high correlation ({corr:.3f}) with target',
                        'recommendation': f'Remove or investigate column "{col}" - it may be derived from target'
                    })
            
            # Check for derived features (column name contains target column name)
            if self.target_column.lower() in col.lower() and col != self.target_column:
                self.leakage_report.append({
                    'type': 'Target Leakage',
                    'severity': 'high',
                    'affected_columns': [col],
                    'description': f'Column "{col}" appears to be derived from target column',
                    'recommendation': f'Remove column "{col}" as it likely contains target information'
                })
    
    def _detect_duplicate_leakage(self):
        """Detect train-test leakage through duplicate rows"""
        duplicate_count = self.df.duplicated().sum()
        
        if duplicate_count > 0:
            duplicate_pct = (duplicate_count / len(self.df)) * 100
            
            severity = 'low'
            if duplicate_pct > 10:
                severity = 'high'
            elif duplicate_pct > 5:
                severity = 'medium'
            
            self.leakage_report.append({
                'type': 'Train-Test Leakage',
                'severity': severity,
                'affected_columns': ['all'],
                'description': f'Found {duplicate_count} duplicate rows ({duplicate_pct:.2f}% of dataset)',
                'recommendation': 'Remove duplicate rows before splitting data into train/test sets'
            })
    
    def _detect_id_leakage(self):
        """Detect leakage from ID columns"""
        for col in self.df.columns:
            # Check if column is likely an ID
            unique_ratio = self.df[col].nunique() / len(self.df)
            
            if unique_ratio > 0.95:
                is_id_column = (
                    'id' in col.lower() or 
                    'key' in col.lower() or 
                    'code' in col.lower() or
                    'index' in col.lower()
                )
                
                if is_id_column:
                    self.leakage_report.append({
                        'type': 'Train-Test Leakage',
                        'severity': 'medium',
                        'affected_columns': [col],
                        'description': f'Column "{col}" appears to be an identifier with high uniqueness',
                        'recommendation': f'Remove column "{col}" before training - IDs can cause overfitting'
                    })
    
    def _detect_temporal_leakage(self):
        """Detect temporal leakage from datetime columns"""
        datetime_cols = []
        
        for col in self.df.columns:
            if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                datetime_cols.append(col)
            elif self.df[col].dtype == 'object':
                # Try to parse as datetime
                try:
                    pd.to_datetime(self.df[col].dropna().head(100))
                    datetime_cols.append(col)
                except:
                    pass
        
        if datetime_cols:
            # Check for future information
            for col in datetime_cols:
                # Look for keywords suggesting future information
                future_keywords = ['future', 'next', 'upcoming', 'forecast', 'prediction']
                if any(keyword in col.lower() for keyword in future_keywords):
                    self.leakage_report.append({
                        'type': 'Temporal Leakage',
                        'severity': 'high',
                        'affected_columns': [col],
                        'description': f'Column "{col}" may contain future information',
                        'recommendation': f'Remove or carefully validate column "{col}" for temporal leakage'
                    })
            
            # General warning about datetime columns
            if len(datetime_cols) > 0:
                self.leakage_report.append({
                    'type': 'Temporal Leakage',
                    'severity': 'low',
                    'affected_columns': datetime_cols,
                    'description': f'Dataset contains datetime columns: {", ".join(datetime_cols)}',
                    'recommendation': 'Ensure train/test split respects temporal ordering if data is time-series'
                })
    
    def get_critical_leakage(self):
        """Get only high severity leakage issues"""
        return [issue for issue in self.leakage_report if issue['severity'] == 'high']
    
    def get_leakage_summary(self):
        """Get summary of leakage detection"""
        high_count = len([l for l in self.leakage_report if l['severity'] == 'high'])
        medium_count = len([l for l in self.leakage_report if l['severity'] == 'medium'])
        low_count = len([l for l in self.leakage_report if l['severity'] == 'low'])
        
        return {
            'total_issues': len(self.leakage_report),
            'high_severity': high_count,
            'medium_severity': medium_count,
            'low_severity': low_count,
            'has_critical_leakage': high_count > 0
        }
