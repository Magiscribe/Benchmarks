"""
Minimal data service for test type discovery.
"""

import json
from pathlib import Path
from typing import List, Optional
from services.dsl_executor import DSLExecutor
from api.models.schemas import TestTypeInfo, ResultsRequest, ResultsResponse, ModelResult, GroupedResult


class DataService:
    """Minimal service for handling test type discovery."""
    
    def __init__(self, tests_dir: Path = None):
        """Initialize the data service with directory paths."""
        if tests_dir is None:
            tests_dir = Path(__file__).parent.parent.parent / "Tests"
            
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

    def get_available_models(self, test_type: str) -> List[str]:
        """Get list of available models for a specific test type from the results CSV."""
        # First check if we need to import pandas
        try:
            import pandas as pd
        except ImportError:
            return []
            
        results_file = Path(__file__).parent.parent.parent / "Results" / f"{test_type}_model_results.csv"
        
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
            print(f"Error loading models for {test_type}: {e}")
            return []    
        
    def get_available_filters(self, test_type: str) -> List[dict]:
        """Get list of available filters (identifier and categorical columns) for a specific test type."""
        test_dir = self.tests_dir / test_type
        format_file = test_dir / "csv_format.json"
        
        if not format_file.exists():
            return []
        
        try:
            format_config = self.dsl_executor.load_format_config(format_file)
            filters = []
            
            for column in format_config.columns:
                # Access dictionary keys, not attributes
                column_type = column['type']
                if column_type in ['identifier', 'categorical']:
                    filters.append({
                        'name': column['name'],
                        'type': column_type,
                        'description': column['description']
                    })
            
            return filters
        except Exception as e:
            print(f"Error loading filters for {test_type}: {e}")
            return []

    def get_available_filter_values(self, test_type: str, filter_name: str) -> List[str]:
        """Get list of unique values for a specific filter from the results CSV."""
        try:
            import pandas as pd
        except ImportError:
            return []
            
        results_file = Path(__file__).parent.parent.parent / "Results" / f"{test_type}_model_results.csv"
        
        if not results_file.exists():
            return []
        
        try:
            df = pd.read_csv(results_file)
            if filter_name in df.columns:                # Get unique values, sort them, and convert to list
                unique_values = sorted(df[filter_name].dropna().unique().tolist())
                # Convert numpy types to Python types for JSON serialization
                return [str(val) for val in unique_values]
            else:
                return []
        except Exception as e:
            print(f"Error loading filter values for {test_type}.{filter_name}: {e}")
            return []    
        
    def get_available_metrics(self, test_type: str) -> List[dict]:
        """Get list of available metrics for a specific test type from csv_format.json."""
        test_dir = self.tests_dir / test_type
        format_file = test_dir / "csv_format.json"
        
        if not format_file.exists():
            return []
        
        try:
            format_config = self.dsl_executor.load_format_config(format_file)
            metrics = []
            
            # Access metrics directly from the DSLFormat dataclass
            if format_config.metrics:
                for metric in format_config.metrics:
                    # Access attributes directly from DSLMetric dataclass
                    metrics.append({
                        'name': metric.name,
                        'displayName': metric.displayName,
                        'description': metric.description
                    })
            
            return metrics
        except Exception as e:
            print(f"Error loading metrics for {test_type}: {e}")
            return []

    def get_available_parameters(self, test_type: str, metric_name: str) -> List[dict]:
        """Get list of available parameters for a specific metric from csv_format.json."""
        test_dir = self.tests_dir / test_type
        format_file = test_dir / "csv_format.json"
        
        if not format_file.exists():
            return []
        
        try:
            format_config = self.dsl_executor.load_format_config(format_file)
            
            # Find the specific metric
            if format_config.metrics:
                for metric in format_config.metrics:
                    if metric.name == metric_name:                        # Check if metric has parameters
                        if hasattr(metric, 'parameters') and metric.parameters:
                            parameters = []
                            for param in metric.parameters:
                                # Parameters are stored as dictionaries, not dataclass objects
                                parameters.append({
                                    'name': param['name'],
                                    'type': param['type'],
                                    'default': param['default'],
                                    'description': param['description']
                                })
                            return parameters
                        else:
                            return []
            
            return []
        except Exception as e:
            print(f"Error loading parameters for {test_type}.{metric_name}: {e}")
            return []    
        
    def get_results(self, test_type: str, metric: str, request: ResultsRequest, group_by: Optional[List[str]] = None) -> ResultsResponse:
        """Get filtered results grouped by model with metric calculation."""
        try:
            import pandas as pd
        except ImportError:
            raise Exception("pandas is required for results processing")
            
        # Load the results CSV
        results_file = Path(__file__).parent.parent.parent / "Results" / f"{test_type}_model_results.csv"
        
        if not results_file.exists():
            raise Exception(f"No results file found for test type: {test_type}")
        
        try:
            df = pd.read_csv(results_file)
            print(f"DEBUG: Loaded CSV with {len(df)} rows and columns: {list(df.columns)}")
        except Exception as e:
            raise Exception(f"Error loading results file: {str(e)}")
        
        # Filter by selected models
        if request.selected_models:
            if 'model' not in df.columns:
                raise Exception("Results file missing 'model' column")
            df = df[df['model'].isin(request.selected_models)]

        for filter_name, selected_values in request.selected_filters.items():
            if selected_values and filter_name in df.columns:
                
                # Convert filter values to match column data type
                converted_values = []
                for value in selected_values:
                    try:
                        # Try to convert to the same type as the column
                        if df[filter_name].dtype in ['int64', 'int32', 'int16', 'int8']:
                            converted_values.append(int(value))
                        elif df[filter_name].dtype in ['float64', 'float32']:
                            converted_values.append(float(value))
                        else:
                            converted_values.append(str(value))
                    except (ValueError, TypeError):
                        # If conversion fails, keep as string
                        converted_values.append(str(value))
                
                df = df[df[filter_name].isin(converted_values)]
        
        # Group by model and calculate metrics
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
                # Create a composite key for the results dictionary
                if isinstance(group_key, tuple):
                    model_name = group_key[0]
                    group_values = group_key[1:]
                    # Create group values dictionary
                    group_dict = {col: str(val) for col, val in zip(group_by, group_values)}
                else:
                    model_name = group_key
                    group_dict = {}
                
                # Calculate metric using DSL executor
                try:
                    metric_value = self._calculate_metric(test_type, metric, group_data, request.parameter_values)
                    results.append(GroupedResult(
                        model=model_name,
                        group_values=group_dict,
                        data=ModelResult(
                            metric_value=metric_value,
                            sample_count=len(group_data)
                        )
                    ))
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    # Continue with other groups even if one fails
                    continue
        else:
            # Original behavior - group only by model
            unique_models = df['model'].unique()
            
            for model_name in unique_models:
                model_data = df[df['model'] == model_name]
                
                if len(model_data) == 0:
                    continue
                    
                # Calculate metric using DSL executor
                try:
                    metric_value = self._calculate_metric(test_type, metric, model_data, request.parameter_values)
                    results.append(GroupedResult(
                        model=model_name,
                        group_values={},
                        data=ModelResult(
                            metric_value=metric_value,
                            sample_count=len(model_data)
                        )
                    ))
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    # Continue with other models even if one fails
                    continue
        
        print(f"DEBUG: Final results: {results}")
        return ResultsResponse(
            results=results,
            test_type=test_type,
            metric=metric,
            group_by=group_by
        )

    def _calculate_metric(self, test_type: str, metric_name: str, data_df, parameter_values: dict) -> float:
        """Calculate a specific metric for the given data using DSL executor."""
        # Load the metric configuration
        test_dir = self.tests_dir / test_type
        format_file = test_dir / "csv_format.json"
        
        if not format_file.exists():
            raise Exception(f"No format configuration found for test type: {test_type}")
        
        format_config = self.dsl_executor.load_format_config(format_file)
        
        # Find the metric definition
        metric_def = None
        if format_config.metrics:
            for metric in format_config.metrics:
                if metric.name == metric_name:
                    metric_def = metric
                    break
        
        if metric_def is None:
            raise Exception(f"Metric '{metric_name}' not found in test type '{test_type}'")
        
        # Execute the metric using DSL executor
        try:
            result = self.dsl_executor.execute_metric(data_df, metric_def, parameter_values)
            
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

    def get_available_assets(self, test_type: str) -> List[str]:
        """Get list of available asset IDs for a specific test type from the assets directory."""
        test_dir = self.tests_dir / test_type / "assets"
        
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
            print(f"Error loading assets for {test_type}: {e}")
            return []


# Global instance
data_service = DataService()
