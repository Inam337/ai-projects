'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Droplets, Sun, Sparkles, CheckCircle } from 'lucide-react';

interface Detection {
  label: string;
  conf: number;
  box: number[];
  crop_path?: string;
}

interface RoomColorAnalysis {
  codes: string[];
  theme: string;
}

interface RecommendationData {
  'Room Color Analysis'?: RoomColorAnalysis;
  'Room Lightening Analysis'?: string;
  object?: string;
  position?: string;
  reference_color?: string;
  justification?: string;
  trend_analysis?: string;
}

interface ImageAnalysisData {
  detections?: Detection[];
  recommendations?: RecommendationData[];
  roomType?: string;
  styleDetected?: string;
  imageUrl: string;
  annotated_image_b64?: string;
  audio_path?: string | null;
}

interface ImageAnalysisPanelProps {
  analysisData?: ImageAnalysisData;
  isLoading?: boolean;
}

// Color Swatch Component
interface ColorSwatchProps {
  color: string;
  size?: 'small' | 'large';
  showHex?: boolean;
}

function ColorSwatch({ color, size = 'small', showHex = true }: ColorSwatchProps) {
  const hexColor = color.startsWith('#') ? color : `#${color}`;
  const sizeClasses = size === 'large' ? 'w-12 h-12' : 'w-10 h-10';
  
  return (
    <div className="flex flex-col items-center">
      <div
        className={`${sizeClasses} rounded-lg shadow-md border-2 border-white cursor-pointer hover:shadow-lg transition-shadow`}
        style={{ backgroundColor: hexColor }}
        title={hexColor}
      />
      {showHex && <span className="text-xs text-gray-500 mt-1">{hexColor}</span>}
    </div>
  );
}

