"use client";
import React, { useState, useMemo } from "react";
import { Transaction } from "@/types";
import {
  ChevronUpIcon,
  ChevronDownIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowDownTrayIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDownIcon as SelectArrowIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";

interface TransactionsTableProps {
  rows: Transaction[];
}

// Category badge component with colors
const CategoryBadge = ({ category }: { category: string }) => {
  const getCategoryColor = (cat: string) => {
    const colors: Record<string, string> = {
      'Fuel': 'bg-orange-100 text-orange-700',
      'Health/Pharmacy': 'bg-red-100 text-red-700',
      'Groceries': 'bg-green-100 text-green-700',
      'Dining': 'bg-yellow-100 text-yellow-700',
      'Transport': 'bg-blue-100 text-blue-700',
      'Utilities': 'bg-purple-100 text-purple-700',
      'Entertainment': 'bg-pink-100 text-pink-700',
      'Electronics': 'bg-orange-100 text-orange-700',
      'Shopping': 'bg-indigo-100 text-indigo-700',
      'Education': 'bg-teal-100 text-teal-700',
      'Travel': 'bg-cyan-100 text-cyan-700',
      'Insurance': 'bg-gray-100 text-gray-700',
      'Investment': 'bg-emerald-100 text-emerald-700',
      'Car/Service': 'bg-amber-100 text-amber-700',
      'Recharge/Topup': 'bg-lime-100 text-lime-700',
      'Misc': 'bg-slate-100 text-slate-700',
    };
    return colors[cat] || 'bg-gray-100 text-gray-700';
  };

  return (
    <span className={`inline-flex items-center justify-center px-3 py-1 rounded-full text-xs font-medium ${getCategoryColor(category)}`}>
      {category}
    </span>
  );
};

type SortField = keyof Transaction;
type SortDirection = "asc" | "desc";

export default function TransactionsTable({ rows }: TransactionsTableProps) {
  const [sortField, setSortField] = useState<SortField>("date");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const [searchTerm, setSearchTerm] = useState("");
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [visibleColumns, setVisibleColumns] = useState<Set<string>>(
    new Set(["date", "description", "amount", "currency", "category"])
  );
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(8);

  // Get unique categories for filter
  const categories = useMemo(() => {
    const uniqueCategories = Array.from(new Set(rows.map(row => row.category)));
    return uniqueCategories.sort();
  }, [rows]);

  // Filter and sort data
  const filteredAndSortedRows = useMemo(() => {
    const filtered = rows.filter(row => {
      const matchesSearch =
        row.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        row.category.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesCategory = filterCategory === "all" || row.category === filterCategory;

      return matchesSearch && matchesCategory;
    });

    // Sort data
    filtered.sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];

      if (typeof aValue === "string" && typeof bValue === "string") {
        return sortDirection === "asc"
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      if (typeof aValue === "number" && typeof bValue === "number") {
        return sortDirection === "asc" ? aValue - bValue : bValue - aValue;
      }

      return 0;
    });

    return filtered;
  }, [rows, searchTerm, filterCategory, sortField, sortDirection]);

  // Pagination calculations
  const totalPages = Math.ceil(filteredAndSortedRows.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedRows = filteredAndSortedRows.slice(startIndex, endIndex);

  // Reset to first page when filters change
  React.useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, filterCategory]);

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const goToPreviousPage = () => {
    setCurrentPage(prev => Math.max(1, prev - 1));
  };

  const goToNextPage = () => {
    setCurrentPage(prev => Math.min(totalPages, prev + 1));
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const toggleColumn = (column: string) => {
    const newVisibleColumns = new Set(visibleColumns);
    if (newVisibleColumns.has(column)) {
      newVisibleColumns.delete(column);
    } else {
      newVisibleColumns.add(column);
    }
    setVisibleColumns(newVisibleColumns);
  };


  const formatAmount = (amount: number, currency: string) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const downloadCSV = () => {
    // Create CSV headers
    const headers = ["Date", "Description", "Amount", "Category", "Rationale", "Currency"];

    // Create CSV content
    const csvContent = [
      headers.join(","),
      ...filteredAndSortedRows.map(row => [
        formatDate(row.date),
        `"${row.description.replace(/"/g, '""')}"`, // Escape quotes in description
        row.amount,
        `"${row.category}"`,
        `"${row.rationale || ""}"`,
        `"${row.currency}"` // Wrap currency in quotes for clarity
      ].join(","))
    ].join("\n");

    // Get unique currencies for filename
    const currencies = Array.from(new Set(filteredAndSortedRows.map(row => row.currency)));
    const currencySuffix = currencies.length === 1 ? `_${currencies[0]}` : '_MultiCurrency';

    // Create and download file
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `transactions_${new Date().toISOString().split('T')[0]}${currencySuffix}.csv`);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!rows || rows.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-8 text-center">
        <div className="text-gray-400 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No transactions found</h3>
        <p className="text-gray-500">Upload a CSV file to see your categorized transactions.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="bg-white p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Transaction Details</h2>
            <p className="text-sm text-gray-500">
              Showing {filteredAndSortedRows.length} of {rows.length} transactions
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <MagnifyingGlassIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none" />
              <input
                type="text"
                placeholder="Search transactions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64 pl-10 pr-4 py-2.5 text-sm text-gray-900 placeholder-gray-500 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 hover:border-gray-400"
              />
            </div>
            <div className="relative">
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="w-48 pl-3 pr-10 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 hover:border-gray-400 appearance-none cursor-pointer"
              >
                <option value="all">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <SelectArrowIcon className="h-4 w-4 text-gray-400" />
              </div>
            </div>
            <button
              onClick={downloadCSV}
              className="group relative inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-medium text-sm rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
            >
              <ArrowDownTrayIcon className="h-4 w-4 group-hover:animate-bounce" />
              <span className="hidden sm:inline">Download CSV</span>
              <span className="sm:hidden">Download</span>
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-lg opacity-0 group-hover:opacity-20 transition-opacity duration-200"></div>
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {visibleColumns.has("date") && (
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort("date")}
                >
                  <div className="flex items-center justify-between">
                    <span>Date</span>
                    {sortField === "date" && (
                      sortDirection === "asc" ? (
                        <ChevronUpIcon className="h-4 w-4" />
                      ) : (
                        <ChevronDownIcon className="h-4 w-4" />
                      )
                    )}
                  </div>
                </th>
              )}
              {visibleColumns.has("description") && (
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort("description")}
                >
                  <div className="flex items-center justify-between">
                    <span>Description</span>
                    {sortField === "description" && (
                      sortDirection === "asc" ? (
                        <ChevronUpIcon className="h-4 w-4" />
                      ) : (
                        <ChevronDownIcon className="h-4 w-4" />
                      )
                    )}
                  </div>
                </th>
              )}
              {visibleColumns.has("amount") && (
                <th
                  className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort("amount")}
                >
                  <div className="flex items-center justify-end gap-1">
                    <span>Amount</span>
                    {sortField === "amount" && (
                      sortDirection === "asc" ? (
                        <ChevronUpIcon className="h-4 w-4" />
                      ) : (
                        <ChevronDownIcon className="h-4 w-4" />
                      )
                    )}
                  </div>
                </th>
              )}
              {visibleColumns.has("category") && (
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort("category")}
                >
                  <div className="flex items-center justify-between">
                    <span>Category</span>
                    {sortField === "category" && (
                      sortDirection === "asc" ? (
                        <ChevronUpIcon className="h-4 w-4" />
                      ) : (
                        <ChevronDownIcon className="h-4 w-4" />
                      )
                    )}
                  </div>
                </th>
              )}
              {visibleColumns.has("rationale") && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rationale
                </th>
              )}
              {visibleColumns.has("currency") && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Currency
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedRows.map((row, index) => (
              <tr key={index} className="hover:bg-gray-50 transition-colors">
                {visibleColumns.has("date") && (
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 text-left">
                    {formatDate(row.date)}
                  </td>
                )}
                {visibleColumns.has("description") && (
                  <td className="px-4 py-2 text-sm text-gray-900 text-left">
                    <div className="truncate max-w-xs" title={row.description}>
                      {row.description}
                    </div>
                  </td>
                )}
                {visibleColumns.has("amount") && (
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                    {formatAmount(row.amount, row.currency)}
                  </td>
                )}
                {visibleColumns.has("category") && (
                  <td className="px-4 py-2 whitespace-nowrap text-left">
                    <CategoryBadge category={row.category} />
                  </td>
                )}
                {visibleColumns.has("rationale") && (
                  <td className="px-4 py-2 text-sm text-gray-500 text-left">
                    {row.rationale || "-"}
                  </td>
                )}
                {visibleColumns.has("currency") && (
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500 text-left">
                    {row.currency}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="bg-gray-50 px-6 py-3 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <p className="text-sm text-gray-500">
              Showing {startIndex + 1}-{Math.min(endIndex, filteredAndSortedRows.length)} of {filteredAndSortedRows.length} transactions
            </p>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center gap-1">
                <button
                  onClick={goToPreviousPage}
                  disabled={currentPage === 1}
                  className="p-1 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeftIcon className="h-4 w-4 text-gray-600" />
                </button>

                <div className="flex items-center gap-1">
                  {Array.from({ length: Math.min(4, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 4) {
                      pageNum = i + 1;
                    } else if (currentPage <= 2) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 1) {
                      pageNum = totalPages - 3 + i;
                    } else {
                      pageNum = currentPage - 1 + i;
                    }

                    return (
                      <button
                        key={pageNum}
                        onClick={() => goToPage(pageNum)}
                        className={clsx(
                          "px-3 py-1 text-sm rounded transition-colors",
                          currentPage === pageNum
                            ? "bg-blue-500 text-white"
                            : "hover:bg-gray-200 text-gray-700"
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
                  className="p-1 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRightIcon className="h-4 w-4 text-gray-600" />
                </button>
              </div>
            )}
          </div>

          {/* Column Visibility Dropdown */}
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <FunnelIcon className="h-4 w-4" />
            <span>Column visibility:</span>
            <div className="relative">
              <select
                value=""
                onChange={(e) => {
                  if (e.target.value) {
                    toggleColumn(e.target.value);
                    e.target.value = "";
                  }
                }}
                className="pl-3 pr-10 py-2 text-xs text-gray-700 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 hover:border-gray-400 appearance-none cursor-pointer"
              >
                <option value="">Select column to toggle</option>
                {["date", "description", "amount", "category", "rationale", "currency"].map(column => (
                  <option key={column} value={column}>
                    {visibleColumns.has(column) ? "✓" : "○"} {column}
                  </option>
                ))}
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <SelectArrowIcon className="h-3 w-3 text-gray-400" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
