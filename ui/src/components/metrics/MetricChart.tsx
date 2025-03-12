import React from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { Metric } from '@/lib/api';

interface MetricChartProps {
  originalMetrics?: Metric[];
  transformedMetrics?: Metric[];
  title?: string;
  height?: number;
}

// Define chart data structure with optional values
interface ChartDataPoint {
  timestamp: number;
  formattedTime: string;
  originalValue?: number;
  transformedValue?: number;
}

export default function MetricChart({ 
  originalMetrics = [], 
  transformedMetrics = [], 
  title = "Metric Visualization",
  height = 400
}: MetricChartProps) {
  
  // Convert timestamps to readable dates for display
  const formatData = (metrics: Metric[]) => {
    return metrics.map(metric => ({
      ...metric,
      formattedTime: new Date(metric.timestamp * 1000).toLocaleString(),
    }));
  };

  const formattedOriginal = formatData(originalMetrics);
  const formattedTransformed = formatData(transformedMetrics);
  
  // Create chart data array with proper typing
  const chartData: ChartDataPoint[] = [];
  
  // Add original data points
  formattedOriginal.forEach(original => {
    const dataPoint: ChartDataPoint = {
      timestamp: original.timestamp,
      formattedTime: original.formattedTime,
      originalValue: original.value,
    };
    
    // Find matching timestamp in transformed data (if any)
    const transformed = formattedTransformed.find(t => t.timestamp === original.timestamp);
    if (transformed) {
      dataPoint.transformedValue = transformed.value;
    }
    
    chartData.push(dataPoint);
  });

  // Add transformed data points that don't have original counterparts
  formattedTransformed.forEach(transformed => {
    if (!chartData.some(d => d.timestamp === transformed.timestamp)) {
      chartData.push({
        timestamp: transformed.timestamp,
        formattedTime: transformed.formattedTime,
        transformedValue: transformed.value,
      });
    }
  });
  
  // Sort by timestamp
  chartData.sort((a, b) => a.timestamp - b.timestamp);

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="formattedTime" 
              label={{ value: 'Time', position: 'insideBottomRight', offset: -10 }}
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
            />
            <YAxis 
              label={{ value: 'Value', angle: -90, position: 'insideLeft' }} 
            />
            <Tooltip 
              formatter={(value: any) => [`${value}`, '']}
              labelFormatter={(label) => `Time: ${label}`}
            />
            <Legend />
            {originalMetrics.length > 0 && (
              <Line 
                type="monotone" 
                dataKey="originalValue" 
                name="Original" 
                stroke="#8884d8" 
                activeDot={{ r: 8 }} 
                strokeWidth={2}
              />
            )}
            {transformedMetrics.length > 0 && (
              <Line 
                type="monotone" 
                dataKey="transformedValue" 
                name="Transformed" 
                stroke="#82ca9d" 
                activeDot={{ r: 8 }} 
                strokeWidth={2}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}