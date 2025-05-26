import { useState, useEffect } from 'react';
import { Metric, MetricParameter } from '../types/dashboard';

const API_BASE = `${import.meta.env.VITE_API_URL}/api/data`;

export const useMetrics = (testType: string) => {
  const [availableMetrics, setAvailableMetrics] = useState<Metric[]>([]);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [availableParameters, setAvailableParameters] = useState<Record<string, MetricParameter[]>>({});
  const [parameterValues, setParameterValues] = useState<Record<string, Record<string, any>>>({});

  const fetchAvailableMetrics = async (testType: string) => {
    try {
      const response = await fetch(`${API_BASE}/available-metrics/${testType}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const metrics: Metric[] = await response.json();
      setAvailableMetrics(metrics);
      // Auto-select first two metrics by default
      const defaultSelection = metrics.slice(0, 2).map(m => m.name);
      setSelectedMetrics(defaultSelection);
    } catch (err) {
      console.error('Error fetching available metrics:', err);
      setAvailableMetrics([]);
      setSelectedMetrics([]);
    }
  };

  const fetchParametersForMetrics = async (testType: string, metrics: string[]) => {
    try {
      const parametersMap: Record<string, MetricParameter[]> = {};
      const valuesMap: Record<string, Record<string, any>> = {};
      
      for (const metric of metrics) {
        try {
          const response = await fetch(`${API_BASE}/available-parameters/${testType}/${metric}`);
          if (response.ok) {
            const parameters: MetricParameter[] = await response.json();
            parametersMap[metric] = parameters;
            
            // Initialize parameter values with defaults
            const defaultValues: Record<string, any> = {};
            parameters.forEach(param => {
              defaultValues[param.name] = param.default;
            });
            valuesMap[metric] = defaultValues;
          }
        } catch (err) {
          console.error(`Error fetching parameters for metric ${metric}:`, err);
          parametersMap[metric] = [];
          valuesMap[metric] = {};
        }
      }
      
      setAvailableParameters(parametersMap);
      setParameterValues(valuesMap);
    } catch (err) {
      console.error('Error fetching parameters for metrics:', err);
      setAvailableParameters({});
      setParameterValues({});
    }
  };

  useEffect(() => {
    if (testType) {
      fetchAvailableMetrics(testType);
    } else {
      setAvailableMetrics([]);
      setSelectedMetrics([]);
      setAvailableParameters({});
      setParameterValues({});
    }
  }, [testType]);

  useEffect(() => {
    if (testType && selectedMetrics.length > 0) {
      fetchParametersForMetrics(testType, selectedMetrics);
    } else {
      setAvailableParameters({});
      setParameterValues({});
    }
  }, [testType, selectedMetrics]);

  const handleMetricSelection = (metric: string) => {
    setSelectedMetrics(prev => 
      prev.includes(metric) 
        ? prev.filter(m => m !== metric)
        : [...prev, metric]
    );
  };

  const selectAllMetrics = () => {
    setSelectedMetrics(availableMetrics.map(m => m.name));
  };

  const selectNoMetrics = () => {
    setSelectedMetrics([]);
  };

  const handleParameterValueChange = (metric: string, paramName: string, value: any) => {
    setParameterValues(prev => ({
      ...prev,
      [metric]: {
        ...prev[metric],
        [paramName]: value
      }
    }));
  };

  return {
    availableMetrics,
    selectedMetrics,
    availableParameters,
    parameterValues,
    handleMetricSelection,
    selectAllMetrics,
    selectNoMetrics,
    handleParameterValueChange,
    setSelectedMetrics
  };
};
