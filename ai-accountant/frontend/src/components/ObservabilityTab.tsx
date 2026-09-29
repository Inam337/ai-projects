"use client";
import { useState, useEffect, useMemo } from "react";
import { UsageMetrics, TokenUsage, ObservabilityResponse, RecentUsageResponse } from "@/types";
import {
  ChartBarIcon,
  ClockIcon,
  CurrencyDollarIcon,
  CpuChipIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ObservabilityTab() {
  const [metrics, setMetrics] = useState<UsageMetrics | null>(null);
  const [recentUsage, setRecentUsage] = useState<TokenUsage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [periodDays, setPeriodDays] = useState(30);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(5);
  const [isOperationsExpanded, setIsOperationsExpanded] = useState(false);

  useEffect(() => {
    loadMetrics();
  }, [periodDays]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadMetrics = async () => {
    try {
      setLoading(true);
      setError(null);

      const [metricsResponse, recentResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/api/observability/metrics?days=${periodDays}`),
        fetch(`${API_BASE_URL}/api/observability/recent?limit=50`)
      ]);

      if (!metricsResponse.ok || !recentResponse.ok) {
        throw new Error("Failed to load observability data");
      }

      const metricsData: ObservabilityResponse = await metricsResponse.json();
      const recentData: RecentUsageResponse = await recentResponse.json();

      setMetrics(metricsData.metrics);
      setRecentUsage(recentData.recent_usage);
    } catch (error) {
      console.error("Error loading observability data:", error);
      setError("Failed to load observability data");
    } finally {
      setLoading(false);
    }
  };

  const cleanupOldData = async () => {
    if (!confirm("Are you sure you want to clean up old usage data?")) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/observability/cleanup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ days_to_keep: 90 }),
      });

      if (!response.ok) {
        throw new Error("Failed to cleanup data");
      }

      const result = await response.json();
      alert(`Cleaned up ${result.records_removed} old records`);
      loadMetrics();
    } catch (error) {
      console.error("Error cleaning up data:", error);
      alert("Failed to cleanup data");
    }
  };

  const testTokenCalculation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/observability/test-tokens`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to test token calculation");
      }

      const result = await response.json();
      alert(`Added ${result.test_tokens_added} test tokens. Total tokens will increase by this amount.`);
      loadMetrics();
    } catch (error) {
      console.error("Error testing token calculation:", error);
      alert("Failed to test token calculation");
    }
  };

  const resetTestData = async () => {
    if (!confirm("Are you sure you want to reset all test data? This will remove all 'test' operation records.")) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/observability/reset-test-data`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to reset test data");
      }

      const result = await response.json();
      alert(`Reset completed: ${result.message}`);
      loadMetrics();
    } catch (error) {
      console.error("Error resetting test data:", error);
      alert("Failed to reset test data");
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 4,
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat("en-US").format(num);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  // Pagination for Recent Usage
  const paginatedRecentUsage = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return recentUsage.slice(startIndex, endIndex);
  }, [recentUsage, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(recentUsage.length / itemsPerPage);

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const goToPreviousPage = () => {
    setCurrentPage(prev => Math.max(1, prev - 1));
  };

  const goToNextPage = () => {
    setCurrentPage(prev => Math.min(totalPages, prev + 1));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading observability data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-600">{error}</p>
        <button
          onClick={loadMetrics}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="text-center py-12">
        <InformationCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No observability data available</p>
      </div>
    );
  }

  // AI Accountant color scheme (matching CategoryChart)
  const colors = [
    "#3B82F6", // Blue - Professional
    "#10B981", // Emerald - Growth/Success
    "#F59E0B", // Amber - Warning/Attention
    "#EF4444", // Red - Expenses
    "#8B5CF6", // Purple - Premium
    "#06B6D4", // Cyan - Tech/AI
    "#84CC16", // Lime - Innovation
    "#F97316", // Orange - Energy
  ];

  // Prepare chart data
  const dailyUsageData = Object.entries(metrics.daily_usage)
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-30); // Last 30 days

  const dailyChartData = {
    labels: dailyUsageData.map(([date]) => new Date(date).toLocaleDateString()),
    datasets: [
      {
        label: "Requests",
        data: dailyUsageData.map(([, data]) => data.requests),
        backgroundColor: "rgba(59, 130, 246, 0.5)",
        borderColor: "#3B82F6",
        borderWidth: 2,
        borderRadius: 4,
        borderSkipped: false,
      },
      {
        label: "Tokens (K)",
        data: dailyUsageData.map(([, data]) => data.tokens / 1000),
        backgroundColor: "rgba(16, 185, 129, 0.5)",
        borderColor: "#10B981",
        borderWidth: 2,
        borderRadius: 4,
        borderSkipped: false,
        yAxisID: "y1",
      },
    ],
  };

  const modelChartData = {
    labels: Object.keys(metrics.requests_by_model),
    datasets: [
      {
        label: "Requests",
        data: Object.values(metrics.requests_by_model),
        backgroundColor: colors.slice(0, Object.keys(metrics.requests_by_model).length),
        borderColor: colors.slice(0, Object.keys(metrics.requests_by_model).length),
        borderWidth: 0,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
      title: {
        display: true,
        text: "Daily Usage Trends",
      },
    },
    scales: {
      y: {
        type: "linear" as const,
        display: true,
        position: "left" as const,
      },
      y1: {
        type: "linear" as const,
        display: true,
        position: "right" as const,
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  const modelChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
      title: {
        display: true,
        text: "Usage by Model",
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ChartBarIcon className="h-6 w-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Observability Dashboard</h2>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative">
            <select
              value={periodDays}
              onChange={(e) => setPeriodDays(parseInt(e.target.value))}
              className="pl-3 pr-10 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 hover:border-gray-400 appearance-none cursor-pointer"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <ChevronDownIcon className="h-4 w-4 text-gray-400" />
            </div>
          </div>

          <button
            onClick={testTokenCalculation}
            className="group relative inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-medium text-sm rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <svg className="h-4 w-4 group-hover:animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="hidden sm:inline">Add Test Tokens</span>
            <span className="sm:hidden">Test</span>
            <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-blue-500 rounded-lg opacity-0 group-hover:opacity-20 transition-opacity duration-200"></div>
          </button>

          <button
            onClick={resetTestData}
            className="group relative inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-medium text-sm rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
          >
            <svg className="h-4 w-4 group-hover:animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span className="hidden sm:inline">Reset Test Data</span>
            <span className="sm:hidden">Reset</span>
            <div className="absolute inset-0 bg-gradient-to-r from-orange-400 to-orange-500 rounded-lg opacity-0 group-hover:opacity-20 transition-opacity duration-200"></div>
          </button>

          <button
            onClick={cleanupOldData}
            className="group relative inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-medium text-sm rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            <svg className="h-4 w-4 group-hover:animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span className="hidden sm:inline">Cleanup Old Data</span>
            <span className="sm:hidden">Cleanup</span>
            <div className="absolute inset-0 bg-gradient-to-r from-red-400 to-red-500 rounded-lg opacity-0 group-hover:opacity-20 transition-opacity duration-200"></div>
          </button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-lg border border-blue-200 p-6 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center">
            <div className="p-3 bg-blue-500 rounded-xl shadow-md">
              <CpuChipIcon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-blue-700">Total Requests</p>
              <p className="text-2xl font-bold text-blue-900">
                {formatNumber(metrics.total_requests)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl shadow-lg border border-emerald-200 p-6 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center">
            <div className="p-3 bg-emerald-500 rounded-xl shadow-md">
              <ChartBarIcon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-emerald-700">Total Tokens</p>
              <p className="text-2xl font-bold text-emerald-900">
                {formatNumber(metrics.total_tokens)}
              </p>
              {metrics.total_tokens === 0 && (
                <p className="text-xs text-emerald-600 mt-1">
                  No successful API calls detected
                </p>
              )}
              {metrics.total_tokens > 0 && (
                <p className="text-xs text-emerald-600 mt-1">
                  Includes real API calls + test data
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl shadow-lg border border-amber-200 p-6 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center">
            <div className="p-3 bg-amber-500 rounded-xl shadow-md">
              <CurrencyDollarIcon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-amber-700">Total Cost</p>
              <p className="text-2xl font-bold text-amber-900">
                {formatCurrency(metrics.total_cost_usd)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl shadow-lg border border-purple-200 p-6 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center">
            <div className="p-3 bg-purple-500 rounded-xl shadow-md">
              <ClockIcon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-purple-700">Avg Latency</p>
              <p className="text-2xl font-bold text-purple-900">
                {metrics.avg_latency_ms.toFixed(0)}ms
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Test Data Explanation */}
      {metrics.total_tokens > 0 && (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl shadow-lg border border-blue-200 p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-blue-500 rounded-xl">
              <InformationCircleIcon className="h-6 w-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">Token Calculation Info</h3>
              <p className="text-blue-700 mb-3">
                The &quot;Total Tokens&quot; includes both real API usage and test data. Each time you click &quot;Add Test Tokens&quot;, it adds 525 tokens to verify the tracking system works.
              </p>
              <div className="space-y-2 text-sm text-blue-700">
                <p>• <strong>Real API calls:</strong> Actual token usage from your application</p>
                <p>• <strong>Test data:</strong> Sample tokens added for testing (operation: &quot;test&quot;)</p>
                <p>• <strong>Reset Test Data:</strong> Removes all test records to see only real usage</p>
                <p>• <strong>Cleanup Old Data:</strong> Removes records older than 90 days</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* API Status Diagnostic */}
      {metrics.total_tokens === 0 && metrics.total_requests > 0 && (
        <div className="bg-gradient-to-br from-amber-50 to-orange-100 rounded-xl shadow-lg border border-amber-200 p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-amber-500 rounded-xl">
              <ExclamationTriangleIcon className="h-6 w-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-amber-800 mb-2">API Configuration Issue</h3>
              <p className="text-amber-700 mb-3">
                Token calculation shows 0 because all API requests are failing. This typically indicates an invalid or missing OpenAI API key.
              </p>
              <div className="space-y-2 text-sm text-amber-700">
                <p>• Check your OpenAI API key configuration</p>
                <p>• Verify the API key has sufficient credits</p>
                <p>• Ensure the API key has proper permissions</p>
                <p>• Check the backend logs for detailed error messages</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl shadow-lg border border-emerald-200 p-6 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-emerald-800">Success Rate</h3>
            {metrics.success_rate >= 95 ? (
              <CheckCircleIcon className="h-6 w-6 text-emerald-600" />
            ) : (
              <ExclamationTriangleIcon className="h-6 w-6 text-amber-600" />
            )}
          </div>
          <div className="flex items-center">
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <span className="text-3xl font-bold text-emerald-900">
                  {metrics.success_rate.toFixed(1)}%
                </span>
              </div>
              <p className="text-sm text-emerald-700 mt-2">
                {metrics.total_requests} total requests
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-xl shadow-lg border border-cyan-200 p-6 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-cyan-800">Rows Processed</h3>
            <div className="p-2 bg-cyan-500 rounded-lg">
              <ChartBarIcon className="h-5 w-5 text-white" />
            </div>
          </div>
          <div className="flex items-center">
            <div className="flex-1">
              <span className="text-3xl font-bold text-cyan-900">
                {formatNumber(metrics.total_rows_processed)}
              </span>
              <p className="text-sm text-cyan-700 mt-2">
                Transaction rows processed
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Operations Card - Full Width Collapsible */}
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl shadow-lg border border-indigo-200 hover:shadow-xl transition-all duration-200">
        {/* Collapsible Header */}
        <div 
          className="flex items-center justify-between p-6 cursor-pointer hover:bg-gradient-to-r hover:from-indigo-100 hover:to-purple-100 transition-all duration-200 rounded-t-xl group"
          onClick={() => setIsOperationsExpanded(!isOperationsExpanded)}
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-md group-hover:shadow-lg transition-shadow duration-200">
              <CpuChipIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-indigo-900">Operations</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-indigo-600">
                  {Object.keys(metrics.requests_by_operation).length} types
                </span>
                <span className="text-indigo-400">•</span>
                <span className="text-sm text-indigo-600">
                  {Object.values(metrics.requests_by_operation).reduce((sum, count) => sum + count, 0)} total
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-2 bg-indigo-100 rounded-lg group-hover:bg-indigo-200 transition-colors duration-200">
              <span className="text-sm text-indigo-700 font-medium">
                {isOperationsExpanded ? 'Hide' : 'Show'}
              </span>
              {isOperationsExpanded ? (
                <ChevronUpIcon className="h-4 w-4 text-indigo-600" />
              ) : (
                <ChevronDownIcon className="h-4 w-4 text-indigo-600" />
              )}
            </div>
          </div>
        </div>

        {/* Collapsible Content */}
        {isOperationsExpanded && (
          <div className="p-6 border-t border-indigo-200 animate-in slide-in-from-top-2 duration-300">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3">
              {Object.entries(metrics.requests_by_operation).map(([operation, count]) => (
                <div key={operation} className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 hover:shadow-md hover:border-indigo-300 transition-all duration-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 capitalize">{operation}</span>
                    <span className="text-lg font-bold text-indigo-900">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-lg border border-blue-200 p-6 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-blue-500 rounded-lg">
              <ChartBarIcon className="h-5 w-5 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-blue-800">Daily Usage Trends</h3>
          </div>
          <div className="h-64 bg-white/50 rounded-lg p-2">
            <Line data={dailyChartData} options={chartOptions} />
          </div>
        </div>

        <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl shadow-lg border border-emerald-200 p-6 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-emerald-500 rounded-lg">
              <ChartBarIcon className="h-5 w-5 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-emerald-800">Usage by Model</h3>
          </div>
          <div className="h-64 bg-white/50 rounded-lg p-2">
            <Bar data={modelChartData} options={modelChartOptions} />
          </div>
        </div>
      </div>

      {/* Model Breakdown */}
      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl shadow-lg border border-purple-200 p-6 hover:shadow-xl transition-all duration-200">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-purple-500 rounded-lg">
            <CpuChipIcon className="h-5 w-5 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-purple-800">Model Usage Breakdown</h3>
        </div>
        <div className="overflow-x-auto bg-white/50 rounded-lg">
          <table className="min-w-full divide-y divide-purple-200">
            <thead className="bg-purple-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-purple-700 uppercase tracking-wider">
                  Model
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-purple-700 uppercase tracking-wider">
                  Requests
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-purple-700 uppercase tracking-wider">
                  Tokens
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-purple-700 uppercase tracking-wider">
                  Cost
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-purple-200">
              {Object.entries(metrics.requests_by_model).map(([model, requests]) => (
                <tr key={model} className="hover:bg-purple-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-purple-900">
                    {model}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-purple-700">
                    {formatNumber(requests)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-purple-700">
                    {formatNumber(metrics.tokens_by_model[model] || 0)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-purple-700">
                    {formatCurrency(metrics.cost_by_model[model] || 0)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Usage */}
      <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl shadow-lg border border-slate-200 p-6 hover:shadow-xl transition-all duration-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-slate-500 rounded-lg">
              <ClockIcon className="h-5 w-5 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-slate-800">Recent Usage</h3>
          </div>
          <div className="text-sm text-slate-600 bg-slate-200 px-3 py-1 rounded-full">
            Showing {Math.min((currentPage - 1) * itemsPerPage + 1, recentUsage.length)}-{Math.min(currentPage * itemsPerPage, recentUsage.length)} of {recentUsage.length} records
          </div>
        </div>
        <div className="overflow-x-auto bg-white/50 rounded-lg">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                  Model
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                  Operation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                  Tokens
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                  Cost
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                  Latency
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {paginatedRecentUsage.map((usage, index) => (
                <tr key={index} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {formatTimestamp(usage.timestamp)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                    {usage.model}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {usage.operation}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {formatNumber(usage.total_tokens)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {formatCurrency(usage.cost_usd)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {usage.latency_ms.toFixed(0)}ms
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {usage.success ? (
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 border border-emerald-200">
                        <CheckCircleIcon className="h-3 w-3 mr-1" />
                        Success
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
                        <ExclamationTriangleIcon className="h-3 w-3 mr-1" />
                        Failed
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-300">
            <div className="flex items-center gap-2">
              <button
                onClick={goToPreviousPage}
                disabled={currentPage === 1}
                className="p-2 rounded-lg hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeftIcon className="h-4 w-4 text-slate-600" />
              </button>
              
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }

                  return (
                    <button
                      key={pageNum}
                      onClick={() => goToPage(pageNum)}
                      className={clsx(
                        "px-3 py-1 text-sm rounded-lg transition-colors",
                        currentPage === pageNum
                          ? "bg-slate-500 text-white"
                          : "hover:bg-slate-200 text-slate-700"
                      )}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
              
              <button
                onClick={goToNextPage}
                disabled={currentPage === totalPages}
                className="p-2 rounded-lg hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRightIcon className="h-4 w-4 text-slate-600" />
              </button>
            </div>
            
            <div className="text-sm text-slate-600 bg-slate-200 px-3 py-1 rounded-full">
              Page {currentPage} of {totalPages}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
