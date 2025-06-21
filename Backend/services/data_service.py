"""
Minimal data service for test type discovery.
"""

import json
from pathlib import Path
from typing import List, Optional
from services.dsl_executor import DSLExecutor
from api.models.schemas import ResultsRequest, ResultsResponse, ResultItem


class DataService:
    """Minimal service for handling test type discovery."""
    
    def __init__(self, tests_dir: Path = None):
        """Initialize the data service with directory paths."""
        if tests_dir is None:
            tests_dir = Path(__file__).parent.parent.parent / "Tests"
            
        self.tests_dir = tests_dir
        self.dsl_executor = DSLExecutor()
    
    def get_available_models(self, benchmark_id: str) -> List[str]:
        """Get list of available models for a specific test type from the results CSV."""
        # First check if we need to import pandas
        try:
            import pandas as pd
        except ImportError:
            return []
            
        results_file = Path(__file__).parent.parent.parent / "Results" / f"{benchmark_id}_model_results.csv"
        
        if not results_file.exists():
            return []
        
        try:
            df = pd.read_csv(results_file)
            if 'model' in df.columns:
                models = sorted(df['model'].unique().tolist())
                return models
            else:
                return []
        except Exception as e:
            print(f"Error loading models for {benchmark_id}: {e}")
            return []

    def _calculate_metric(self, benchmark_id: str, metric_name: str, data_df) -> float:
        """Calculate a specific metric for the given data using DSL executor."""
        # Load the metric configuration
        test_dir = self.tests_dir / benchmark_id
        format_file = test_dir / "csv_format.json"
        
        if not format_file.exists():
            raise Exception(f"No format configuration found for test type: {benchmark_id}")
        
        format_config = self.dsl_executor.load_format_config(format_file)
          # Find the metric definition
        metric_def = None
        if format_config.metrics:
            for metric in format_config.metrics:
                if metric.id == metric_name:
                    metric_def = metric
                    break
        
        if metric_def is None:
            raise Exception(f"Metric '{metric_name}' not found in test type '{benchmark_id}'")
        
        # Execute the metric using DSL executor
        try:
            result = self.dsl_executor.execute_metric(data_df, metric_def)
            
            # The result should be a single numeric value
            if isinstance(result, (int, float)):
                return float(result)
            elif hasattr(result, 'iloc') and len(result) > 0:
                # If it's a pandas Series/DataFrame, get the first value
                return float(result.iloc[0] if hasattr(result, 'iloc') else result[0])
            else:
                # Try to convert to float
                return float(result)
                
        except Exception as e:
            raise Exception(f"Error executing metric '{metric_name}': {str(e)}")

    def get_available_assets(self, benchmark_id: str) -> List[str]:
        """Get list of available asset IDs for a specific test type from the assets directory."""
        test_dir = self.tests_dir / benchmark_id / "assets"
        
        if not test_dir.exists():
            return []
        
        try:
            assets = []
            # Look for PNG files in the assets directory
            for asset_file in test_dir.glob("*.png"):
                # Remove the .png extension to get the asset ID
                asset_id = asset_file.stem
                assets.append(asset_id)
            
            return sorted(assets)
        except Exception as e:
            print(f"Error loading assets for {benchmark_id}: {e}")
            return []

    def get_benchmarks(self) -> List[dict]:
        """Get list of available benchmarks in API contract format."""
        benchmarks = []
        
        for test_dir in self.tests_dir.iterdir():
            if test_dir.is_dir() and test_dir.name != "__pycache__":
                # Look for csv_format.json to get test info
                format_file = test_dir / "csv_format.json"
                if format_file.exists():
                    try:
                        format_config = self.dsl_executor.load_format_config(format_file)
                        
                        benchmarks.append({
                            "id": test_dir.name,
                            "name": format_config.benchmark,
                            "description": format_config.description
                        })
                    except Exception as e:
                        # Skip benchmarks with configuration errors
                        print(f"Skipping benchmark {test_dir.name}: {str(e)}")
                        continue
        
        return benchmarks

    def get_benchmark_metrics(self, benchmark_id: str) -> List[dict]:
        """Get list of available metrics for a specific benchmark in API contract format."""
        test_dir = self.tests_dir / benchmark_id
        format_file = test_dir / "csv_format.json"
        
        if not format_file.exists():
            return []
        
        try:
            format_config = self.dsl_executor.load_format_config(format_file)
            metrics = []
              # Access metrics directly from the DSLFormat dataclass
            if format_config.metrics:
                for metric in format_config.metrics:
                    # API contract format: id, name, description - LIKE A REAL G!
                    metrics.append({
                        'id': metric.id,
                        'name': metric.name,
                        'description': metric.description
                    })
            
            return metrics
        except Exception as e:
            print(f"Error loading metrics for {benchmark_id}: {e}")
            return []

    def get_benchmark_filters(self, benchmark_id: str) -> dict:
        """Get available filters for a specific benchmark in API contract format."""
        # Get filter metadata from csv_format.json
        test_dir = self.tests_dir / benchmark_id
        format_file = test_dir / "csv_format.json"
        
        if not format_file.exists():
            return {}
        
        # Load CSV data for unique values
        try:
            import pandas as pd
        except ImportError:
            return {}
            
        results_file = Path(__file__).parent.parent.parent / "Results" / f"{benchmark_id}_model_results.csv"
        
        if not results_file.exists():
            return {}
        
        try:
            # Load format config to find filterable columns
            format_config = self.dsl_executor.load_format_config(format_file)
            
            # Load CSV data
            df = pd.read_csv(results_file)
            
            filters = {}
            
            # Process each column that can be filtered
            for column in format_config.columns:
                column_type = column['type']
                column_name = column['name']
                
                # Only include categorical and identifier columns (not quantitative or entity)
                if column_type in ['categorical', 'identifier'] and column_name in df.columns:
                    # Get unique values, sort them, and convert to strings
                    unique_values = sorted(df[column_name].dropna().unique().tolist())
                    filters[column_name] = [str(val) for val in unique_values]
            
            return filters
            
        except Exception as e:
            print(f"Error loading filters for {benchmark_id}: {e}")
            return {}
    
    def get_benchmark_results(self, benchmark_id: str, metric_id: str, request: ResultsRequest, group_by: Optional[List[str]] = None) -> ResultsResponse:
        """Get filtered results in API contract format."""
        try:
            import pandas as pd
        except ImportError:
            raise Exception("pandas is required for results processing")
            
        # Load the results CSV
        results_file = Path(__file__).parent.parent.parent / "Results" / f"{benchmark_id}_model_results.csv"
        
        if not results_file.exists():
            raise Exception(f"No results file found for benchmark: {benchmark_id}")
        
        try:
            df = pd.read_csv(results_file)
        except Exception as e:
            raise Exception(f"Error loading results file: {str(e)}")
        
        # Filter by models (API contract uses 'models' not 'selected_models')
        if request.models:
            if 'model' not in df.columns:
                raise Exception("Results file missing 'model' column")
            df = df[df['model'].isin(request.models)]

        # Filter by filters (API contract uses 'filters' not 'selected_filters')
        for filter_name, selected_values in request.filters.items():
            if selected_values and filter_name in df.columns:
                # Convert filter values to match column data type
                converted_values = []
                for value in selected_values:
                    try:
                        if df[filter_name].dtype in ['int64', 'int32', 'int16', 'int8']:
                            converted_values.append(int(value))
                        elif df[filter_name].dtype in ['float64', 'float32']:
                            converted_values.append(float(value))
                        else:
                            converted_values.append(str(value))
                    except (ValueError, TypeError):
                        converted_values.append(str(value))
                
                df = df[df[filter_name].isin(converted_values)]
        
        # Build results in API contract format
        results = []
        
        if 'model' not in df.columns:
            raise Exception("Results file missing 'model' column")
            
        if group_by:
            # Verify all group_by columns exist
            missing_cols = [col for col in group_by if col not in df.columns]
            if missing_cols:
                raise Exception(f"Group by columns not found in data: {missing_cols}")
            
            # Group by both model and additional columns
            group_cols = ['model'] + group_by
            grouped = df.groupby(group_cols)
            
            for group_key, group_data in grouped:
                if isinstance(group_key, tuple):
                    model_name = group_key[0]
                    group_values = [str(val) for val in group_key[1:]]  # Convert to groupings array
                else:
                    model_name = group_key
                    group_values = []
                
                # Calculate metric using DSL executor
                try:
                    metric_value = self._calculate_metric(benchmark_id, metric_id, group_data)
                    results.append(ResultItem(
                        model=model_name,
                        groupings=group_values,
                        value=metric_value
                    ))
                except Exception as e:
                    # Continue with other groups even if one fails
                    continue
        else:
            # No grouping - empty groupings array
            unique_models = df['model'].unique()
            
            for model_name in unique_models:
                model_data = df[df['model'] == model_name]
                
                if len(model_data) == 0:
                    continue
                    
                # Calculate metric using DSL executor
                try:
                    metric_value = self._calculate_metric(benchmark_id, metric_id, model_data)
                    results.append(ResultItem(
                        model=model_name,
                        groupings=[],  # No grouping = empty array
                        value=metric_value
                    ))
                except Exception as e:
                    # Continue with other models even if one fails
                    continue
        
        return ResultsResponse(
            results=results,
            metric=metric_id
        )

# Global instance
data_service = DataService()
