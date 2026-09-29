"use client";
import { useState, useEffect } from "react";
import { ModelConfig, AppSettings, SettingsResponse } from "@/types";
import {
  CogIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
} from "@heroicons/react/24/outline";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SettingsTab() {
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [currentModel, setCurrentModel] = useState<string>("");
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      
      // Load models and current settings
      const [modelsResponse, settingsResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/api/settings/models`),
        fetch(`${API_BASE_URL}/api/settings/current`)
      ]);

      if (!modelsResponse.ok || !settingsResponse.ok) {
        throw new Error("Failed to load settings");
      }

      const modelsData: SettingsResponse = await modelsResponse.json();
      const settingsData: AppSettings = await settingsResponse.json();

      setModels(modelsData.models);
      setCurrentModel(modelsData.current_model);
      setSettings(settingsData);
    } catch (error) {
      console.error("Error loading settings:", error);
      setMessage({ type: "error", text: "Failed to load settings" });
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async (updatedSettings: Partial<AppSettings>) => {
    try {
      setSaving(true);
      setMessage(null);

      const response = await fetch(`${API_BASE_URL}/api/settings`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedSettings),
      });

      if (!response.ok) {
        throw new Error("Failed to save settings");
      }

      setSettings(prev => prev ? { ...prev, ...updatedSettings } : null);
      setMessage({ type: "success", text: "Settings saved successfully" });
    } catch (error) {
      console.error("Error saving settings:", error);
      setMessage({ type: "error", text: "Failed to save settings" });
    } finally {
      setSaving(false);
    }
  };

  const resetSettings = async () => {
    if (!confirm("Are you sure you want to reset all settings to defaults?")) {
      return;
    }

    try {
      setSaving(true);
      setMessage(null);

      const response = await fetch(`${API_BASE_URL}/api/settings/reset`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to reset settings");
      }

      await loadSettings();
      setMessage({ type: "success", text: "Settings reset to defaults" });
    } catch (error) {
      console.error("Error resetting settings:", error);
      setMessage({ type: "error", text: "Failed to reset settings" });
    } finally {
      setSaving(false);
    }
  };

  const handleModelChange = (modelName: string) => {
    saveSettings({ default_model: modelName });
    setCurrentModel(modelName);
  };

  const handleSettingChange = (key: keyof AppSettings, value: boolean | number | string) => {
    if (!settings) return;
    saveSettings({ [key]: value });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading settings...</span>
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-600">Failed to load settings</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500 rounded-lg">
            <CogIcon className="h-6 w-6 text-white" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Settings</h2>
        </div>
      </div>

      {/* Message */}
      {message && (
        <div className={`p-4 rounded-xl shadow-lg border-2 ${
          message.type === "success" 
            ? "bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200 text-emerald-800" 
            : "bg-gradient-to-br from-red-50 to-red-100 border-red-200 text-red-800"
        }`}>
          <div className="flex items-center gap-2">
            {message.type === "success" ? (
              <div className="p-1 bg-emerald-500 rounded-lg">
                <CheckIcon className="h-4 w-4 text-white" />
              </div>
            ) : (
              <div className="p-1 bg-red-500 rounded-lg">
                <ExclamationTriangleIcon className="h-4 w-4 text-white" />
              </div>
            )}
            <span className="font-medium">{message.text}</span>
          </div>
        </div>
      )}

      {/* AI Model Selection */}
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-lg border border-blue-200 p-6 hover:shadow-xl transition-all duration-200">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-blue-500 rounded-lg">
            <CogIcon className="h-5 w-5 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-blue-800">AI Model Configuration</h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-blue-700 mb-2">
              Default AI Model
            </label>
            <div className="grid gap-3">
              {models.map((model) => (
                <div
                  key={model.name}
                  className={`p-4 border-2 rounded-xl cursor-pointer transition-all duration-200 ${
                    currentModel === model.name
                      ? "border-blue-500 bg-blue-200 shadow-md transform scale-[1.02]"
                      : "border-blue-200 bg-white/50 hover:border-blue-300 hover:bg-white/70 hover:shadow-md"
                  }`}
                  onClick={() => handleModelChange(model.name)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold text-blue-900">{model.display_name}</h4>
                        {!model.has_api_key && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">
                            <ExclamationTriangleIcon className="h-3 w-3 mr-1" />
                            API Key Required
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-blue-700 mt-1">{model.description}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-blue-600">
                        <span>Provider: {model.provider}</span>
                        <span>Cost: ${model.cost_per_1k_input}/${model.cost_per_1k_output} per 1K tokens</span>
                        <span>Max tokens: {model.max_tokens.toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      {currentModel === model.name && (
                        <div className="p-1 bg-blue-500 rounded-lg">
                          <CheckIcon className="h-4 w-4 text-white" />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Processing Settings */}
      <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl shadow-lg border border-emerald-200 p-6 hover:shadow-xl transition-all duration-200">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-emerald-500 rounded-lg">
            <CogIcon className="h-5 w-5 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-emerald-800">Processing Settings</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-emerald-700 mb-2">
              Batch Size
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={settings.batch_size}
              onChange={(e) => handleSettingChange("batch_size", parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-emerald-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white/70"
            />
            <p className="text-xs text-emerald-600 mt-1">Number of transactions to process in each batch</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-emerald-700 mb-2">
              Max Retries
            </label>
            <input
              type="number"
              min="0"
              max="10"
              value={settings.max_retries}
              onChange={(e) => handleSettingChange("max_retries", parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-emerald-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white/70"
            />
            <p className="text-xs text-emerald-600 mt-1">Maximum number of retry attempts for failed requests</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-emerald-700 mb-2">
              Timeout (seconds)
            </label>
            <input
              type="number"
              min="5"
              max="300"
              step="5"
              value={settings.timeout_seconds}
              onChange={(e) => handleSettingChange("timeout_seconds", parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-emerald-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white/70"
            />
            <p className="text-xs text-emerald-600 mt-1">Request timeout in seconds</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-emerald-700 mb-2">
              Data Retention (days)
            </label>
            <input
              type="number"
              min="1"
              max="365"
              value={settings.data_retention_days}
              onChange={(e) => handleSettingChange("data_retention_days", parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-emerald-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white/70"
            />
            <p className="text-xs text-emerald-600 mt-1">How long to keep usage data</p>
          </div>
        </div>
      </div>

      {/* Feature Toggles */}
      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl shadow-lg border border-purple-200 p-6 hover:shadow-xl transition-all duration-200">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-purple-500 rounded-lg">
            <CogIcon className="h-5 w-5 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-purple-800">Feature Settings</h3>
        </div>
        
        <div className="space-y-4">
          {[
            {
              key: "enable_token_tracking" as keyof AppSettings,
              label: "Token Usage Tracking",
              description: "Track token usage and costs for monitoring and optimization"
            },
            {
              key: "enable_circuit_breaker" as keyof AppSettings,
              label: "Circuit Breaker",
              description: "Automatically disable AI calls when failure rate is high"
            },
            {
              key: "auto_categorize" as keyof AppSettings,
              label: "Auto Categorization",
              description: "Automatically categorize transactions using AI"
            },
            {
              key: "fallback_to_rules" as keyof AppSettings,
              label: "Rule-based Fallback",
              description: "Use rule-based categorization when AI fails"
            }
          ].map(({ key, label, description }) => (
            <div key={key} className="flex items-center justify-between bg-white/50 rounded-lg p-4 hover:bg-white/70 transition-colors">
              <div className="flex-1">
                <h4 className="font-semibold text-purple-900">{label}</h4>
                <p className="text-sm text-purple-700">{description}</p>
              </div>
              <button
                onClick={() => handleSettingChange(key, !settings[key])}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-200 ${
                  settings[key] ? "bg-purple-500 shadow-md" : "bg-purple-200"
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 shadow-sm ${
                    settings[key] ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Circuit Breaker Settings */}
      {settings.enable_circuit_breaker && (
        <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl shadow-lg border border-amber-200 p-6 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-amber-500 rounded-lg">
              <ExclamationTriangleIcon className="h-5 w-5 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-amber-800">Circuit Breaker Settings</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-amber-700 mb-2">
                Failure Threshold
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={settings.circuit_breaker_threshold}
                onChange={(e) => handleSettingChange("circuit_breaker_threshold", parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 bg-white/70"
              />
              <p className="text-xs text-amber-600 mt-1">Number of failures before opening circuit</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-amber-700 mb-2">
                Recovery Timeout (seconds)
              </label>
              <input
                type="number"
                min="10"
                max="600"
                value={settings.circuit_breaker_timeout}
                onChange={(e) => handleSettingChange("circuit_breaker_timeout", parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 bg-white/70"
              />
              <p className="text-xs text-amber-600 mt-1">Time to wait before trying again</p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between">
        <button
          onClick={resetSettings}
          disabled={saving}
          className="group relative inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-medium text-sm rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          <svg className="h-4 w-4 group-hover:animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span className="hidden sm:inline">Reset to Defaults</span>
          <span className="sm:hidden">Reset</span>
          <div className="absolute inset-0 bg-gradient-to-r from-red-400 to-red-500 rounded-lg opacity-0 group-hover:opacity-20 transition-opacity duration-200"></div>
        </button>

        <div className="flex items-center gap-2 text-sm text-gray-500 bg-gray-100 px-3 py-2 rounded-lg">
          <div className="p-1 bg-gray-500 rounded">
            <InformationCircleIcon className="h-3 w-3 text-white" />
          </div>
          <span className="font-medium">Settings are automatically saved</span>
        </div>
      </div>
    </div>
  );
}
