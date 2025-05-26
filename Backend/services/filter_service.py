"""
Filter Service for preprocessing benchmark data.
Handles all filtering operations independently of DSL execution.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
from api.models.schemas import AdvancedFilter, FilterCondition, FilterGroup, FilterMetadata, FilterCapabilities


class FilterService:
    """Service for filtering benchmark data based on column metadata and conditions."""
    
    def __init__(self):
        """Initialize the filter service."""
        pass
    
    def get_filter_capabilities(self, df: pd.DataFrame, format_config: dict) -> FilterCapabilities:
        """
        Get comprehensive filter capabilities for a dataset based on its format configuration.
        
        Args:
            df: The dataframe to analyze
            format_config: The csv_format.json configuration
            
        Returns:
            FilterCapabilities with metadata for all filterable columns
        """
        columns = []
        
        for column_def in format_config.get('columns', []):
            col_name = column_def.get('name')
            col_type = column_def.get('type')
            
            if col_name not in df.columns:
                continue
                
            # Define operators based on column type
            operators = self._get_operators_for_type(col_type)
            
            # Get display name and description
            display_name = column_def.get('displayName', col_name.replace('_', ' ').title())
            description = column_def.get('description', f"{display_name} values")
            
            filter_metadata = FilterMetadata(
                column=col_name,
                type=col_type,
                displayName=display_name,
                description=description,
                operators=operators
            )
            
            # Add values for categorical/entity/identifier columns
            if col_type in ['categorical', 'entity', 'identifier']:
                unique_values = sorted(df[col_name].dropna().unique().tolist())
                filter_metadata.values = unique_values
            
            # Add range for quantitative columns
            elif col_type == 'quantitative':
                if df[col_name].dtype in ['int64', 'float64']:
                    filter_metadata.range = {
                        'min': float(df[col_name].min()),
                        'max': float(df[col_name].max())
                    }
            
            columns.append(filter_metadata)
        
        return FilterCapabilities(
            test_type=format_config.get('testType', ''),
            columns=columns
        )
    
    def apply_filters(self, df: pd.DataFrame, filters: AdvancedFilter) -> pd.DataFrame:
        """
        Apply advanced filters to a dataframe.
        
        Args:
            df: The dataframe to filter
            filters: The filter configuration
            
        Returns:
            Filtered dataframe
        """
        if filters.is_empty():
            return df
        
        # Combine all filter groups with OR logic
        group_masks = []
        
        for group in filters.groups:
            # Combine conditions within group with group's operator (AND/OR)
            condition_masks = []
            
            for condition in group.conditions:
                mask = self._apply_condition(df, condition)
                condition_masks.append(mask)
            
            if condition_masks:
                if group.operator.upper() == 'OR':
                    group_mask = pd.concat(condition_masks, axis=1).any(axis=1)
                else:  # AND
                    group_mask = pd.concat(condition_masks, axis=1).all(axis=1)
                
                group_masks.append(group_mask)
        
        # Combine groups with OR logic (any group can match)
        if group_masks:
            final_mask = pd.concat(group_masks, axis=1).any(axis=1)
            return df[final_mask]
        
        return df
    
    def _apply_condition(self, df: pd.DataFrame, condition: FilterCondition) -> pd.Series:
        """
        Apply a single filter condition to a dataframe.
        
        Args:
            df: The dataframe
            condition: The filter condition
            
        Returns:
            Boolean mask series
        """
        column = condition.column
        operator = condition.operator.lower()
        value = condition.value
        
        if column not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        
        col_data = df[column]
        
        if operator == 'eq':
            return col_data == value
        elif operator == 'in':
            if isinstance(value, list):
                return col_data.isin(value)
            else:
                return col_data == value
        elif operator == 'not_in':
            if isinstance(value, list):
                return ~col_data.isin(value)
            else:
                return col_data != value
        elif operator == 'gt':
            return col_data > value
        elif operator == 'gte':
            return col_data >= value
        elif operator == 'lt':
            return col_data < value
        elif operator == 'lte':
            return col_data <= value
        elif operator == 'between':
            if isinstance(value, dict) and 'min' in value and 'max' in value:
                return (col_data >= value['min']) & (col_data <= value['max'])
            elif isinstance(value, list) and len(value) == 2:
                return (col_data >= value[0]) & (col_data <= value[1])
            else:
                return pd.Series([False] * len(df), index=df.index)
        elif operator == 'contains':
            return col_data.astype(str).str.contains(str(value), case=False, na=False)
        elif operator == 'starts_with':
            return col_data.astype(str).str.startswith(str(value), na=False)
        elif operator == 'ends_with':
            return col_data.astype(str).str.endswith(str(value), na=False)
        elif operator == 'is_null':
            return col_data.isnull()
        elif operator == 'is_not_null':
            return col_data.notnull()
        else:
            # Unknown operator, return all False
            return pd.Series([False] * len(df), index=df.index)
    
    def _get_operators_for_type(self, col_type: str) -> List[str]:
        """
        Get available operators for a column type.
        
        Args:
            col_type: The column type from format configuration
            
        Returns:
            List of available operators
        """
        if col_type in ['categorical', 'entity', 'identifier']:
            return ['eq', 'in', 'not_in', 'is_null', 'is_not_null']
        elif col_type == 'quantitative':
            return ['eq', 'gt', 'gte', 'lt', 'lte', 'between', 'is_null', 'is_not_null']
        elif col_type == 'text':
            return ['eq', 'contains', 'starts_with', 'ends_with', 'is_null', 'is_not_null']
        else:
            # Default operators for unknown types
            return ['eq', 'in', 'not_in', 'contains', 'is_null', 'is_not_null']
    
    def create_simple_filter(self, column: str, operator: str, value: Any) -> AdvancedFilter:
        """
        Create a simple single-condition filter.
        
        Args:
            column: Column name
            operator: Filter operator
            value: Filter value
            
        Returns:
            AdvancedFilter with single condition
        """
        condition = FilterCondition(column=column, operator=operator, value=value)
        group = FilterGroup(operator="AND", conditions=[condition])
        return AdvancedFilter(groups=[group])
    
    def create_multi_filter(self, conditions: List[tuple], group_operator: str = "AND") -> AdvancedFilter:
        """
        Create a filter with multiple conditions.
        
        Args:
            conditions: List of (column, operator, value) tuples
            group_operator: How to combine conditions ("AND" or "OR")
            
        Returns:
            AdvancedFilter with multiple conditions
        """
        filter_conditions = []
        for column, operator, value in conditions:
            filter_conditions.append(FilterCondition(column=column, operator=operator, value=value))
        
        group = FilterGroup(operator=group_operator, conditions=filter_conditions)
        return AdvancedFilter(groups=[group])


# Global filter service instance
filter_service = FilterService()
