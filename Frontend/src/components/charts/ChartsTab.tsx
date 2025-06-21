import React from 'react';
import { Benchmark } from '../../types/dashboard';
import { ChartBuilder } from './ChartBuilder';

interface ChartsTabProps {
  benchmarks: Benchmark[];
  selectedBenchmark?: string;
  onBenchmarkChange?: (benchmarkId: string) => void;
}

export const ChartsTab: React.FC<ChartsTabProps> = ({ 
  benchmarks, 
  selectedBenchmark, 
  onBenchmarkChange 
}) => {  return (
    <div className="space-y-6">
      {/* Chart Builder Interface */}
      <ChartBuilder 
        benchmarks={benchmarks} 
        selectedBenchmark={selectedBenchmark}
        onBenchmarkChange={onBenchmarkChange}
      />
    </div>
  );
};
