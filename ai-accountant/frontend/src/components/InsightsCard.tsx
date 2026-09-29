"use client";
import React from "react";
import { SummaryResponse } from "@/types";
import {
  LightBulbIcon,
  CurrencyDollarIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CalendarDaysIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ClockIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from "@heroicons/react/24/outline";

export default function InsightsCard({ summary }: { summary: SummaryResponse }) {
  // State for collapsible forecast section
  const [isForecastExpanded, setIsForecastExpanded] = React.useState(false);

  if (!summary) return null;

  // Handle summary text
  const summaryText = Array.isArray(summary.summary) ? summary.summary.join('\n') : summary.summary;
  const budgetTip = summary.budget_tip || '';
  const taxHint = summary.tax_hint || '';

  // Split summary text for formatting
  const lines = summaryText.split("\n").filter((l) => l.trim() !== "");

  // AI-based forecasting data (this would typically come from backend analysis)
  const forecastData = {
    nextMonthPrediction: {
      totalSpending: 12500,
      currency: 'PKR',
      trend: 'increase', // 'increase', 'decrease', 'stable'
      confidence: 85,
      topCategories: [
        { name: 'Dining', amount: 3200, trend: 'increase' },
        { name: 'Electronics', amount: 2800, trend: 'stable' },
        { name: 'Shopping', amount: 2100, trend: 'decrease' },
        { name: 'Transport', amount: 1800, trend: 'increase' },
        { name: 'Utilities', amount: 1600, trend: 'stable' }
      ],
      recommendations: [
        'Consider reducing dining expenses by 15% to stay within budget',
        'Electronics spending is expected to remain stable - good planning',
        'Shopping expenses are trending down - excellent cost control',
        'Transport costs may increase due to seasonal factors'
      ]
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increase':
        return <ArrowTrendingUpIcon className="h-8 w-8 text-red-500" />;
      case 'decrease':
        return <ArrowTrendingDownIcon className="h-8 w-8 text-green-500" />;
      default:
        return <ClockIcon className="h-8 w-8 text-blue-500" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'increase':
        return 'text-red-600';
      case 'decrease':
        return 'text-green-600';
      default:
        return 'text-blue-600';
    }
  };

  return (
    <div className="space-y-8">
      {/* Main Insights Card */}
      <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <div className="p-3 bg-gradient-to-br from-purple-100 to-indigo-100 rounded-xl">
            <LightBulbIcon className="h-7 w-7 text-purple-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">AI Spending Insights</h2>
            <p className="text-base text-gray-600 font-medium">Powered by advanced analytics</p>
          </div>
        </div>

        {/* Summary Lines */}
        <div className="space-y-4 mb-8">
          {lines.map((line, index) => (
            <div key={index} className="flex items-start gap-4">
              <div className="p-2 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg mt-1">
                <ChartBarIcon className="h-4 w-4 text-blue-600" />
              </div>
              <p className="text-gray-800 text-base leading-relaxed font-medium">{line}</p>
            </div>
          ))}
        </div>

        {/* AI Forecasting Section */}
        <div className="mb-8">
          <div 
            className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border border-purple-200 cursor-pointer hover:bg-gradient-to-r hover:from-purple-100 hover:to-indigo-100 transition-all duration-200"
            onClick={() => setIsForecastExpanded(!isForecastExpanded)}
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-purple-100 to-indigo-100 rounded-lg">
                <CalendarDaysIcon className="h-5 w-5 text-purple-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900">Next Month Forecast</h3>
              <div className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                {forecastData.nextMonthPrediction.confidence}% Confidence
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-purple-600 font-medium">
                {isForecastExpanded ? 'Hide Details' : 'Show Details'}
              </span>
              {isForecastExpanded ? (
                <ChevronUpIcon className="h-5 w-5 text-purple-600" />
              ) : (
                <ChevronDownIcon className="h-5 w-5 text-purple-600" />
              )}
            </div>
          </div>

          {/* Collapsible Content */}
          {isForecastExpanded && (
            <div className="mt-6 space-y-6 animate-in slide-in-from-top-2 duration-300">

              {/* Forecast Overview */}
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border-2 border-indigo-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-xl">
                      <CurrencyDollarIcon className="h-6 w-6 text-indigo-600" />
                    </div>
                    <div>
                      <h4 className="font-bold text-indigo-800 text-lg">Predicted Spending</h4>
                      <p className="text-indigo-600 text-sm">Based on current patterns</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-indigo-800">
                      {forecastData.nextMonthPrediction.totalSpending.toLocaleString()} {forecastData.nextMonthPrediction.currency}
                    </div>
                    <div className={`flex items-center gap-1 text-sm font-medium ${getTrendColor(forecastData.nextMonthPrediction.trend)}`}>
                      {getTrendIcon(forecastData.nextMonthPrediction.trend)}
                      {forecastData.nextMonthPrediction.trend === 'increase' ? 'Expected Increase' : 
                       forecastData.nextMonthPrediction.trend === 'decrease' ? 'Expected Decrease' : 'Stable Spending'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Category Forecasts */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {forecastData.nextMonthPrediction.topCategories.map((category, index) => {
                  const getCategoryColors = (catName: string, trend: string) => {
                    const colorSchemes: Record<string, Record<string, string>> = {
                      'Dining': {
                        bg: 'bg-gradient-to-br from-orange-100 to-red-100',
                        border: 'border-orange-300',
                        text: 'text-orange-800',
                        amount: 'text-orange-900',
                        icon: trend === 'increase' ? 'text-red-600' : trend === 'decrease' ? 'text-green-600' : 'text-blue-600'
                      },
                      'Electronics': {
                        bg: 'bg-gradient-to-br from-purple-100 to-indigo-100',
                        border: 'border-purple-300',
                        text: 'text-purple-800',
                        amount: 'text-purple-900',
                        icon: trend === 'increase' ? 'text-red-600' : trend === 'decrease' ? 'text-green-600' : 'text-blue-600'
                      },
                      'Shopping': {
                        bg: 'bg-gradient-to-br from-pink-100 to-rose-100',
                        border: 'border-pink-300',
                        text: 'text-pink-800',
                        amount: 'text-pink-900',
                        icon: trend === 'increase' ? 'text-red-600' : trend === 'decrease' ? 'text-green-600' : 'text-blue-600'
                      },
                      'Transport': {
                        bg: 'bg-gradient-to-br from-blue-100 to-cyan-100',
                        border: 'border-blue-300',
                        text: 'text-blue-800',
                        amount: 'text-blue-900',
                        icon: trend === 'increase' ? 'text-red-600' : trend === 'decrease' ? 'text-green-600' : 'text-blue-600'
                      },
                      'Utilities': {
                        bg: 'bg-gradient-to-br from-emerald-100 to-teal-100',
                        border: 'border-emerald-300',
                        text: 'text-emerald-800',
                        amount: 'text-emerald-900',
                        icon: trend === 'increase' ? 'text-red-600' : trend === 'decrease' ? 'text-green-600' : 'text-blue-600'
                      }
                    };
                    return colorSchemes[catName] || {
                      bg: 'bg-gradient-to-br from-gray-100 to-slate-100',
                      border: 'border-gray-300',
                      text: 'text-gray-800',
                      amount: 'text-gray-900',
                      icon: trend === 'increase' ? 'text-red-600' : trend === 'decrease' ? 'text-green-600' : 'text-blue-600'
                    };
                  };

                  const colors = getCategoryColors(category.name, category.trend);

                  return (
                    <div key={index} className={`${colors.bg} rounded-xl border-2 ${colors.border} p-5 hover:shadow-lg hover:scale-105 transition-all duration-300`}>
                      <div className="flex items-center justify-between mb-3">
                        <h5 className={`font-bold text-sm ${colors.text} uppercase tracking-wide`}>{category.name}</h5>
                        <div className={`p-2 rounded-lg  ${colors.bg}`}>
                          {getTrendIcon(category.trend)}
                        </div>
                      </div>
                      <div className={`text-2xl font-bold ${colors.amount} mb-2`}>
                        {category.amount.toLocaleString()} {forecastData.nextMonthPrediction.currency}
                      </div>
                      <div className={`text-xs font-semibold ${getTrendColor(category.trend)} flex items-center gap-1`}>
                        {category.trend === 'increase' ? '↑ Trending Up' : 
                         category.trend === 'decrease' ? '↓ Trending Down' : '→ Stable'}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* AI Recommendations */}
              <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl border-2 border-emerald-200 p-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gradient-to-br from-emerald-100 to-green-100 rounded-xl">
                    <LightBulbIcon className="h-6 w-6 text-emerald-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-bold text-emerald-800 mb-3 text-lg">AI Recommendations</h4>
                    <div className="space-y-2">
                      {forecastData.nextMonthPrediction.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2 flex-shrink-0"></div>
                          <p className="text-emerald-700 text-sm leading-relaxed">{rec}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {budgetTip && (
            <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl border-2 border-orange-200 p-6 hover:shadow-lg transition-all duration-300">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-gradient-to-br from-orange-100 to-red-100 rounded-xl">
                  <CurrencyDollarIcon className="h-6 w-6 text-orange-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-orange-800 mb-3 text-lg">Budget Optimization</h3>
                  <p className="text-orange-700 text-base leading-relaxed font-medium">{budgetTip}</p>
                </div>
              </div>
            </div>
          )}

          {taxHint && (
            <div className="bg-gradient-to-br from-teal-50 to-cyan-50 rounded-xl border-2 border-teal-200 p-6 hover:shadow-lg transition-all duration-300">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-gradient-to-br from-teal-100 to-cyan-100 rounded-xl">
                  <DocumentTextIcon className="h-6 w-6 text-teal-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-teal-800 mb-3 text-lg">Tax Planning</h3>
                  <p className="text-teal-700 text-base leading-relaxed font-medium">{taxHint}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mb-4 bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-200 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="p-2 bg-gradient-to-br from-amber-100 to-orange-100 rounded-lg mt-1">
            <ExclamationTriangleIcon className="h-5 w-5 text-amber-600" />
          </div>
          <div>
            <h4 className="font-bold text-amber-800 text-base mb-2">Important Notice</h4>
            <p className="text-amber-700 text-sm leading-relaxed font-medium">
              These insights are AI-generated for informational purposes only. 
              Always consult with a qualified financial advisor or tax professional 
              for personalized advice regarding your specific financial situation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
