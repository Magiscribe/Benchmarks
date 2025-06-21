import Container from '@/components/layouts/Container';
import Section from '@/components/Section';
import Loading from '@/components/Loading';
import { useDashboardData } from '@/hooks/useDashboardData';
import { TabNavigation, TabType } from '@/components/common/TabNavigation';
import { OverviewTab } from '@/components/overview/OverviewTab';
import { ChartsTab } from '@/components/charts/ChartsTab';
import { LeaderboardTab } from '@/components/leaderboard/LeaderboardTab';
import { useState } from 'react';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  
  // Dashboard data (test types, loading, error)
  const {
    benchmarks,
    loading,
    error,
    refetch: refetchbenchmarks
  } = useDashboardData();

  if (loading) {
    return (
      <Container>
        <Section title="Loading">
          <div className="flex items-center justify-center py-12">
            <Loading className="w-8 h-8 mr-3" />
            <div className="text-lg">Loading test types...</div>
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
        return <OverviewTab benchmarks={benchmarks} />;
      case 'charts':
        return <ChartsTab benchmarks={benchmarks} />;
      case 'leaderboard':
        return <LeaderboardTab />;
      default:
        return <OverviewTab benchmarks={benchmarks} />;
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
            Comprehensive analysis and visualization of LLM benchmark results
          </p>
        </div>

        {/* Tab Navigation */}
        <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />        {/* Tab Content */}
        {renderTabContent()}
      </div>
    </Container>
  );
}
