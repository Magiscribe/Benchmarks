"""
Data service for processing LLM Eye Test CSV results.
Handles dynamic data loading, filtering, and accuracy calculations.
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Optional
from api.models.schemas import FilterOptions, AccuracyData, AccuracyRequest

class DataService:
    """Service class for handling CSV data operations."""
    
    def __init__(self):
        """Initialize the data service and load CSV data."""
        self.results_path = Path(__file__).parent.parent.parent / "Results"
        self.csv_file = self.results_path / "Eye_Test_model_results.csv"
        self.df = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Load the CSV data into a pandas DataFrame."""
        if not self.csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_file}")
        
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"✅ Loaded {len(self.df)} rows from {self.csv_file}")
        except Exception as e:
            raise Exception(f"Failed to load CSV data: {str(e)}")
    
    def get_filter_options(self) -> FilterOptions:
        """
        Dynamically extract unique filter options from the CSV data.
        
        Returns:
            FilterOptions: Available models, fonts, and sizes
        """
        if self.df is None:
            raise Exception("Data not loaded")
        
        return FilterOptions(
            models=sorted(self.df['model'].unique().tolist()),
            fonts=sorted(self.df['font'].unique().tolist()),
            sizes=sorted(self.df['size'].unique().tolist())
        )
    
    def calculate_accuracy(self, request: AccuracyRequest) -> List[AccuracyData]:
        """
        Calculate accuracy data based on filter criteria.
        
        Args:
            request: Filter criteria (fonts, sizes, models)
            
        Returns:
            List[AccuracyData]: Accuracy results per model
        """
        if self.df is None:
            raise Exception("Data not loaded")
        
        # Start with full dataset
        filtered_df = self.df.copy()
        
        # Apply filters
        if request.fonts:
            filtered_df = filtered_df[filtered_df['font'].isin(request.fonts)]
        
        if request.sizes:
            filtered_df = filtered_df[filtered_df['size'].isin(request.sizes)]
        
        if request.models:
            filtered_df = filtered_df[filtered_df['model'].isin(request.models)]
        
        # Group by model and calculate accuracy
        accuracy_results = []
        
        if len(filtered_df) == 0:
            return accuracy_results
        
        grouped = filtered_df.groupby('model').agg({
            'correct': 'sum',
            'total': 'sum'
        }).reset_index()
        
        for _, row in grouped.iterrows():
            total_correct = int(row['correct'])
            total_attempts = int(row['total'])
            accuracy = total_correct / total_attempts if total_attempts > 0 else 0.0
            
            accuracy_results.append(AccuracyData(
                model=row['model'],
                accuracy=round(accuracy, 4),
                total_correct=total_correct,
                total_attempts=total_attempts
            ))
        
        # Sort by accuracy descending
        accuracy_results.sort(key=lambda x: x.accuracy, reverse=True)
        
        return accuracy_results
    
    def get_raw_data(self, limit: Optional[int] = None) -> Dict:
        """
        Get raw CSV data for debugging purposes.
        
        Args:
            limit: Optional limit on number of rows
            
        Returns:
            Dict: Raw data and metadata
        """
        if self.df is None:
            raise Exception("Data not loaded")
        
        df_subset = self.df.head(limit) if limit else self.df
        
        return {
            "total_rows": len(self.df),
            "returned_rows": len(df_subset),
            "columns": self.df.columns.tolist(),
            "data": df_subset.to_dict('records')
        }

# Global instance
data_service = DataService()
