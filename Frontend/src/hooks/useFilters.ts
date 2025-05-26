import { useState, useEffect } from 'react';
import { FilterColumn } from '../types/dashboard';

const API_BASE = `${import.meta.env.VITE_API_URL}/api/data`;

export const useFilters = (testType: string) => {
  const [availableFilters, setAvailableFilters] = useState<FilterColumn[]>([]);
  const [filterValues, setFilterValues] = useState<Record<string, string[]>>({});
  const [selectedFilterValues, setSelectedFilterValues] = useState<Record<string, string[]>>({});

  const fetchAvailableFilters = async (testType: string) => {
    try {
      const response = await fetch(`${API_BASE}/available-filters/${testType}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const filters: FilterColumn[] = await response.json();
      setAvailableFilters(filters);
      
      // Fetch values for each filter
      const filterValuesMap: Record<string, string[]> = {};
      const selectedValuesMap: Record<string, string[]> = {};
      
      for (const filter of filters) {
        try {
          const valuesResponse = await fetch(`${API_BASE}/available-filter-values/${testType}/${filter.name}`);
          if (valuesResponse.ok) {
            const values: string[] = await valuesResponse.json();
            filterValuesMap[filter.name] = values;
            // Select all values by default
            selectedValuesMap[filter.name] = [...values];
          }
        } catch (err) {
          console.error(`Error fetching values for filter ${filter.name}:`, err);
          filterValuesMap[filter.name] = [];
          selectedValuesMap[filter.name] = [];
        }
      }
      
      setFilterValues(filterValuesMap);
      setSelectedFilterValues(selectedValuesMap);
    } catch (err) {
      console.error('Error fetching available filters:', err);
      setAvailableFilters([]);
      setFilterValues({});
      setSelectedFilterValues({});
    }
  };

  useEffect(() => {
    if (testType) {
      fetchAvailableFilters(testType);
    } else {
      setAvailableFilters([]);
      setFilterValues({});
      setSelectedFilterValues({});
    }
  }, [testType]);

  const handleFilterValueSelection = (filterName: string, value: string) => {
    setSelectedFilterValues(prev => ({
      ...prev,
      [filterName]: prev[filterName]?.includes(value)
        ? prev[filterName].filter(v => v !== value)
        : [...(prev[filterName] || []), value]
    }));
  };

  const selectAllFilterValues = (filterName: string) => {
    setSelectedFilterValues(prev => ({
      ...prev,
      [filterName]: [...(filterValues[filterName] || [])]
    }));
  };

  const selectNoFilterValues = (filterName: string) => {
    setSelectedFilterValues(prev => ({
      ...prev,
      [filterName]: []
    }));
  };

  return {
    availableFilters,
    filterValues,
    selectedFilterValues,
    handleFilterValueSelection,
    selectAllFilterValues,
    selectNoFilterValues
  };
};
