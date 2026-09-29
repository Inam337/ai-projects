"use client";
import { useState } from "react";
import FileUploader from "@/components/FileUploader";
import CategoryChart from "@/components/CategoryChart";
import TransactionsTable from "@/components/TransactionsTable";
import InsightsCard from "@/components/InsightsCard";
import SettingsTab from "@/components/SettingsTab";
import ObservabilityTab from "@/components/ObservabilityTab";
import { ProcessedData } from "@/types";
import {
  CloudArrowUpIcon,
  ChartBarIcon,
  TableCellsIcon,
  LightBulbIcon,
  CogIcon,
  ChartPieIcon,
  ArrowLeftIcon,
} from "@heroicons/react/24/outline";

export default function HomePage() {
  const [data, setData] = useState<ProcessedData | null>(null);
  const [activeTab, setActiveTab] = useState<"charts" | "table" | "insights" | "settings" | "observability">("charts");

  const handleUpload = (uploadedData: ProcessedData) => {
    setData(uploadedData);
  };

  const handleBackToUpload = () => {
    setData(null);
    setActiveTab("charts");
  };

  const tabs: Array<{
    id: "charts" | "table" | "insights" | "settings" | "observability";
    name: string;
    icon: typeof ChartBarIcon;
  }> = [
      { id: "charts", name: "Analytics", icon: ChartBarIcon },
      { id: "table", name: "Transactions", icon: TableCellsIcon },
      { id: "insights", name: "Insights", icon: LightBulbIcon },
      { id: "settings", name: "Settings", icon: CogIcon },
      { id: "observability", name: "Observability", icon: ChartPieIcon },
    ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Awesome Header */}
      <div className="relative bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900 shadow-2xl border-b border-blue-800/30 overflow-hidden mb-2">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-40">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-transparent to-purple-600/10"></div>
        </div>
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-transparent to-purple-600/20"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center gap-4">
              {/* Enhanced Logo */}
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl blur-lg opacity-75 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="relative p-3 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 rounded-xl shadow-lg">
                  <CloudArrowUpIcon className="h-8 w-8 text-white drop-shadow-lg" />
                </div>
              </div>
              
              {/* Enhanced Title */}
              <div className="space-y-1">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent drop-shadow-lg">
                  AI Accountant
                </h1>
                <p className="text-sm text-blue-200 font-medium tracking-wide">
                  Intelligent Transaction Analysis & Financial Insights
                </p>
              </div>
            </div>

            {/* Right Side - Status Indicator */}
            <div className="flex items-center gap-4">
              {data ? (
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 backdrop-blur-sm rounded-full border border-green-400/30">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-green-200">Data Loaded</span>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-white font-bold">Transactions</p>
                    <p className="text-xl font-bold text-white">{data.rows.length}</p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2 px-4 py-2 bg-blue-500/20 backdrop-blur-sm rounded-full border border-blue-400/30">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-blue-200">Ready to Upload</span>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Bottom Accent Line */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500"></div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-2 sm:px-2 lg:px-2 py-2">
        {/* Upload Section - Always visible at top */}
        {!data && (<div className="mb-2">
          <FileUploader onUpload={handleUpload} />
        </div>
        )}
        {/* Back to Upload Button - Only show when data is loaded */}
        {data && (
          <div className="mb-2">
            <button
              onClick={handleBackToUpload}
              className="group relative inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 text-white font-medium text-sm rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              <ArrowLeftIcon className="h-4 w-4 group-hover:animate-pulse" />
              <span className="hidden sm:inline">Back to Upload</span>
              <span className="sm:hidden">Back</span>
              <div className="absolute inset-0 bg-gradient-to-r from-gray-400 to-gray-500 rounded-lg opacity-0 group-hover:opacity-20 transition-opacity duration-200"></div>
            </button>
          </div>
        )}

        {/* Tab Navigation - Only show after successful upload */}
        {data && (
          <div className="bg-blue-50 rounded-xl shadow-sm border border-blue-100 p-1 mb-2">
            <nav className="flex space-x-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === tab.id
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                      }`}
                  >
                    <Icon className="h-4 w-4" />
                    {tab.name}
                  </button>
                );
              })}
            </nav>
          </div>
        )}

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === "charts" && data && (
            <CategoryChart 
              totals={data.totals} 
              currency={data.rows.length > 0 ? data.rows[0].currency : "USD"} 
            />
          )}

          {activeTab === "table" && data && (
            <TransactionsTable rows={data.rows} />
          )}

          {activeTab === "insights" && data && (
            <InsightsCard summary={data.summary} />
          )}

          {activeTab === "settings" && data && (
            <SettingsTab />
          )}

          {activeTab === "observability" && data && (
            <ObservabilityTab />
          )}
        </div>
      </div>
    </div>
  );
}
