"""
Visualization Module
Generates various charts and visualizations using Plotly
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import json


class DataVisualizer:
    """Generates visualizations for datasets"""
    
    def __init__(self, df):
        self.df = df
    
    def create_bar_chart(self, column, title=None):
        """Create a bar chart for categorical data"""
        if column not in self.df.columns:
            return None
        
        value_counts = self.df[column].value_counts().head(20)
        
        fig = px.bar(
            x=value_counts.index.astype(str),
            y=value_counts.values,
            labels={'x': column, 'y': 'Count'},
            title=title or f'Bar Chart: {column}'
        )
        fig.update_layout(template='plotly_white')
        
        return fig.to_json()
    
    def create_line_chart(self, x_column, y_column, title=None):
        """Create a line chart"""
        if x_column not in self.df.columns or y_column not in self.df.columns:
            return None
        
        df_sorted = self.df.sort_values(x_column)
        
        fig = px.line(
            df_sorted,
            x=x_column,
            y=y_column,
            title=title or f'Line Chart: {y_column} vs {x_column}'
        )
        fig.update_layout(template='plotly_white')
        
        return fig.to_json()
    
    def create_histogram(self, column, bins=30, title=None):
        """Create a histogram for numerical data"""
        if column not in self.df.columns:
            return None
        
        fig = px.histogram(
            self.df,
            x=column,
            nbins=bins,
            title=title or f'Histogram: {column}'
        )
        fig.update_layout(template='plotly_white')
        
        return fig.to_json()
    
    def create_box_plot(self, column, title=None):
        """Create a box plot for numerical data"""
        if column not in self.df.columns:
            return None
        
        fig = px.box(
            self.df,
            y=column,
            title=title or f'Box Plot: {column}'
        )
        fig.update_layout(template='plotly_white')
        
        return fig.to_json()
    
    def create_scatter_plot(self, x_column, y_column, color_column=None, title=None):
        """Create a scatter plot"""
        if x_column not in self.df.columns or y_column not in self.df.columns:
            return None
        
        if color_column and color_column not in self.df.columns:
            color_column = None
        
        fig = px.scatter(
            self.df,
            x=x_column,
            y=y_column,
            color=color_column,
            title=title or f'Scatter Plot: {y_column} vs {x_column}'
        )
        fig.update_layout(template='plotly_white')
        
        return fig.to_json()
    
    def create_pie_chart(self, column, title=None):
        """Create a pie chart for categorical data"""
        if column not in self.df.columns:
            return None
        
        value_counts = self.df[column].value_counts().head(10)
        
        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index.astype(str),
            title=title or f'Pie Chart: {column}'
        )
        fig.update_layout(template='plotly_white')
        
        return fig.to_json()
    
    def create_correlation_heatmap(self, columns=None, title=None):
        """Create a correlation heatmap"""
        numeric_df = self.df.select_dtypes(include=[np.number])
        
        if columns:
            numeric_df = numeric_df[[col for col in columns if col in numeric_df.columns]]
        
        if numeric_df.empty or len(numeric_df.columns) < 2:
            return None
        
        # Limit to first 20 columns for readability
        if len(numeric_df.columns) > 20:
            numeric_df = numeric_df.iloc[:, :20]
        
        corr_matrix = numeric_df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title=title or 'Correlation Heatmap',
            template='plotly_white',
            xaxis={'side': 'bottom'},
            width=800,
            height=800
        )
        
        return fig.to_json()
    
    def get_available_charts(self):
        """Get list of available chart types for each column"""
        available = {}
        
        for col in self.df.columns:
            charts = []
            
            if pd.api.types.is_numeric_dtype(self.df[col]):
                charts.extend(['histogram', 'box_plot'])
            
            if self.df[col].dtype == 'object' or self.df[col].nunique() < 20:
                charts.extend(['bar_chart', 'pie_chart'])
            
            available[col] = charts
        
        return available
    
    def get_numeric_columns(self):
        """Get list of numeric columns"""
        return self.df.select_dtypes(include=[np.number]).columns.tolist()
    
    def get_categorical_columns(self):
        """Get list of categorical columns"""
        return [col for col in self.df.columns 
                if self.df[col].dtype == 'object' or self.df[col].nunique() < 20]
