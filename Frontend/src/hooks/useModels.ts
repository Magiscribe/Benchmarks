import { useState, useEffect } from 'react';

const API_BASE = `${import.meta.env.VITE_API_URL}/api/data`;

export const useModels = (testType: string) => {
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);

  const fetchAvailableModels = async (testType: string) => {
    try {
      const response = await fetch(`${API_BASE}/available-models/${testType}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const models: string[] = await response.json();
      setAvailableModels(models);
      // Select all models by default
      setSelectedModels(models);
    } catch (err) {
      console.error('Error fetching available models:', err);
      setAvailableModels([]);
      setSelectedModels([]);
    }
  };

  useEffect(() => {
    if (testType) {
      fetchAvailableModels(testType);
    } else {
      setAvailableModels([]);
      setSelectedModels([]);
    }
  }, [testType]);

  const handleModelSelection = (model: string) => {
    setSelectedModels(prev => 
      prev.includes(model) 
        ? prev.filter(m => m !== model)
        : [...prev, model]
    );
  };

  const selectAllModels = () => {
    setSelectedModels([...availableModels]);
  };

  const selectNoModels = () => {
    setSelectedModels([]);
  };

  return {
    availableModels,
    selectedModels,
    handleModelSelection,
    selectAllModels,
    selectNoModels,
    setSelectedModels
  };
};
