"""
Preprocessing Module
Handles data cleaning and preprocessing operations
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.feature_selection import VarianceThreshold


class DataPreprocessor:
    """Handles various data preprocessing operations"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.preprocessing_log = []
    
    def handle_missing_values(self, strategy='mean', columns=None):
        """
        Handle missing values
        strategy: 'mean', 'median', 'mode', 'drop'
        """
        if columns is None:
            columns = self.df.columns
        
        for col in columns:
            if self.df[col].isnull().sum() == 0:
                continue
            
            if strategy == 'drop':
                before_count = len(self.df)
                self.df = self.df.dropna(subset=[col])
                dropped = before_count - len(self.df)
                self.preprocessing_log.append(f'Dropped {dropped} rows with missing values in "{col}"')
            
            elif strategy == 'mean' and pd.api.types.is_numeric_dtype(self.df[col]):
                mean_val = self.df[col].mean()
                self.df[col].fillna(mean_val, inplace=True)
                self.preprocessing_log.append(f'Filled missing values in "{col}" with mean: {mean_val:.2f}')
            
            elif strategy == 'median' and pd.api.types.is_numeric_dtype(self.df[col]):
                median_val = self.df[col].median()
                self.df[col].fillna(median_val, inplace=True)
                self.preprocessing_log.append(f'Filled missing values in "{col}" with median: {median_val:.2f}')
            
            elif strategy == 'mode':
                mode_val = self.df[col].mode()[0] if len(self.df[col].mode()) > 0 else 'Unknown'
                self.df[col].fillna(mode_val, inplace=True)
                self.preprocessing_log.append(f'Filled missing values in "{col}" with mode: {mode_val}')
        
        return self.df
    
    def remove_duplicates(self):
        """Remove duplicate rows"""
        before_count = len(self.df)
        self.df = self.df.drop_duplicates()
        removed_count = before_count - len(self.df)
        
        if removed_count > 0:
            self.preprocessing_log.append(f'Removed {removed_count} duplicate rows')
        
        return self.df
    
    def correct_datatypes(self):
        """Attempt to correct data types"""
        for col in self.df.columns:
            # Try to convert to numeric if possible
            if self.df[col].dtype == 'object':
                try:
                    # Check if it's actually numeric
                    self.df[col] = pd.to_numeric(self.df[col], errors='raise')
                    self.preprocessing_log.append(f'Converted "{col}" to numeric type')
                except:
                    # Try datetime
                    try:
                        self.df[col] = pd.to_datetime(self.df[col], errors='raise')
                        self.preprocessing_log.append(f'Converted "{col}" to datetime type')
                    except:
                        pass
        
        return self.df
    
    def handle_outliers(self, method='iqr', columns=None, threshold=1.5):
        """
        Handle outliers
        method: 'iqr' or 'zscore'
        """
        if columns is None:
            columns = [col for col in self.df.columns if pd.api.types.is_numeric_dtype(self.df[col])]
        
        for col in columns:
            if not pd.api.types.is_numeric_dtype(self.df[col]):
                continue
            
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outliers = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound)).sum()
                if outliers > 0:
                    # Cap outliers instead of removing
                    self.df[col] = self.df[col].clip(lower=lower_bound, upper=upper_bound)
                    self.preprocessing_log.append(f'Capped {outliers} outliers in "{col}" using IQR method')
            
            elif method == 'zscore':
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                outliers = (z_scores > 3).sum()
                if outliers > 0:
                    # Cap at 3 standard deviations
                    mean_val = self.df[col].mean()
                    std_val = self.df[col].std()
                    self.df[col] = self.df[col].clip(lower=mean_val - 3*std_val, upper=mean_val + 3*std_val)
                    self.preprocessing_log.append(f'Capped {outliers} outliers in "{col}" using Z-score method')
        
        return self.df
    
    def scale_features(self, method='standard', columns=None):
        """
        Scale numerical features
        method: 'standard' or 'minmax'
        """
        if columns is None:
            columns = [col for col in self.df.columns if pd.api.types.is_numeric_dtype(self.df[col])]
        
        for col in columns:
            if not pd.api.types.is_numeric_dtype(self.df[col]):
                continue
            
            if method == 'standard':
                scaler = StandardScaler()
                self.df[col] = scaler.fit_transform(self.df[[col]])
                self.preprocessing_log.append(f'Applied StandardScaler to "{col}"')
            
            elif method == 'minmax':
                scaler = MinMaxScaler()
                self.df[col] = scaler.fit_transform(self.df[[col]])
                self.preprocessing_log.append(f'Applied MinMaxScaler to "{col}"')
        
        return self.df
    
    def encode_categorical(self, method='label', columns=None):
        """
        Encode categorical variables
        method: 'label' or 'onehot'
        """
        if columns is None:
            columns = [col for col in self.df.columns if self.df[col].dtype == 'object']
        
        for col in columns:
            if col not in self.df.columns:
                continue
            
            if method == 'label':
                le = LabelEncoder()
                # Handle missing values
                self.df[col] = self.df[col].fillna('missing')
                self.df[col] = le.fit_transform(self.df[col].astype(str))
                self.preprocessing_log.append(f'Applied Label Encoding to "{col}"')
            
            elif method == 'onehot':
                # Only for columns with reasonable number of categories
                if self.df[col].nunique() <= 10:
                    dummies = pd.get_dummies(self.df[col], prefix=col, drop_first=True)
                    self.df = pd.concat([self.df.drop(col, axis=1), dummies], axis=1)
                    self.preprocessing_log.append(f'Applied One-Hot Encoding to "{col}"')
                else:
                    self.preprocessing_log.append(f'Skipped One-Hot Encoding for "{col}" (too many categories)')
        
        return self.df
    
    def feature_selection(self, method='correlation', threshold=0.95, target_column=None):
        """
        Perform feature selection
        method: 'correlation' or 'variance'
        """
        if method == 'correlation':
            # Remove highly correlated features
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                corr_matrix = self.df[numeric_cols].corr().abs()
                upper_triangle = corr_matrix.where(
                    np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
                )
                
                to_drop = []
                for col in upper_triangle.columns:
                    if any(upper_triangle[col] > threshold):
                        if col != target_column:  # Don't drop target
                            to_drop.append(col)
                
                if to_drop:
                    self.df = self.df.drop(columns=to_drop)
                    self.preprocessing_log.append(f'Removed {len(to_drop)} highly correlated features: {", ".join(to_drop)}')
        
        elif method == 'variance':
            # Remove low variance features
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                selector = VarianceThreshold(threshold=0.01)
                try:
                    selector.fit(self.df[numeric_cols])
                    low_variance_cols = [col for col, var in zip(numeric_cols, selector.variances_) if var < 0.01]
                    
                    if low_variance_cols and target_column not in low_variance_cols:
                        self.df = self.df.drop(columns=low_variance_cols)
                        self.preprocessing_log.append(f'Removed {len(low_variance_cols)} low variance features')
                except:
                    pass
        
        return self.df
    
    def remove_columns(self, columns):
        """Remove specific columns"""
        columns_to_remove = [col for col in columns if col in self.df.columns]
        if columns_to_remove:
            self.df = self.df.drop(columns=columns_to_remove)
            self.preprocessing_log.append(f'Removed columns: {", ".join(columns_to_remove)}')
        
        return self.df
    
    def get_preprocessing_log(self):
        """Get log of all preprocessing operations"""
        return self.preprocessing_log
    
    def get_processed_dataframe(self):
        """Get the processed dataframe"""
        return self.df
