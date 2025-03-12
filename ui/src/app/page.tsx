"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { MetricAPI } from '@/lib/api';

export default function HomePage() {
  const [apiInfo, setApiInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch API info when component mounts
  useEffect(() => {
    const fetchApiInfo = async () => {
      try {
        // Use relative URL that will be handled by Next.js rewrites
        const response = await fetch('/api/');
        if (!response.ok) {
          throw new Error('Failed to fetch API info');
        }
        const data = await response.json();
        setApiInfo(data);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching API info:', error);
        setApiInfo(null);
        setIsLoading(false);
      }
    };

    fetchApiInfo();
  }, []);

  return (
    <DashboardLayout>
      <div className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="overflow-hidden bg-white shadow sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6">
              <h1 className="text-2xl font-bold text-gray-900">
                Metric Query Interface Demo
              </h1>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                A Rust/Python hybrid backend for transforming time-series metrics
              </p>
            </div>
            
            {isLoading ? (
              <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
                <div className="animate-pulse flex space-x-4">
                  <div className="flex-1 space-y-6 py-1">
                    <div className="h-2 bg-slate-200 rounded"></div>
                    <div className="space-y-3">
                      <div className="grid grid-cols-3 gap-4">
                        <div className="h-2 bg-slate-200 rounded col-span-2"></div>
                        <div className="h-2 bg-slate-200 rounded col-span-1"></div>
                      </div>
                      <div className="h-2 bg-slate-200 rounded"></div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
                <dl className="sm:divide-y sm:divide-gray-200">
                  <div className="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Architecture</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                      <span className="block">
                        <span className="font-semibold">Backend:</span> Rust core library with Python bindings
                      </span>
                      <span className="block">
                        <span className="font-semibold">API:</span> Flask REST API
                      </span>
                      <span className="block">
                        <span className="font-semibold">Frontend:</span> React with Next.js
                      </span>
                    </dd>
                  </div>
                  
                  <div className="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Key Features</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                      <ul className="divide-y divide-gray-200 rounded-md border border-gray-200">
                        <li className="flex items-center justify-between py-3 pl-3 pr-4 text-sm">
                          <div className="flex w-0 flex-1 items-center">
                            <span className="ml-2 w-0 flex-1 truncate">Filtering operations (GT, LT, GTE, LTE, Eq)</span>
                          </div>
                        </li>
                        <li className="flex items-center justify-between py-3 pl-3 pr-4 text-sm">
                          <div className="flex w-0 flex-1 items-center">
                            <span className="ml-2 w-0 flex-1 truncate">Aggregation operations (SUM, AVG, MIN, MAX)</span>
                          </div>
                        </li>
                        <li className="flex items-center justify-between py-3 pl-3 pr-4 text-sm">
                          <div className="flex w-0 flex-1 items-center">
                            <span className="ml-2 w-0 flex-1 truncate">Time grouping (HOUR, MINUTE, DAY)</span>
                          </div>
                        </li>
                        <li className="flex items-center justify-between py-3 pl-3 pr-4 text-sm">
                          <div className="flex w-0 flex-1 items-center">
                            <span className="ml-2 w-0 flex-1 truncate">Fluent Pipeline API for chaining transformations</span>
                          </div>
                        </li>
                        <li className="flex items-center justify-between py-3 pl-3 pr-4 text-sm">
                          <div className="flex w-0 flex-1 items-center">
                            <span className="ml-2 w-0 flex-1 truncate">Plugin architecture for extensibility</span>
                          </div>
                        </li>
                      </ul>
                    </dd>
                  </div>
                  
                  <div className="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Performance Highlights</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                      <ul className="list-disc pl-5 space-y-1">
                        <li>Rust core for high-performance metric processing</li>
                        <li>Memory-efficient pipeline execution</li>
                        <li>PyO3 bindings for seamless Python integration</li>
                        <li>Optimized for streaming data environments</li>
                      </ul>
                    </dd>
                  </div>
                </dl>
              </div>
            )}
            
            <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
              <h2 className="text-lg font-medium text-gray-900">Explore the Demo</h2>
              <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:shadow">
                  <Link href="/playground" className="focus:outline-none">
                    <div className="flex items-center">
                      <span className="flex h-12 w-12 items-center justify-center rounded-md bg-indigo-500 text-white">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12a7.5 7.5 0 0015 0m-15 0a7.5 7.5 0 1115 0m-15 0H3m16.5 0H21m-1.5 0H12m-8.457 3.077l1.41-.513m14.095-5.13l1.41-.513M5.106 17.785l1.15-.964m11.49-9.642l1.149-.964M7.501 19.795l.75-1.3m7.5-12.99l.75-1.3m-6.063 16.658l.26-1.477m2.605-14.772l.26-1.477m0 17.726l-.26-1.477M10.698 4.614l-.26-1.477M16.5 19.794l-.75-1.299M7.5 4.205L12 12m6.894 5.785l-1.149-.964M6.256 7.178l-1.15-.964m15.352 8.864l-1.41-.513M4.954 9.435l-1.41-.514M12.002 12l-3.75 6.495" />
                        </svg>
                      </span>
                      <div className="ml-4 flex-1">
                        <div className="font-medium text-gray-900">Transformation Playground</div>
                        <div className="text-sm text-gray-500">Build, test, and visualize metric transformations</div>
                      </div>
                    </div>
                  </Link>
                </div>
                
                <div className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:shadow">
                  <Link href="/performance" className="focus:outline-none">
                    <div className="flex items-center">
                      <span className="flex h-12 w-12 items-center justify-center rounded-md bg-indigo-500 text-white">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                        </svg>
                      </span>
                      <div className="ml-4 flex-1">
                        <div className="font-medium text-gray-900">Performance Benchmarks</div>
                        <div className="text-sm text-gray-500">Measure and compare transformation performance</div>
                      </div>
                    </div>
                  </Link>
                </div>

                <div className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:shadow">
                  <a href="https://api-metrics-demandbase.rileyseaburg.com/apidocs/#/Documentation/get_" target="_blank" rel="noopener noreferrer" className="focus:outline-none">
                    <div className="flex items-center">
                      <span className="flex h-12 w-12 items-center justify-center rounded-md bg-green-500 text-white">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 7.5h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5m3-9h3.375c.621 0 1.125.504 1.125 1.125V18a2.25 2.25 0 01-2.25 2.25M16.5 7.5V18a2.25 2.25 0 002.25 2.25M16.5 7.5V4.875c0-.621-.504-1.125-1.125-1.125H4.125C3.504 3.75 3 4.254 3 4.875V18a2.25 2.25 0 002.25 2.25h13.5M6 7.5h3v3H6v-3z" />
                        </svg>
                      </span>
                      <div className="ml-4 flex-1">
                        <div className="font-medium text-gray-900">API Documentation</div>
                        <div className="text-sm text-gray-500">Explore the Swagger documentation for the main API service</div>
                      </div>
                    </div>
                  </a>
                </div>
              </div>
            </div>
            
            <div className="border-t border-gray-200 bg-gray-50 px-4 py-5 sm:px-6">
              <div className="text-sm">
                <Link href="https://github.com/rileyseaburg/metric-query-rs" className="font-medium text-indigo-600 hover:text-indigo-500">
                  View source code on GitHub &rarr;
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
