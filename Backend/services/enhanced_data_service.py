"""
Enhanced data service that supports multiple test types and DSL execution.
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from api.models.schemas import (
    FilterOptions, AccuracyData, AccuracyRequest, MetricRequest, 
    MetricsResponse, MetricResult, AvailableTest, AvailableTestsResponse
)
from services.dsl_executor import dsl_executor, DSLFormat


class EnhancedDataService:
    """Enhanced service class for handling multiple test types with DSL support."""
    
    def __init__(self):
        """Initialize the enhanced data service."""
        self.project_root = Path(__file__).parent.parent.parent
        self.results_path = self.project_root / "Results"
        self.tests_path = self.project_root / "Tests"
        
        # Cache for loaded data and configurations
        self._data_cache: Dict[str, pd.DataFrame] = {}
        self._config_cache: Dict[str, DSLFormat] = {}
        
        self._discover_tests()
    
    def _discover_tests(self) -> None:
        """Discover available test types and their configurations."""
        self.available_tests = {}
        
        if not self.tests_path.exists():
            print(f"⚠️  Tests directory not found: {self.tests_path}")
            return
        
        for test_dir in self.tests_path.iterdir():
            if test_dir.is_dir() and not test_dir.name.startswith('.'):
                config_file = test_dir / "csv_format.json"
                if config_file.exists():
                    try:
                        config = dsl_executor.load_format_config(config_file)
                        self.available_tests[config.testType] = {
                            'config': config,
                            'config_path': config_file,
                            'test_dir': test_dir
                        }
                        print(f"✅ Discovered test type: {config.testType}")
                    except Exception as e:
                        print(f"⚠️  Failed to load config for {test_dir.name}: {e}")
    
    def get_available_tests(self) -> AvailableTestsResponse:
        """Get information about all available test types."""
        tests = []
        
        for test_type, test_info in self.available_tests.items():
            config = test_info['config']
            
            # Check if CSV results file exists
            csv_path = self.results_path / f"{test_type}_model_results.csv"
            csv_exists = csv_path.exists()
            
            metrics_info = []
            for metric in config.metrics:
                metrics_info.append({
                    'name': metric.name,
                    'displayName': metric.displayName,
                    'description': metric.description,
                    'hasParameters': metric.parameters is not None
                })
            
            test = AvailableTest(
                test_type=test_type,
                description=config.description,
                columns=config.columns,
                metrics=metrics_info,
                csv_path=str(csv_path) if csv_exists else None
            )
            tests.append(test)
        
        return AvailableTestsResponse(tests=tests)
    
    def _load_test_data(self, test_type: str) -> pd.DataFrame:
        """Load CSV data for a specific test type."""
        if test_type in self._data_cache:
            return self._data_cache[test_type]
        
        csv_file = self.results_path / f"{test_type}_model_results.csv"
        if not csv_file.exists():
            raise FileNotFoundError(f"Results file not found: {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            self._data_cache[test_type] = df
            print(f"✅ Loaded {len(df)} rows for {test_type}")
            return df
        except Exception as e:
            raise Exception(f"Failed to load CSV data for {test_type}: {str(e)}")
    
    def _get_test_config(self, test_type: str) -> DSLFormat:
        """Get configuration for a specific test type."""
        if test_type not in self.available_tests:
            raise ValueError(f"Unknown test type: {test_type}")
        
        if test_type not in self._config_cache:
            config_path = self.available_tests[test_type]['config_path']
            config = dsl_executor.load_format_config(config_path)
            self._config_cache[test_type] = config
        
        return self._config_cache[test_type]
    
    def calculate_metrics(self, request: MetricRequest) -> MetricsResponse:
        """
        Calculate metrics using DSL for a specific test type.
        
        Args:
            request: Metric calculation request
            
        Returns:
            MetricsResponse: Calculated metrics with metadata
        """
        # Load data and configuration
        df = self._load_test_data(request.test_type)
        config = self._get_test_config(request.test_type)
        
        # Apply filters if provided
        filtered_df = df.copy()
        if request.filters:
            for column, values in request.filters.items():
                if column in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[column].isin(values)]
        
        # Determine which metrics to calculate
        metrics_to_calculate = config.metrics
        if request.metric_names:
            metrics_to_calculate = [m for m in config.metrics if m.name in request.metric_names]
        
        # Calculate metrics
        results = []
        success_count = 0
        error_count = 0
        
        for metric in metrics_to_calculate:
            try:
                # Get parameters for this metric
                params = {}
                if request.parameters and metric.name in request.parameters:
                    params = request.parameters[metric.name]
                
                # Set default parameters if defined in metric and not provided
                if metric.parameters:
                    for param_def in metric.parameters:
                        param_name = param_def['name']
                        if param_name not in params:
                            params[param_name] = param_def.get('default')
                
                value = dsl_executor.execute_metric(filtered_df, metric, params)
                
                result = MetricResult(
                    name=metric.name,
                    display_name=metric.displayName,
                    description=metric.description,
                    value=value
                )
                success_count += 1
                
            except Exception as e:
                result = MetricResult(
                    name=metric.name,
                    display_name=metric.displayName,
                    description=metric.description,
                    error=str(e)
                )
                error_count += 1
            
            results.append(result)
        
        return MetricsResponse(
            test_type=request.test_type,
            metrics=results,
            filters_applied=request.filters,
            total_rows_processed=len(filtered_df),
            success_count=success_count,
            error_count=error_count
        )
    
    def get_filter_options_for_test(self, test_type: str) -> Dict[str, List]:
        """Get available filter options for a specific test type."""
        df = self._load_test_data(test_type)
        config = self._get_test_config(test_type)
        
        options = {}
        for column_def in config.columns:
            column_name = column_def['name']
            if column_name in df.columns:
                # Get unique values, handling different data types
                unique_values = df[column_name].dropna().unique()
                
                # Convert to appropriate Python types and sort
                if column_def['type'] in ['quantitative']:
                    # Numeric values
                    try:
                        unique_values = sorted([float(x) for x in unique_values if pd.notna(x)])
                    except (ValueError, TypeError):
                        unique_values = sorted([str(x) for x in unique_values])
                else:
                    # String/categorical values
                    unique_values = sorted([str(x) for x in unique_values])
                
                options[column_name] = unique_values
        
        return options
    
    # Legacy methods for backward compatibility
    def get_filter_options(self) -> FilterOptions:
        """Legacy method - get filter options for Eye_Test (backward compatibility)."""
        try:
            options = self.get_filter_options_for_test("Eye_Test")
            return FilterOptions(
                models=options.get('model', []),
                fonts=options.get('font', []),
                sizes=[int(x) for x in options.get('size', []) if str(x).isdigit()]
            )
        except Exception:
            # Fallback to empty options
            return FilterOptions(models=[], fonts=[], sizes=[])
    
    def calculate_accuracy(self, request: AccuracyRequest) -> List[AccuracyData]:
        """Legacy method - calculate accuracy for Eye_Test (backward compatibility)."""
        try:
            df = self._load_test_data("Eye_Test")
        except FileNotFoundError:
            return []
        
        # Apply filters
        filtered_df = df.copy()
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
    
    def get_raw_data(self, limit: Optional[int] = None, test_type: str = "Eye_Test") -> Dict:
        """Get raw CSV data for debugging purposes."""
        try:
            df = self._load_test_data(test_type)
        except FileNotFoundError:
            return {"error": f"No data found for test type: {test_type}"}
        
        df_subset = df.head(limit) if limit else df
        
        return {
            "test_type": test_type,
            "total_rows": len(df),
            "returned_rows": len(df_subset),
            "columns": df.columns.tolist(),
            "data": df_subset.to_dict('records')
        }


# Global instance
enhanced_data_service = EnhancedDataService()
