import React, { useState } from "react";
import { ProcessedData } from "@/types";

interface FileUploaderProps {
    onUpload: (data: ProcessedData) => void;
}

export default function FileUploader({ onUpload }: FileUploaderProps) {
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [dragActive, setDragActive] = useState(false);

    const parseErrorMessage = (errorMessage: string) => {
        // Parse different types of error messages for better display
        if (errorMessage.includes("Missing required columns")) {
            // Extract missing columns and found columns from the error message
            const missingMatch = errorMessage.match(/Missing required columns: ([^.]+)/);
            const foundMatch = errorMessage.match(/Found columns: ([^.]+)/);
            
            const missingColumns = missingMatch ? missingMatch[1].split(',').map(col => col.trim()) : [];
            const foundColumns = foundMatch ? foundMatch[1].split(',').map(col => col.trim()) : [];
            
            return {
                type: "columns",
                title: "Missing Required Columns",
                message: `Missing required columns: ${missingColumns.join(', ')}. Please ensure your CSV contains columns named: '${missingColumns.join("', '")}' (or similar variations).`,
                missingColumns,
                foundColumns,
                suggestions: [
                    "Ensure your CSV has columns named: date, description, amount, currency",
                    "Column names are case-insensitive (e.g., 'Date', 'DATE', 'date' all work)",
                    "You can also use variations like 'transaction_date', 'desc', 'value', 'ccy'"
                ]
            };
        } else if (errorMessage.includes("Data validation failed")) {
            // Parse specific validation errors from the message
            const errors = errorMessage.split(';').map(err => err.trim());
            const fieldErrors: { [key: string]: string[] } = {};
            
            errors.forEach(error => {
                if (error.includes('date:')) {
                    fieldErrors.date = fieldErrors.date || [];
                    fieldErrors.date.push(error.replace('date:', '').trim());
                } else if (error.includes('amount:')) {
                    fieldErrors.amount = fieldErrors.amount || [];
                    fieldErrors.amount.push(error.replace('amount:', '').trim());
                } else if (error.includes('description:')) {
                    fieldErrors.description = fieldErrors.description || [];
                    fieldErrors.description.push(error.replace('description:', '').trim());
                } else if (error.includes('currency:')) {
                    fieldErrors.currency = fieldErrors.currency || [];
                    fieldErrors.currency.push(error.replace('currency:', '').trim());
                }
            });

            return {
                type: "data",
                title: "Data Format Issues Found",
                message: "We found some issues with your CSV data that need to be fixed before processing.",
                fieldErrors,
                suggestions: [
                    "Check that dates are in formats like YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY",
                    "Ensure amounts are positive numbers (e.g., 123.45, 1000)",
                    "Verify currency codes are 3-letter ISO codes (USD, EUR, GBP, etc.)",
                    "Make sure descriptions are not empty"
                ]
            };
        } else if (errorMessage.includes("File validation failed")) {
            return {
                type: "file",
                title: "File Issues",
                message: errorMessage,
                suggestions: [
                    "Ensure the file is a valid CSV format",
                    "Check that the file is not empty",
                    "Make sure the file size is under 10MB",
                    "Save the file as UTF-8 encoding"
                ]
            };
        } else {
            return {
                type: "general",
                title: "Upload Error",
                message: errorMessage,
                suggestions: [
                    "Check your internet connection",
                    "Try uploading a different CSV file",
                    "Ensure the file is properly formatted"
                ]
            };
        }
    };

    const handleFileUpload = async (file: File) => {
        setUploading(true);
        setError(null);
        setSuccess(false);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("http://localhost:8000/upload_csv", {
            method: "POST",
            body: formData,
        });

            if (!res.ok) {
                // Try to get detailed error message from response
                let errorMessage = `Upload failed: ${res.statusText}`;
                try {
                    const errorData = await res.json();
                    if (errorData.detail) {
                        errorMessage = errorData.detail;
                    }
                } catch {
                    // If JSON parsing fails, use the status text
                }
                throw new Error(errorMessage);
            }

            const uploadResponse = await res.json();

            // Transform the response to match our ProcessedData interface
            const processedData: ProcessedData = {
                rows: uploadResponse.rows || [],
                totals: uploadResponse.totals || {},
                summary: {
                    summary: uploadResponse.summary?.summary || [uploadResponse.summary || "No summary available"],
                    budget_tip: uploadResponse.summary?.budget_tip || "Consider tracking recurring subscriptions and canceling unused ones.",
                    tax_hint: uploadResponse.summary?.tax_hint || "Save receipts for business-related purchases; consult a tax professional for specifics."
                }
            };

            setSuccess(true);
            onUpload(processedData);
            
            // Clear success message after 3 seconds
            setTimeout(() => setSuccess(false), 3000);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Upload failed");
        } finally {
            setUploading(false);
        }
    };

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        await handleFileUpload(file);
    };

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const file = e.dataTransfer.files[0];
            if (file.type === "text/csv" || file.name.endsWith('.csv')) {
                await handleFileUpload(file);
            } else {
                setError("Please upload a CSV file only");
            }
        }
    };

    const errorInfo = error ? parseErrorMessage(error) : null;

    return (
        <div className="min-h-[calc(100vh-200px)] flex items-center justify-center p-4">
            <div className="w-full max-w-2xl bg-white rounded-xl shadow-lg border border-gray-100 p-6">
            <div className="text-center">
                {/* Success State */}
                {success && (
                    <div className="mb-6 p-4 bg-gradient-to-br from-emerald-50 to-emerald-100 border border-emerald-200 rounded-lg">
                        <div className="flex items-center justify-center gap-3">
                            <div className="p-2 bg-emerald-500 rounded-lg">
                                <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-emerald-800">Upload Successful!</h3>
                                <p className="text-sm text-emerald-700">Your transactions have been processed and categorized by AI</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Upload Icon */}
                <div className={`mx-auto w-12 h-12 rounded-lg flex items-center justify-center mb-4 transition-colors ${
                    success 
                        ? 'bg-emerald-100' 
                        : uploading 
                            ? 'bg-blue-100 animate-pulse'
                            : 'bg-blue-100'
                }`}>
                    {success ? (
                        <svg className="h-6 w-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    ) : (
                        <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                    )}
                </div>

                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    {success ? 'Transaction Data Processed' : 'Upload Transaction Data'}
                </h2>
                <p className="text-sm text-gray-600 mb-6 max-w-md mx-auto">
                    {success 
                        ? 'Your CSV file has been successfully processed with AI-powered categorization.'
                        : 'Upload a CSV file with your transaction data for AI-powered analysis and categorization.'
                    }
                </p>
                
                {/* Drag and Drop Area */}
                <div className="relative">
                    <input 
                        type="file" 
                        accept=".csv" 
                        onChange={handleFileChange}
                        disabled={uploading}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed z-10"
                    />
                    <div 
                        className={`border-2 border-dashed rounded-lg p-6 transition-all duration-200 ${
                            dragActive 
                                ? 'border-blue-400 bg-blue-50' 
                                : uploading 
                            ? 'border-blue-300 bg-blue-50' 
                                    : success
                                        ? 'border-emerald-300 bg-emerald-50'
                            : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                        }`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                    >
                        <div className="flex flex-col items-center justify-center gap-3">
                            {uploading ? (
                                <>
                                    <svg className="animate-spin h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    <div className="text-center">
                                        <p className="text-sm font-medium text-blue-600">Processing...</p>
                                        <p className="text-xs text-blue-500 mt-1">AI is analyzing your transactions</p>
                                    </div>
                                </>
                            ) : success ? (
                                <>
                                    <svg className="h-6 w-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <div className="text-center">
                                        <p className="text-sm font-medium text-emerald-600">Upload Complete!</p>
                                        <p className="text-xs text-emerald-500 mt-1">Click to upload another file</p>
                                    </div>
                                </>
                            ) : (
                                <div className="flex items-center gap-3">
                                    <svg className="h-6 w-6 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                                    <div className="text-center flex-1">
                                        <p className="text-sm font-medium text-gray-600">
                                            {dragActive ? 'Drop your CSV file here' : 'Choose CSV file or drag and drop'}
                                        </p>
                                    </div>
                                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full flex-shrink-0">
                                        Max 10MB
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
                
                {/* Enhanced Error Messages */}
                {errorInfo && (
                    <div className="mt-6 p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-lg">
                        <div className="flex items-start gap-3">
                            <div className="p-1 bg-red-500 rounded">
                                <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div className="flex-1">
                                <h4 className="text-sm font-semibold text-red-800 mb-2">{errorInfo.title}</h4>
                                <p className="text-sm text-red-700 mb-3">{errorInfo.message}</p>
                                
                                {/* Show specific missing and found columns */}
                                {errorInfo.type === "columns" && (
                                    <div className="mb-3 space-y-2">
                                        {errorInfo.missingColumns && errorInfo.missingColumns.length > 0 && (
                                <div className="bg-red-100 rounded-lg p-3">
                                                <h5 className="text-xs font-medium text-red-800 mb-2">❌ Missing Columns:</h5>
                                                <div className="flex flex-wrap gap-1">
                                                    {errorInfo.missingColumns.map((col, index) => (
                                                        <span key={index} className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-200 text-red-800 border border-red-300">
                                                            {col}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                        
                                        {errorInfo.foundColumns && errorInfo.foundColumns.length > 0 && (
                                            <div className="bg-green-100 rounded-lg p-3">
                                                <h5 className="text-xs font-medium text-green-800 mb-2">✅ Found Columns:</h5>
                                                <div className="flex flex-wrap gap-1">
                                                    {errorInfo.foundColumns.map((col, index) => (
                                                        <span key={index} className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-200 text-green-800 border border-green-300">
                                                            {col}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                                
                                {/* Show specific field validation errors */}
                                {errorInfo.type === "data" && errorInfo.fieldErrors && (
                                    <div className="mb-3">
                                        <h5 className="text-xs font-medium text-red-800 mb-2">⚠️ Field Issues:</h5>
                                        <div className="space-y-2">
                                            {Object.entries(errorInfo.fieldErrors).map(([field, errors]) => (
                                                <div key={field} className="bg-red-100 rounded-lg p-3">
                                                    <h6 className="text-xs font-medium text-red-800 mb-1 capitalize">{field} errors:</h6>
                                    <ul className="text-xs text-red-700 space-y-1">
                                                        {errors.map((error, index) => (
                                                            <li key={index} className="flex items-start gap-2">
                                                                <span className="text-red-500 mt-1">•</span>
                                                                <span>{error}</span>
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                
                                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                                    <h5 className="text-xs font-medium text-blue-800 mb-2">How to fix:</h5>
                                    <ul className="text-xs text-blue-700 space-y-1">
                                        {errorInfo.suggestions.slice(0, 3).map((suggestion, index) => (
                                            <li key={index} className="flex items-start gap-2">
                                                <span className="text-blue-500 mt-1">•</span>
                                                <span>{suggestion}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
                
                {/* Simplified Quick Tips */}
                {!error && !success && (
                    <div className="mt-6 p-3 bg-gradient-to-r from-purple-50 to-blue-100 border border-blue-200 rounded-lg">
                        <div className="flex items-center flex-col gap-3">
                            <div className="w-full flex-col flex items-center gap-3 flex-1">
                                <div className="p-1 bg-purple-500 rounded flex-shrink-0">
                                <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                                <div className="flex-1">
                                    <span className="text-sm font-medium text-blue-800">Quick Tips: </span>
                                    <span className="text-xs text-blue-700">
                                        Flexible columns • AI categorization • Multiple formats • Max 10MB
                                    </span>
                        </div>
                            </div>
                            <div className="flex items-center gap-1 flex-shrink-0">
                                <svg className="h-3 w-3 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                                <span className="text-xs font-medium text-emerald-800">Pro: Use &apos;desc&apos;, &apos;value&apos;, &apos;ccy&apos;</span>
                            </div>
                        </div>
                    </div>
                )}
                </div>
            </div>
        </div>
    );
}