// Parse colors from reference color text
const parseColorsFromText = (text: string): string[] => {
  // Match hex colors in the text
  const hexMatches = text.match(/#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}/g);
  if (hexMatches && hexMatches.length > 0) {
    return hexMatches;
  }
  return [];
};

export default function ImageAnalysisPanel({ analysisData, isLoading = false }: ImageAnalysisPanelProps) {
  if (!analysisData && !isLoading) {
    return null;
  }

  // Extract data from recommendations
  const firstRecommendation = analysisData?.recommendations?.[0];
  const roomColorAnalysis = firstRecommendation?.['Room Color Analysis'];
  const roomLighteningAnalysis = firstRecommendation?.['Room Lightening Analysis'];
  const detectedObjects = analysisData?.detections || [];

  return (
    <div className="w-[500px] bg-gradient-to-b from-gray-50 to-white border-l border-gray-200 overflow-hidden h-full flex flex-col">
      {/* Header - Fixed */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 rounded-lg flex items-center justify-center mr-3">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-900">AI Analysis</h2>
            <p className="text-xs text-gray-500">Room Insights & Recommendations</p>
          </div>
        </div>
      </div>

      {/* Content - Scrollable */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoading ? (
            <div className="px-4 py-8 flex flex-col items-center justify-center">
              <div className="relative mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
                  <div className="animate-spin rounded-full h-12 w-12 border-4 border-white/30 border-t-white"></div>
                </div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-white animate-pulse" />
                </div>
              </div>
              <p className="text-sm font-medium text-gray-700">Analyzing your image...</p>
              <p className="text-xs text-gray-500 mt-1">This may take a few seconds</p>
            </div>
          ) : (
            <>
            {/* Detected Objects */}
            {detectedObjects.length > 0 && (
              <Card className="shadow-md border-0 bg-white overflow-hidden hover:shadow-lg transition-all duration-300">
                <CardHeader className="pb-4 bg-gradient-to-r from-emerald-50 via-green-50 to-emerald-50/50">
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg">
                        <CheckCircle className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <div className="text-base font-bold text-gray-900">What I Found</div>
                        <div className="text-xs text-gray-600 font-normal mt-0.5">
                          {detectedObjects.length} {detectedObjects.length === 1 ? 'item detected' : 'items detected'}
                        </div>
                      </div>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-4 pb-4 overflow-y-auto max-h-[200px]">
                  <div className="grid grid-cols-2 gap-2">
                    {detectedObjects.map((obj, index) => {
                      const confidence = Math.round(obj.conf * 100);
                      const isHighConfidence = confidence >= 70;
                      
                      return (
                        <div
                          key={index}
                          className="group relative bg-gradient-to-br from-gray-50 to-white rounded-xl p-3 border border-gray-200 hover:border-emerald-300 hover:shadow-md transition-all duration-300 hover:scale-[1.02] cursor-pointer"
                          style={{
                            animationDelay: `${index * 50}ms`,
                          }}
                        >
                          <div className="flex flex-col items-center text-center gap-2">
                            <div className={`relative w-12 h-12 rounded-xl flex items-center justify-center shadow-sm transition-all duration-300 ${
                              isHighConfidence 
                                ? 'bg-gradient-to-br from-emerald-400 to-green-500 group-hover:from-emerald-500 group-hover:to-green-600' 
                                : 'bg-gradient-to-br from-amber-400 to-orange-500 group-hover:from-amber-500 group-hover:to-orange-600'
                            } group-hover:scale-110`}>
                              <span className="text-white font-bold text-sm">
                                {obj.label.charAt(0).toUpperCase()}
                              </span>
                              {isHighConfidence && (
                                <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white shadow-sm" />
                              )}
                            </div>
                            <div className="flex-1 w-full">
                              <div className="text-xs font-semibold text-gray-800 capitalize mb-1 leading-tight">
                                {obj.label}
                              </div>
                              <div className="flex items-center justify-center gap-1">
                                <div className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                  isHighConfidence 
                                    ? 'bg-emerald-100 text-emerald-700' 
                                    : 'bg-amber-100 text-amber-700'
                                }`}>
                                  {confidence}%
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}

              {detectedObjects.length > 0 && <Separator />}

            {/* Room Color Analysis */}
            {roomColorAnalysis && roomColorAnalysis.codes && Array.isArray(roomColorAnalysis.codes) && roomColorAnalysis.codes.length > 0 && (
              <Card className="shadow-sm border border-gray-200 bg-gradient-to-br from-blue-50/50 to-white">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-bold flex items-center text tam-900">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-2">
                      <Droplets className="w-4 h-4 text-blue-600" />
                    </div>
                    Color Palette
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  {roomColorAnalysis.theme && (
                    <div className="mb-4 p-3 bg-white/60 rounded-lg border border-blue-200">
                      <p className="text-sm font-medium text-gray-800 italic">{roomColorAnalysis.theme}</p>
                    </div>
                  )}
                  <div className="flex flex-wrap gap-3">
                    {roomColorAnalysis.codes.map((color, index) => (
                      <ColorSwatch key={index} color={color} />
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Room Lightening Analysis */}
            {roomLighteningAnalysis && (
              <Card className="shadow-sm border border-gray-200 bg-gradient-to-br from-amber-50/50 to-white">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-bold flex items-center text-gray-900">
                    <div className="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center mr-2">
                      <Sun className="w-4 h-4 text-amber-600" />
                    </div>
                    Lighting Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-sm text-gray-700 leading-relaxed">{roomLighteningAnalysis}</p>
                </CardContent>
              </Card>
            )}

            {/* Recommendations */}
            {analysisData?.recommendations && analysisData.recommendations.length > 0 && (
              <Card className="shadow-sm border border-gray-200 bg-gradient-to-br from-purple-50/50 to-white">
                <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-bold flex items-center text-gray-900">
                    <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-2">
                      <Sparkles className="w-4 h-4 text-purple-600" />
                    </div>
                    Recommendations ({analysisData.recommendations.length})
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    {analysisData.recommendations.map((rec, index) => (
                      <div key={index} className="bg-white rounded-xl p-4 shadow-md border border-gray-200 hover:shadow-lg hover:border-purple-300 transition-all">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-start space-x-2 flex-1">
                            <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                              <span className="text-purple-600 font-bold text-xs">{index + 1}</span>
                            </div>
                            <h4 className="font-bold text-gray-900 text-base leading-snug">{rec.object}</h4>
                          </div>
                          {index === 0 && (
                            <span className="text-xs font-bold bg-gradient-to-r from-amber-400 to-orange-500 text-white px-3 py-1 rounded-full shadow-sm">
                              ⭐ Top Pick
                            </span>
                          )}
                        </div>
                        
                        {rec.position && (
                          <div className="mb-3 p-2 bg-blue-50 rounded-lg border border-blue-200">
                            <p className="text-xs font-semibold text-blue-900 mb-1 flex items-center">
                              📍 Position
                            </p>
                            <p className="text-xs text-gray-700 leading-relaxed">{rec.position}</p>
                          </div>
                        )}
                        
                        {rec.reference_color && (
                          <div className="mb-3">
                            <p className="text-xs font-semibold text-gray-900 mb-2 flex items-center">
                              🎨 Suggested Colors
                            </p>
                            {(() => {
                              const colors = parseColorsFromText(rec.reference_color);
                              return colors.length > 0 ? (
                                <div className="flex flex-wrap gap-2">
                                  {colors.map((hexColor, i) => (
                                    <ColorSwatch key={i} color={hexColor} size="large" showHex={false} />
                                  ))}
                                </div>
                              ) : (
                                <p className="text-xs text-gray-600">{rec.reference_color}</p>
                              );
                            })()}
                          </div>
                        )}
                        
                        {rec.justification && (
                          <div className="mb-3">
                            <p className="text-xs font-semibold text-gray-900 mb-2">💡 Why this works</p>
                            <p className="text-sm text-gray-700 leading-relaxed bg-gray-50 p-3 rounded-lg">
                              {rec.justification}
                            </p>
                          </div>
                        )}
                        
                        {rec.trend_analysis && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <p className="text-xs font-bold text-purple-700 mb-2 flex items-center">
                              📊 2025 Trend Analysis
                            </p>
                            <p className="text-xs text-gray-600 leading-relaxed bg-purple-50 p-3 rounded-lg">
                              {rec.trend_analysis}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </div>
  );
}
