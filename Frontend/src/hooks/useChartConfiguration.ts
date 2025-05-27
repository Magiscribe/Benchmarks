import { useState, useMemo } from 'react';
import { ChartConfiguration, ChartValidation, ChartType } from '../types/charts';

export const useChartConfiguration = (
  availableMetrics: string[], 
  availableCategorical: string[] = []
) => {  const [config, setConfig] = useState<ChartConfiguration>(() => {
    const initialConfig: ChartConfiguration = { chartType: 'bar' };
    
    // Set default values for bar chart on initialization
    if (availableMetrics.length > 0) {
      initialConfig.metric1 = availableMetrics[0];
    }
    
    return initialConfig;
  });

  const validation = useMemo((): ChartValidation => {
    const errors: string[] = [];

    switch (config.chartType) {
      case 'bar':
        if (!config.metric1) {
          errors.push('Please select at least one metric for the bar chart');
        }
        break;
      case 'scatter':
        if (!config.xMetric) {
          errors.push('Please select X-axis metric for scatter plot');
        }
        if (!config.yMetric) {
          errors.push('Please select Y-axis metric for scatter plot');
        }
        if (config.xMetric && config.yMetric && config.xMetric === config.yMetric) {
          errors.push('X and Y metrics must be different for scatter plot');
        }
        break;
      case 'line':
        if (!config.categorical) {
          errors.push('Please select a categorical field for line chart');
        }
        if (!config.lineMetric) {
          errors.push('Please select a metric for line chart');
        }
        break;
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }, [config]);
  const updateChartType = (chartType: ChartType) => {
    const newConfig: ChartConfiguration = { chartType };
    
    // Auto-select first available options based on chart type
    switch (chartType) {
      case 'bar':
        if (availableMetrics.length > 0) {
          newConfig.metric1 = availableMetrics[0];
        }
        break;
      case 'scatter':
        if (availableMetrics.length >= 2) {
          newConfig.xMetric = availableMetrics[0];
          newConfig.yMetric = availableMetrics[1];
        } else if (availableMetrics.length === 1) {
          newConfig.xMetric = availableMetrics[0];
        }
        break;
      case 'line':
        if (availableCategorical.length > 0) {
          newConfig.categorical = availableCategorical[0];
        }
        if (availableMetrics.length > 0) {
          newConfig.lineMetric = availableMetrics[0];
        }
        break;
    }
    
    setConfig(newConfig);
  };

  const updateMetric1 = (metric: string) => {
    setConfig(prev => ({ ...prev, metric1: metric }));
  };

  const updateMetric2 = (metric: string) => {
    setConfig(prev => ({ 
      ...prev, 
      metric2: metric || undefined 
    }));
  };

  const updateXMetric = (metric: string) => {
    setConfig(prev => ({ ...prev, xMetric: metric }));
  };

  const updateYMetric = (metric: string) => {
    setConfig(prev => ({ ...prev, yMetric: metric }));
  };

  const updateCategorical = (categorical: string) => {
    setConfig(prev => ({ ...prev, categorical }));
  };

  const updateLineMetric = (metric: string) => {
    setConfig(prev => ({ ...prev, lineMetric: metric }));
  };

  return {
    config,
    validation,
    updateChartType,
    updateMetric1,
    updateMetric2,
    updateXMetric,
    updateYMetric,
    updateCategorical,
    updateLineMetric,
    availableMetrics,
    availableCategorical
  };
};
