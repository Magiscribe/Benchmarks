import Container from '@/components/layouts/Container';
import Section from '@/components/Section';
import Loading from '@/components/Loading';
import { useDashboardData } from '@/hooks/useDashboardData';
import { TabNavigation, TabType } from '@/components/common/TabNavigation';
import { OverviewTab } from '@/components/overview/OverviewTab';
import { ChartBuilder } from '@/components/charts/ChartBuilder';
import { LeaderboardTab } from '@/components/leaderboard/LeaderboardTab';
import { useState, useEffect } from 'react';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [selectedBenchmark, setSelectedBenchmark] = useState<string>('');
  
  // Dashboard data (benchmarks, loading, error)
  const {
    benchmarks,
    loading,
    error,
    refetch: refetchbenchmarks
  } = useDashboardData();

  // Auto-select first benchmark when benchmarks are loaded
  useEffect(() => {
    if (benchmarks.length > 0 && !selectedBenchmark) {
      setSelectedBenchmark(benchmarks[0].id);
    }
  }, [benchmarks, selectedBenchmark]);

  if (loading) {
    return (
      <Container>
        <Section title="Loading">
          <div className="flex items-center justify-center py-12">
            <Loading className="w-8 h-8 mr-3" />
            <div className="text-lg">Loading Benchmarks...</div>
          </div>
        </Section>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Section title="Error">
          <div className="flex items-center justify-center py-12">
            <div className="text-red-500">Error: {error}</div>
            <button
              onClick={refetchbenchmarks}
              className="ml-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Retry
            </button>
          </div>
        </Section>
      </Container>
    );
  }
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab 
          benchmarks={benchmarks} 
          selectedBenchmark={selectedBenchmark}
          onBenchmarkChange={setSelectedBenchmark}
        />;      case 'charts':
        return (
          <div className="space-y-6">
            <ChartBuilder 
              benchmarks={benchmarks}
              selectedBenchmark={selectedBenchmark}
              onBenchmarkChange={setSelectedBenchmark}
            />
          </div>
        );case 'leaderboard':
        return <LeaderboardTab 
          benchmarks={benchmarks}
          selectedBenchmark={selectedBenchmark}
          onBenchmarkChange={setSelectedBenchmark}
        />;
      default:
        return <OverviewTab 
          benchmarks={benchmarks}
          selectedBenchmark={selectedBenchmark}
          onBenchmarkChange={setSelectedBenchmark}
        />;
    }
  };

  return (
    <Container>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Benchmark Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Comprehensive analysis and visualization of LLM Benchmark results
          </p>
        </div>

        {/* Tab Navigation */}
        <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />        {/* Tab Content */}
        {renderTabContent()}
      </div>
    </Container>
  );
}
