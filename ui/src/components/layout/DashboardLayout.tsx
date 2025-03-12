import React, { ReactNode } from 'react';
import Link from 'next/link';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Metric Query Interface</h1>
            <p className="text-sm text-gray-500">Rust/Python Hybrid Backend Demo</p>
          </div>
          <nav className="flex space-x-4">
            <Link 
              href="/"
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-900 hover:bg-gray-100"
            >
              Dashboard
            </Link>
            <Link 
              href="/playground"
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-900 hover:bg-gray-100"
            >
              Playground
            </Link>
            <Link 
              href="/performance"
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-900 hover:bg-gray-100"
            >
              Performance
            </Link>
          </nav>
        </div>
      </header>
      
      <main className="flex-grow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>
      
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-500">
              Metric Query Interface Demo &copy; {new Date().getFullYear()}
            </div>
            <div className="flex space-x-4 text-sm text-gray-500">
              <a href="https://github.com/rileyseaburg/metric-query-rs" className="hover:text-gray-900">
                GitHub Repository
              </a>
              <a href="/docs" className="hover:text-gray-900">
                Documentation
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}