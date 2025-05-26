"""
DSL Executor for processing metric calculations defined in csv_format.json files.
Supports dynamic operations on pandas DataFrames based on configuration.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class DSLOperation:
    """Represents a single DSL operation."""
    op: str
    col: Optional[str] = None
    cols: Optional[List[str]] = None
    as_: Optional[str] = None
    condition: Optional[str] = None
    exp: Optional[Union[int, float]] = None
    value: Optional[str] = None


@dataclass
class DSLMetric:
    """Represents a metric definition from csv_format.json."""
    name: str
    displayName: str
    description: str
    steps: List[DSLOperation]
    parameters: Optional[List[Dict[str, Any]]] = None


@dataclass
class DSLFormat:
    """Represents the complete csv_format.json structure."""
    testType: str
    description: str
    columns: List[Dict[str, Any]]
    metrics: List[DSLMetric]


class DSLExecutor:
    """Executes DSL operations on pandas DataFrames."""
    
    def __init__(self):
        """Initialize the DSL executor."""
        self.variables: Dict[str, Any] = {}
        self.df: Optional[pd.DataFrame] = None
    
    def load_format_config(self, config_path: Path) -> DSLFormat:
        """
        Load and parse a csv_format.json configuration file.
        
        Args:
            config_path: Path to the csv_format.json file
            
        Returns:
            DSLFormat: Parsed configuration
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Parse metrics
        metrics = []
        for metric_data in config_data.get('metrics', []):
            steps = []
            for step_data in metric_data.get('steps', []):
                # Handle the 'as' field (Python keyword issue)
                as_field = step_data.get('as')
                step = DSLOperation(
                    op=step_data['op'],
                    col=step_data.get('col'),
                    cols=step_data.get('cols'),
                    as_=as_field,
                    condition=step_data.get('condition'),
                    exp=step_data.get('exp'),
                    value=step_data.get('value')
                )
                steps.append(step)
            
            metric = DSLMetric(
                name=metric_data['name'],
                displayName=metric_data['displayName'],
                description=metric_data['description'],
                steps=steps,
                parameters=metric_data.get('parameters')
            )
            metrics.append(metric)
        
        return DSLFormat(
            testType=config_data['testType'],
            description=config_data['description'],
            columns=config_data['columns'],
            metrics=metrics
        )
    
    def execute_metric(self, df: pd.DataFrame, metric: DSLMetric, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a single metric calculation on a DataFrame.
        
        Args:
            df: Input DataFrame
            metric: Metric definition to execute
            parameters: Optional parameters for parameterized metrics
            
        Returns:
            Any: Calculated metric value
        """
        self.df = df.copy()
        self.variables = {}
        
        # Set parameters if provided
        if parameters:
            for key, value in parameters.items():
                self.variables[f"${key}"] = value
        
        # Execute each step
        for step in metric.steps:
            self._execute_operation(step)
        
        # The last operation should be a 'return' that specifies the result
        return self.variables.get(metric.steps[-1].value) if metric.steps[-1].op == 'return' else None
    
    def _execute_operation(self, op: DSLOperation) -> None:
        """Execute a single DSL operation."""
        if op.op == "sum":
            col_data = self._get_value(op.col)
            result = col_data.sum() if hasattr(col_data, 'sum') else sum(col_data)
            if op.as_:
                self.variables[op.as_] = result
        
        elif op.op == "avg":
            col_data = self._get_value(op.col)
            result = col_data.mean() if hasattr(col_data, 'mean') else sum(col_data) / len(col_data)
            if op.as_:
                self.variables[op.as_] = result
        
        elif op.op == "count":
            try:
                col_data = self._get_value(op.col)
                if isinstance(col_data, pd.Series):
                    result = len(col_data.dropna())
                elif isinstance(col_data, pd.DataFrame):
                    result = len(col_data)
                else:
                    result = 1 if col_data is not None else 0
            except ValueError:
                # If identifier not found, return 0
                result = 0
            if op.as_:
                self.variables[op.as_] = result
        
        elif op.op == "divide":
            if len(op.cols) != 2:
                raise ValueError("Divide operation requires exactly 2 columns")
            
            col1, col2 = op.cols
            
            # Get values (could be columns or variables)
            val1 = self._get_value(col1)
            val2 = self._get_value(col2)
            
            # Handle division by zero
            if isinstance(val2, (pd.Series, np.ndarray)):
                result = val1 / val2.replace(0, np.nan)
            else:
                result = val1 / val2 if val2 != 0 else np.nan
            
            if op.as_:
                self.variables[op.as_] = result
        
        elif op.op == "filter":
            # Parse condition
            condition_str = op.condition
            
            # Replace parameter placeholders
            for var_name, var_value in self.variables.items():
                if var_name.startswith('$'):
                    condition_str = condition_str.replace(var_name, str(var_value))
            
            # Get the column data
            col_data = self._get_value(op.col)
            
            # Apply filter based on condition
            if "==" in condition_str:
                _, value = condition_str.split("==")
                value = float(value.strip()) if value.strip().replace('.', '').isdigit() else value.strip()
                mask = col_data == value
            elif ">=" in condition_str:
                _, value = condition_str.split(">=")
                value = float(value.strip())
                mask = col_data >= value
            elif "<=" in condition_str:
                _, value = condition_str.split("<=")
                value = float(value.strip())
                mask = col_data <= value
            elif ">" in condition_str:
                _, value = condition_str.split(">")
                value = float(value.strip())
                mask = col_data > value
            elif "<" in condition_str:
                _, value = condition_str.split("<")
                value = float(value.strip())
                mask = col_data < value
            else:
                raise ValueError(f"Unsupported condition: {condition_str}")
            
            # Filter the DataFrame
            filtered_df = self.df[mask] if isinstance(mask, pd.Series) else self.df
            
            if op.as_:
                self.variables[op.as_] = filtered_df
        
        elif op.op == "pow":
            col_data = self._get_value(op.col)
            result = col_data ** op.exp
            if op.as_:
                self.variables[op.as_] = result
        
        elif op.op == "sqrt":
            col_data = self._get_value(op.col)
            result = np.sqrt(col_data)
            if op.as_:
                self.variables[op.as_] = result
        
        elif op.op == "abs":
            col_data = self._get_value(op.col)
            result = np.abs(col_data)
            if op.as_:
                self.variables[op.as_] = result
        
        elif op.op == "add":
            if len(op.cols) != 2:
                raise ValueError("Add operation requires exactly 2 columns")
            
            col1, col2 = op.cols
            val1 = self._get_value(col1)
            val2 = self._get_value(col2)
            result = val1 + val2
            
            if op.as_:
                self.variables[op.as_] = result
        
        elif op.op == "max":
            col_data = self._get_value(op.col)
            result = col_data.max() if hasattr(col_data, 'max') else max(col_data)
            if op.as_:
                self.variables[op.as_] = result
        
        elif op.op == "min":
            col_data = self._get_value(op.col)
            result = col_data.min() if hasattr(col_data, 'min') else min(col_data)
            if op.as_:
                self.variables[op.as_] = result
        
        elif op.op == "stddev":
            col_data = self._get_value(op.col)
            result = col_data.std() if hasattr(col_data, 'std') else np.std(col_data)
            if op.as_:
                self.variables[op.as_] = result
        
        elif op.op == "return":
            # Return operation just marks the final result
            pass
        
        else:
            raise ValueError(f"Unsupported operation: {op.op}")
    
    def _get_value(self, identifier: str) -> Any:
        """Get value from either DataFrame column or variables."""
        if identifier in self.df.columns:
            return self.df[identifier]
        elif identifier in self.variables:
            return self.variables[identifier]
        else:
            raise ValueError(f"Unknown identifier: {identifier}")
    
    def execute_all_metrics(self, df: pd.DataFrame, format_config: DSLFormat, 
                          metric_parameters: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Execute all metrics defined in a format configuration.
        
        Args:
            df: Input DataFrame
            format_config: Complete format configuration
            metric_parameters: Optional parameters for specific metrics
            
        Returns:
            Dict[str, Any]: Results for all metrics
        """
        results = {}
        
        for metric in format_config.metrics:
            try:
                # Get parameters for this specific metric
                params = metric_parameters.get(metric.name, {}) if metric_parameters else {}
                
                # Set default parameters if defined in metric
                if metric.parameters:
                    for param_def in metric.parameters:
                        param_name = param_def['name']
                        if param_name not in params:
                            params[param_name] = param_def.get('default')
                
                result = self.execute_metric(df, metric, params)
                results[metric.name] = {
                    'value': result,
                    'displayName': metric.displayName,
                    'description': metric.description
                }
            except Exception as e:
                results[metric.name] = {
                    'error': str(e),
                    'displayName': metric.displayName,
                    'description': metric.description
                }
        
        return results


# Global instance
dsl_executor = DSLExecutor()
