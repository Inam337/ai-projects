"use client";
import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import { Bar, Doughnut } from "react-chartjs-2";
import { ArrowTrendingUpIcon, ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/24/outline";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface CategoryChartProps {
  totals: Record<string, number>;
  currency?: string;
}

export default function CategoryChart({ totals, currency = "USD" }: CategoryChartProps) {
  // State for collapsible category cards section
  const [isCategoryCardsExpanded, setIsCategoryCardsExpanded] = React.useState(false);

  const categories = Object.keys(totals);
  const amounts = Object.values(totals);
  const totalAmount = amounts.reduce((sum, amount) => sum + amount, 0);

  // Function to get currency symbol
  const getCurrencySymbol = (currencyCode: string) => {
    const currencySymbols: Record<string, string> = {
      'USD': '$',
      'EUR': '€',
      'GBP': '£',
      'JPY': '¥',
      'CAD': 'C$',
      'AUD': 'A$',
      'CHF': 'CHF',
      'CNY': '¥',
      'INR': '₹',
      'BRL': 'R$',
      'MXN': '$',
      'KRW': '₩',
      'SGD': 'S$',
      'HKD': 'HK$',
      'NZD': 'NZ$',
      'SEK': 'kr',
      'NOK': 'kr',
      'DKK': 'kr',
      'PLN': 'zł',
      'CZK': 'Kč',
      'HUF': 'Ft',
      'RUB': '₽',
      'TRY': '₺',
      'ZAR': 'R',
      'ILS': '₪',
      'AED': 'د.إ',
      'SAR': '﷼',
      'THB': '฿',
      'MYR': 'RM',
      'PHP': '₱',
      'IDR': 'Rp',
      'VND': '₫',
    };
    return currencySymbols[currencyCode.toUpperCase()] || currencyCode;
  };

  const currencySymbol = getCurrencySymbol(currency);

  // AI Accountant color scheme with more colors for all categories
  const colors = [
    "#3B82F6", // Blue - Professional
    "#10B981", // Emerald - Growth/Success
    "#F59E0B", // Amber - Warning/Attention
    "#EF4444", // Red - Expenses
    "#8B5CF6", // Purple - Premium
    "#06B6D4", // Cyan - Tech/AI
    "#84CC16", // Lime - Innovation
    "#F97316", // Orange - Energy
    "#EC4899", // Pink - Entertainment
    "#6366F1", // Indigo - Shopping
    "#14B8A6", // Teal - Education
    "#F43F5E", // Rose - Travel
    "#8B5A2B", // Brown - Insurance
    "#059669", // Green - Investment
    "#DC2626", // Red - Car/Service
    "#16A34A", // Green - Recharge/Topup
    "#6B7280", // Gray - Misc
  ];

  // Light background colors corresponding to each category color
  const lightColors = [
    "#EBF4FF", // Light Blue
    "#ECFDF5", // Light Emerald
    "#FFFBEB", // Light Amber
    "#FEF2F2", // Light Red
    "#F3E8FF", // Light Purple
    "#ECFEFF", // Light Cyan
    "#F7FEE7", // Light Lime
    "#FFF7ED", // Light Orange
    "#FDF2F8", // Light Pink
    "#EEF2FF", // Light Indigo
    "#F0FDFA", // Light Teal
    "#FFF1F2", // Light Rose
    "#FEF3C7", // Light Brown
    "#ECFDF5", // Light Green
    "#FEF2F2", // Light Red
    "#F0FDF4", // Light Green
    "#F9FAFB", // Light Gray
  ];

  const chartData = {
    labels: categories,
    datasets: [
      {
        label: `Amount (${currencySymbol})`,
        data: amounts,
        backgroundColor: colors.slice(0, categories.length),
        borderColor: colors.slice(0, categories.length),
        borderWidth: 0,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };

  const doughnutData = {
    labels: categories,
    datasets: [
      {
        data: amounts,
        backgroundColor: colors.slice(0, categories.length),
        borderColor: "#ffffff",
        borderWidth: 3,
        hoverBorderWidth: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12,
            weight: "normal" as const,
          },
        },
      },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        titleColor: "#ffffff",
        bodyColor: "#ffffff",
        borderColor: "#3B82F6",
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context: { parsed: { y: number }; label: string }) {
            const value = context.parsed.y;
            const percentage = ((value / totalAmount) * 100).toFixed(1);
            return `${context.label}: ${currencySymbol}${value.toLocaleString()} (${percentage}%)`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: "rgba(0, 0, 0, 0.05)",
        },
        ticks: {
          callback: function(value: number | string) {
            return `${currencySymbol}${Number(value).toLocaleString()}`;
          },
          font: {
            size: 11,
          },
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            size: 11,
            weight: "normal" as const,
          },
        },
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom" as const,
        labels: {
          usePointStyle: true,
          padding: 15,
          font: {
            size: 11,
            weight: "normal" as const,
          },
        },
      },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        titleColor: "#ffffff",
        bodyColor: "#ffffff",
        borderColor: "#3B82F6",
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          label: function(context: { parsed: number; label: string }) {
            const value = context.parsed;
            const percentage = ((value / totalAmount) * 100).toFixed(1);
            return `${context.label}: ${currencySymbol}${value.toLocaleString()} (${percentage}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
              <ArrowTrendingUpIcon className="h-6 w-6" />
              Spending Analytics
            </h2>
            <p className="text-blue-100">AI-powered transaction categorization insights</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold flex items-center gap-1">
              <span className="tex-2xl font-bold">{currencySymbol}</span>
              <span className="tex-2xl font-bold">-</span>

              {totalAmount.toLocaleString()}
            </div>
            <p className="text-blue-100 text-sm">Total Spending ({currency})</p>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-1">Spending by Category</h3>
            <p className="text-sm text-gray-500">Detailed breakdown of expenses</p>
          </div>
          <div className="h-80">
            <Bar data={chartData} options={options} />
          </div>
        </div>

        {/* Doughnut Chart */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-1">Spending Distribution</h3>
            <p className="text-sm text-gray-500">Percentage breakdown</p>
          </div>
          <div className="h-80">
            <Doughnut data={doughnutData} options={doughnutOptions} />
          </div>
        </div>
      </div>

      {/* Category Cards Section */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 mb-4">
        {/* Collapsible Header */}
        <div 
          className="flex items-center justify-between p-4  rounded-t-xl  cursor-pointer hover:bg-gradient-to-r hover:from-indigo-100 hover:to-purple-100 transition-all duration-200"
          onClick={() => setIsCategoryCardsExpanded(!isCategoryCardsExpanded)}
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-lg">
              <ArrowTrendingUpIcon className="h-5 w-5 text-indigo-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-800">Category Breakdown</h3>
            <div className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">
              {categories.length} Categories
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-indigo-600 font-medium">
              {isCategoryCardsExpanded ? 'Hide Details' : 'Show Details'}
            </span>
            {isCategoryCardsExpanded ? (
              <ChevronUpIcon className="h-5 w-5 text-indigo-600" />
            ) : (
              <ChevronDownIcon className="h-5 w-5 text-indigo-600" />
            )}
          </div>
        </div>

        {/* Collapsible Content */}
        {isCategoryCardsExpanded && (
          <div className="p-6 animate-in slide-in-from-top-2 duration-300 border-t border-indigo-200">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {categories.map((category, index) => {
                const amount = totals[category];
                const percentage = ((amount / totalAmount) * 100).toFixed(1);
                return (
                  <div
                    key={category}
                    className="rounded-xl shadow-lg border-2 p-4 hover:shadow-xl transition-all duration-200 hover:scale-105"
                    style={{ 
                      backgroundColor: lightColors[index % lightColors.length],
                      borderColor: colors[index % colors.length] + '40'
                    }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div
                        className="w-4 h-4 rounded-full shadow-sm"
                        style={{ backgroundColor: colors[index % colors.length] }}
                      ></div>
                      <span className="text-xs font-medium px-2 py-1 rounded-full" style={{ 
                        backgroundColor: colors[index % colors.length] + '20',
                        color: colors[index % colors.length]
                      }}>
                        {percentage}%
                      </span>
                    </div>
                    <h4 className="font-semibold text-gray-800 text-sm mb-1">{category}</h4>
                    <p className="text-lg font-bold text-gray-900">{currencySymbol} - {amount.toLocaleString()}</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
