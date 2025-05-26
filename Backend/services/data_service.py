"""
DSL-based data service for loading and processing benchmark results.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from services.dsl_executor import DSLExecutor, DSLFormat
from services.filter_service import filter_service
from api.models.schemas import (
    ModelResult, TestResult, DataPoint, MetricResult,
    ModelComparison, TestTypeInfo, ErrorResponse, AdvancedFilter,
    FilterCapabilities
)


class DataService:
    """Service for handling benchmark data operations using DSL executor."""
    
    def __init__(self, results_dir: Path = None, tests_dir: Path = None):
        """Initialize the data service with directory paths."""
        if results_dir is None:
            results_dir = Path(__file__).parent.parent.parent / "Results"
        if tests_dir is None:
            tests_dir = Path(__file__).parent.parent.parent / "Tests"
            
        self.results_dir = results_dir
        self.tests_dir = tests_dir
        self.dsl_executor = DSLExecutor()
    
    def get_available_test_types(self) -> List[TestTypeInfo]:
        """Get list of available test types from the Tests directory."""
        test_types = []
        
        for test_dir in self.tests_dir.iterdir():
            if test_dir.is_dir() and test_dir.name != "__pycache__":
                # Look for csv_format.json to get test info
                format_file = test_dir / "csv_format.json"
                if format_file.exists():
                    try:
                        format_config = self.dsl_executor.load_format_config(format_file)
                        
                        test_types.append(TestTypeInfo(
                            name=test_dir.name,
                            displayName=format_config.testType,
                            description=format_config.description,
                            available=True
                        ))
                    except Exception as e:
                        test_types.append(TestTypeInfo(
                            name=test_dir.name,
                            displayName=test_dir.name,
                            description=f'Test configuration error: {str(e)}',
                            available=False
                        ))
        
        return test_types
    
    def load_test_results(self, test_type: str) -> Optional[pd.DataFrame]:
        """Load results for a specific test type."""
        results_file = self.results_dir / f"{test_type}_model_results.csv"
        
        if not results_file.exists():
            return None
        
        try:
            return pd.read_csv(results_file)
        except Exception as e:
            print(f"Error loading results for {test_type}: {e}")
            return None
    
    def load_format_config(self, test_type: str) -> Optional[DSLFormat]:
        """Load DSL format configuration for a test type."""
        format_file = self.tests_dir / test_type / "csv_format.json"
        
        if not format_file.exists():
            return None
        
        try:
            return self.dsl_executor.load_format_config(format_file)
        except Exception as e:
            print(f"Error loading format config for {test_type}: {e}")
            return None
    
    def calculate_metrics(self, test_type: str, df: pd.DataFrame, 
                         metric_parameters: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Calculate all metrics for a test type using DSL."""
        format_config = self.load_format_config(test_type)
        if not format_config:
            return {}
        
        return self.dsl_executor.execute_all_metrics(df, format_config, metric_parameters)
    
    def get_model_results(self, test_type: str) -> List[ModelResult]:
        """Get results grouped by model for a specific test type."""
        df = self.load_test_results(test_type)
        if df is None:
            return []
        
        results = []
        
        for model in df['model'].unique():
            model_data = df[df['model'] == model]
            
            # Calculate metrics using DSL
            metrics = self.calculate_metrics(test_type, model_data)
            
            # Get primary accuracy metric (fallback to first metric if 'accuracy' not found)
            accuracy = 0
            if 'accuracy' in metrics and 'value' in metrics['accuracy']:
                accuracy = metrics['accuracy']['value']
            elif metrics:
                first_metric = next(iter(metrics.values()))
                if 'value' in first_metric:
                    accuracy = first_metric['value']
            
            # Create data points
            data_points = []
            for _, row in model_data.iterrows():
                data_points.append(DataPoint(
                    id=f"{row['model']}_{len(data_points)}",
                    values=row.to_dict()
                ))
            
            results.append(ModelResult(
                model=model,
                accuracy=accuracy,
                totalTests=len(model_data),
                dataPoints=data_points,
                metrics=metrics
            ))
        
        return results
    
    def get_test_results(self, test_type: str) -> List[TestResult]:
        """Get individual test results for a specific test type."""
        df = self.load_test_results(test_type)
        if df is None:
            return []
        
        # Calculate overall metrics
        overall_metrics = self.calculate_metrics(test_type, df)
        
        results = []
        for _, row in df.iterrows():
            # Calculate metrics for this single row
            single_row_df = pd.DataFrame([row])
            row_metrics = self.calculate_metrics(test_type, single_row_df)
            
            # Get primary accuracy metric
            accuracy = 0
            if 'accuracy' in row_metrics and 'value' in row_metrics['accuracy']:
                accuracy = row_metrics['accuracy']['value']
            elif 'correct' in row and 'total' in row and row['total'] > 0:
                accuracy = row['correct'] / row['total']
            
            results.append(TestResult(
                id=f"{row['model']}_{len(results)}",
                model=row['model'],
                accuracy=accuracy,
                metadata=row.to_dict(),
                metrics=row_metrics
            ))
        
        return results
    
    def get_model_comparison(self, test_type: str, models: List[str]) -> ModelComparison:
        """Compare specific models on a test type."""
        df = self.load_test_results(test_type)
        if df is None:
            return ModelComparison(models=models, metrics={}, summary="No data available")
        
        # Filter to requested models
        model_data = df[df['model'].isin(models)]
        
        metrics = {}
        for model in models:
            model_df = model_data[model_data['model'] == model]
            if len(model_df) > 0:
                # Calculate all DSL metrics for this model
                model_metrics = self.calculate_metrics(test_type, model_df)
                
                # Get primary accuracy metric
                accuracy = 0
                if 'accuracy' in model_metrics and 'value' in model_metrics['accuracy']:
                    accuracy = model_metrics['accuracy']['value']
                elif model_metrics:
                    first_metric = next(iter(model_metrics.values()))
                    if 'value' in first_metric:
                        accuracy = first_metric['value']
                
                # Extract additional metrics (excluding accuracy)
                additional_metrics = {}
                for metric_name, metric_data in model_metrics.items():
                    if metric_name != 'accuracy' and 'value' in metric_data:
                        additional_metrics[metric_name] = metric_data['value']
                
                metrics[model] = MetricResult(
                    accuracy=accuracy,
                    totalTests=len(model_df),
                    additionalMetrics=additional_metrics
                )
        
        # Generate summary based on best performing model
        if metrics:
            best_model = max(metrics.keys(), key=lambda m: metrics[m].accuracy)
            best_accuracy = metrics[best_model].accuracy
            summary = f"Best performing model: {best_model} (accuracy: {best_accuracy:.3f})"
        else:
            summary = "No valid data for comparison"
        
        return ModelComparison(
            models=models,
            metrics=metrics,
            summary=summary
        )
    
    # Filter-related methods
    def get_filter_capabilities(self, test_type: str) -> Optional[FilterCapabilities]:
        """Get filter capabilities for a test type."""
        try:
            # Load data and format config
            df = self.load_test_results(test_type)
            format_config = self.load_format_config(test_type)
            
            if df is None or format_config is None:
                return None
            
            return filter_service.get_filter_capabilities(df, format_config.dict())
        except Exception:
            return None
    
    def apply_filters(self, df: pd.DataFrame, filters: Optional[AdvancedFilter]) -> pd.DataFrame:
        """Apply filters to a dataframe as preprocessing step."""
        if filters is None or filters.is_empty():
            return df
        
        return filter_service.apply_filters(df, filters)
    
    def load_filtered_data(self, test_type: str, filters: Optional[AdvancedFilter] = None) -> Optional[pd.DataFrame]:
        """Load test data and apply filters as preprocessing step."""
        # Load raw data
        df = self.load_test_results(test_type)
        if df is None:
            return None
        
        # Apply filters if provided
        if filters is not None:
            df = self.apply_filters(df, filters)
        
        return df


# Global instance
data_service = DataService()
