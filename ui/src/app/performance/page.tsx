"use client";

import React, { useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { MetricAPI, PipelineOperation } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

// Default operations for benchmarking
const BENCHMARK_OPERATIONS = {
  filter: { operation: 'greater_than', value: 50 },
  aggregate: { operation: 'sum' },
  timeGroup: { operation: 'group_by_hour', aggregation: 'avg' },
  complex: [
    { operation: 'greater_than', value: 50 },
    { operation: 'group_by_hour', aggregation: 'sum' }
  ]
};

// Data sizes for benchmarking
const DATA_SIZES = [100, 500, 1000, 5000, 10000];

type BenchmarkResult = {
  operation: string;
  dataSize: number;
  executionTime: number;
};

export default function PerformancePage() {
  const [benchmarkResults, setBenchmarkResults] = useState<BenchmarkResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Generate random metrics data
  const generateRandomMetrics = (count: number) => {
    const metrics = [];
    const now = Math.floor(Date.now() / 1000);
    
    for (let i = 0; i < count; i++) {
      metrics.push({
        value: Math.floor(Math.random() * 1000),
        timestamp: now - Math.floor(Math.random() * 86400 * 30) // Random time in the last 30 days
      });
    }
    
    return metrics;
  };

  // Run a single benchmark
  const runSingleBenchmark = async (
    operationName: string, 
    operations: PipelineOperation | PipelineOperation[], 
    dataSize: number
  ): Promise<BenchmarkResult> => {
    // Generate test data
    const metrics = generateRandomMetrics(dataSize);
    
    // Normalize operations to array
    const operationsArray = Array.isArray(operations) ? operations : [operations];
    
    // Run the benchmark
    const startTime = performance.now();
    
    try {
      await MetricAPI.pipelineTransform(operationsArray);
      const endTime = performance.now();
      
      return {
        operation: operationName,
        dataSize,
        executionTime: endTime - startTime
      };
    } catch (error) {
      console.error(`Benchmark failed for ${operationName} with ${dataSize} records:`, error);
      throw error;
    }
  };

  // Run all benchmarks
  const runBenchmarks = async () => {
    setIsRunning(true);
    setError(null);
    setBenchmarkResults([]);
    
    const results: BenchmarkResult[] = [];
    const totalBenchmarks = Object.keys(BENCHMARK_OPERATIONS).length * DATA_SIZES.length;
    let completedBenchmarks = 0;
    
    try {
      // Run benchmarks for each operation type and data size
      for (const [opName, operations] of Object.entries(BENCHMARK_OPERATIONS)) {
        for (const dataSize of DATA_SIZES) {
          const result = await runSingleBenchmark(opName, operations as any, dataSize);
          results.push(result);
          
          // Update progress
          completedBenchmarks++;
          setProgress(Math.floor((completedBenchmarks / totalBenchmarks) * 100));
        }
      }
      
      setBenchmarkResults(results);
    } catch (err: any) {
      setError(`Benchmark failed: ${err.message || 'Unknown error'}`);
    } finally {
      setIsRunning(false);
      setProgress(100);
    }
  };

  // Format data for charts
  const getOperationComparisonData = () => {
    const data: any[] = [];
    
    // Group by data size
    DATA_SIZES.forEach(size => {
      const dataPoint: any = { dataSize: size };
      
      // Add execution time for each operation
      Object.keys(BENCHMARK_OPERATIONS).forEach(opName => {
        const result = benchmarkResults.find(r => r.operation === opName && r.dataSize === size);
        if (result) {
          dataPoint[opName] = result.executionTime;
        }
      });
      
      data.push(dataPoint);
    });
    
    return data;
  };

  // Format data for operation-specific charts
  const getOperationScalingData = (operationName: string) => {
    return benchmarkResults
      .filter(result => result.operation === operationName)
      .map(result => ({
        dataSize: result.dataSize,
        executionTime: result.executionTime
      }));
  };

  return (
    <DashboardLayout>
      <div className="md:flex md:items-start md:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Performance Benchmarks</h1>
          <p className="mt-1 text-sm text-gray-500">
            Measure and compare the performance of different transformations with varying data sizes
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <button
            onClick={runBenchmarks}
            disabled={isRunning}
            className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
              isRunning ? 'bg-indigo-400' : 'bg-indigo-600 hover:bg-indigo-700'
            } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
          >
            {isRunning ? 'Running Benchmarks...' : 'Run Benchmarks'}
          </button>
        </div>
      </div>

      {/* Progress and errors */}
      {isRunning && (
        <div className="mb-6">
          <div className="flex justify-between mb-1">
            <span className="text-sm font-medium text-indigo-700">Running benchmarks</span>
            <span className="text-sm font-medium text-indigo-700">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: `${progress}%` }}></div>
          </div>
          <p className="text-xs text-gray-500 mt-2">This may take a few minutes depending on benchmark size</p>
        </div>
      )}

      {error && (
        <div className="p-4 mb-6 bg-red-50 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">{error}</h3>
            </div>
          </div>
        </div>
      )}

      {benchmarkResults.length > 0 ? (
        <div className="space-y-6">
          {/* Operation comparison chart */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Operation Performance Comparison</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={getOperationComparisonData()}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="dataSize" label={{ value: 'Data Size (records)', position: 'insideBottom', offset: -5 }} />
                  <YAxis label={{ value: 'Execution Time (ms)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip 
                    formatter={(value: any) => [`${value.toFixed(2)} ms`, '']}
                    labelFormatter={(label) => `Data Size: ${label} records`}
                  />
                  <Legend />
                  <Bar dataKey="filter" name="Filter" fill="#8884d8" />
                  <Bar dataKey="aggregate" name="Aggregation" fill="#82ca9d" />
                  <Bar dataKey="timeGroup" name="Time Grouping" fill="#ffc658" />
                  <Bar dataKey="complex" name="Complex Pipeline" fill="#ff8042" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Individual scaling charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.keys(BENCHMARK_OPERATIONS).map(opName => (
              <div key={opName} className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-medium text-gray-900 mb-4">{opName.charAt(0).toUpperCase() + opName.slice(1)} Scaling</h2>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={getOperationScalingData(opName)}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="dataSize" 
                        label={{ value: 'Data Size (records)', position: 'insideBottom', offset: -5 }}
                      />
                      <YAxis 
                        label={{ value: 'Time (ms)', angle: -90, position: 'insideLeft' }} 
                      />
                      <Tooltip
                        formatter={(value: any) => [`${value.toFixed(2)} ms`, 'Execution Time']}
                        labelFormatter={(label) => `${label} records`}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="executionTime" 
                        name="Execution Time" 
                        stroke="#8884d8" 
                        activeDot={{ r: 8 }} 
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ))}
          </div>

          {/* Results table */}
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6">
              <h2 className="text-lg font-medium text-gray-900">Detailed Benchmark Results</h2>
            </div>
            <div className="border-t border-gray-200">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Operation
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Data Size
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Execution Time
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {benchmarkResults.map((result, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {result.operation}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {result.dataSize} records
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {result.executionTime.toFixed(2)} ms
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No benchmark data</h3>
            <p className="mt-1 text-sm text-gray-500">Start by running the benchmarks to measure performance.</p>
            <div className="mt-6">
              <button
                onClick={runBenchmarks}
                disabled={isRunning}
                className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                  isRunning ? 'bg-indigo-400' : 'bg-indigo-600 hover:bg-indigo-700'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
              >
                {isRunning ? 'Running Benchmarks...' : 'Run Benchmarks'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Performance explanation */}
      <div className="mt-6 bg-white rounded-lg shadow overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900">About The Benchmark</h3>
          <div className="mt-2 text-sm text-gray-500">
            <p className="mb-2">
              These benchmarks measure the performance of various transformation operations provided by the Rust/Python backend.
            </p>
            <p className="mb-2">
              The operations being tested include:
            </p>
            <ul className="list-disc pl-5 mb-2">
              <li><strong>Filter</strong> - Filtering metrics based on value using a greater-than operation</li>
              <li><strong>Aggregation</strong> - Summing all metric values into a single result</li>
              <li><strong>Time Grouping</strong> - Grouping metrics by hour and calculating the average within each group</li>
              <li><strong>Complex Pipeline</strong> - A multi-step transformation that filters metrics and then groups them by hour</li>
            </ul>
            <p>
              Each operation is tested with different data sizes to demonstrate how performance scales with increasing data volumes.
              The execution times include API call overhead, which is useful for real-world performance assessment.
            </p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}