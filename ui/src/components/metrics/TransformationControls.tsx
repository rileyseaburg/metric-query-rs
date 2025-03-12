import React, { useState } from 'react';
import { PipelineOperation } from '@/lib/api';

interface TransformationControlsProps {
  onApplyTransformations: (pipeline: PipelineOperation[]) => void;
}

export default function TransformationControls({ onApplyTransformations }: TransformationControlsProps) {
  const [pipeline, setPipeline] = useState<PipelineOperation[]>([]);
  const [currentOperation, setCurrentOperation] = useState<Partial<PipelineOperation>>({
    operation: 'filter'
  });

  // Handle form input changes
  const handleOperationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const operation = e.target.value;
    setCurrentOperation({ operation });
  };

  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCurrentOperation({ ...currentOperation, type: e.target.value });
  };

  const handleValueChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentOperation({ ...currentOperation, value: parseInt(e.target.value) });
  };

  const handleAggregationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCurrentOperation({ ...currentOperation, aggregation: e.target.value });
  };

  // Add current operation to pipeline
  const addOperation = () => {
    if (!currentOperation.operation) return;

    // Validate required fields based on operation type
    if (currentOperation.operation === 'filter' && 
        (!currentOperation.type || currentOperation.value === undefined)) {
      alert('Filter operations require type and value');
      return;
    }

    if (currentOperation.operation === 'aggregate' && !currentOperation.type) {
      alert('Aggregate operations require type');
      return;
    }

    if (currentOperation.operation === 'group_by' && 
        (!currentOperation.time_grouping || !currentOperation.aggregation)) {
      alert('Group by operations require time grouping and aggregation');
      return;
    }

    setPipeline([...pipeline, currentOperation as PipelineOperation]);
    
    // Reset current operation
    setCurrentOperation({ operation: 'filter' });
  };

  // Remove operation from pipeline
  const removeOperation = (index: number) => {
    const newPipeline = [...pipeline];
    newPipeline.splice(index, 1);
    setPipeline(newPipeline);
  };

  // Apply pipeline
  const applyTransformations = () => {
    if (pipeline.length === 0) {
      alert('Please add at least one transformation');
      return;
    }
    onApplyTransformations(pipeline);
  };

  // Clear pipeline
  const clearPipeline = () => {
    setPipeline([]);
  };

  // Render different controls based on operation type
  const renderOperationControls = () => {
    switch (currentOperation.operation) {
      case 'filter':
        return (
          <>
            <div className="col-span-6 sm:col-span-3">
              <label htmlFor="filter-type" className="block text-sm font-medium text-gray-700">
                Filter Type
              </label>
              <select
                id="filter-type"
                name="filter-type"
                value={currentOperation.type || ''}
                onChange={handleTypeChange}
                className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              >
                <option value="">Select filter type</option>
                <option value="gt">Greater Than</option>
                <option value="lt">Less Than</option>
                <option value="ge">Greater Than or Equal</option>
                <option value="le">Less Than or Equal</option>
                <option value="eq">Equal</option>
              </select>
            </div>
            <div className="col-span-6 sm:col-span-3">
              <label htmlFor="filter-value" className="block text-sm font-medium text-gray-700">
                Value
              </label>
              <input
                type="number"
                name="filter-value"
                id="filter-value"
                value={currentOperation.value || ''}
                onChange={handleValueChange}
                className="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
              />
            </div>
          </>
        );
      case 'aggregate':
        return (
          <div className="col-span-6">
            <label htmlFor="aggregation-type" className="block text-sm font-medium text-gray-700">
              Aggregation Type
            </label>
            <select
              id="aggregation-type"
              name="aggregation-type"
              value={currentOperation.type || ''}
              onChange={handleTypeChange}
              className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            >
              <option value="">Select aggregation type</option>
              <option value="sum">Sum</option>
              <option value="avg">Average</option>
              <option value="min">Minimum</option>
              <option value="max">Maximum</option>
            </select>
          </div>
        );
      case 'group_by':
        return (
          <>
            <div className="col-span-6 sm:col-span-3">
              <label htmlFor="time-grouping" className="block text-sm font-medium text-gray-700">
                Time Grouping
              </label>
              <select
                id="time-grouping"
                name="time-grouping"
                value={currentOperation.time_grouping || ''}
                onChange={(e) => setCurrentOperation({ ...currentOperation, time_grouping: e.target.value })}
                className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              >
                <option value="">Select time grouping</option>
                <option value="minute">Minute</option>
                <option value="hour">Hour</option>
                <option value="day">Day</option>
              </select>
            </div>
            <div className="col-span-6 sm:col-span-3">
              <label htmlFor="group-aggregation" className="block text-sm font-medium text-gray-700">
                Aggregation
              </label>
              <select
                id="group-aggregation"
                name="group-aggregation"
                value={currentOperation.aggregation || ''}
                onChange={handleAggregationChange}
                className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              >
                <option value="">Select aggregation</option>
                <option value="sum">Sum</option>
                <option value="avg">Average</option>
                <option value="min">Minimum</option>
                <option value="max">Maximum</option>
              </select>
            </div>
          </>
        );
      case 'group_by_minute':
      case 'group_by_hour':
      case 'group_by_day':
        return (
          <div className="col-span-6">
            <label htmlFor="group-aggregation" className="block text-sm font-medium text-gray-700">
              Aggregation
            </label>
            <select
              id="group-aggregation"
              name="group-aggregation"
              value={currentOperation.aggregation || ''}
              onChange={handleAggregationChange}
              className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            >
              <option value="">Select aggregation (optional)</option>
              <option value="sum">Sum</option>
              <option value="avg">Average</option>
              <option value="min">Minimum</option>
              <option value="max">Maximum</option>
            </select>
          </div>
        );
      default:
        return null;
    }
  };

  // Format operation for display
  const formatOperation = (op: PipelineOperation): string => {
    switch (op.operation) {
      case 'filter':
        return `Filter: ${op.type} ${op.value}`;
      case 'greater_than':
        return `Greater Than: ${op.value}`;
      case 'less_than':
        return `Less Than: ${op.value}`;
      case 'equal_to':
        return `Equal To: ${op.value}`;
      case 'aggregate':
        return `Aggregate: ${op.type}`;
      case 'sum':
        return 'Sum';
      case 'average':
        return 'Average';
      case 'group_by':
        return `Group By: ${op.time_grouping} (${op.aggregation})`;
      case 'group_by_minute':
        return `Group By Minute${op.aggregation ? ` (${op.aggregation})` : ''}`;
      case 'group_by_hour':
        return `Group By Hour${op.aggregation ? ` (${op.aggregation})` : ''}`;
      case 'group_by_day':
        return `Group By Day${op.aggregation ? ` (${op.aggregation})` : ''}`;
      default:
        return 'Unknown operation';
    }
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Transformation Pipeline</h3>
        
        {/* Helper documentation */}
        <div className="mt-2 p-4 bg-blue-50 rounded-md">
          <h4 className="text-sm font-medium text-blue-800">Pipeline Transformation Guide</h4>
          <div className="mt-2 text-xs text-blue-700">
            <p className="mb-2">Build a pipeline by adding operations in sequence. Each operation processes the data from the previous step.</p>
            
            <p className="font-medium mt-1">Available Operations:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li><span className="font-medium">Filter</span> - Filters metrics based on a condition (requires type and value)</li>
              <li><span className="font-medium">Greater Than/Less Than</span> - Shorthand for filter operations (just specify value)</li>
              <li><span className="font-medium">Aggregate</span> - Apply sum, average, min, or max aggregation to values</li>
              <li><span className="font-medium">Group By</span> - Group metrics by time unit and apply aggregation</li>
            </ul>
            
            <p className="font-medium mt-2">Example Pipeline:</p>
            <ol className="list-decimal pl-5 space-y-1">
              <li>Add "Greater Than: 50" to filter values above 50</li>
              <li>Add "Group By Hour (sum)" to sum values by hour</li>
              <li>Click "Apply Transformations" to process the data</li>
            </ol>
          </div>
          <div className="mt-2 text-xs text-blue-700">
            <p className="font-medium">API Format:</p>
            <p>The pipeline is converted to JSON in this format:</p>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto mt-1">
{`[
  {"operation": "greater_than", "value": 50},
  {"operation": "group_by_hour", "aggregation": "sum"}
]`}
            </pre>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-6 gap-6">
          <div className="col-span-6">
            <label htmlFor="operation-type" className="block text-sm font-medium text-gray-700">
              Operation
            </label>
            <select
              id="operation-type"
              name="operation-type"
              value={currentOperation.operation}
              onChange={handleOperationChange}
              className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            >
              <option value="filter">Filter</option>
              <option value="greater_than">Greater Than</option>
              <option value="less_than">Less Than</option>
              <option value="equal_to">Equal To</option>
              <option value="aggregate">Aggregate</option>
              <option value="sum">Sum</option>
              <option value="average">Average</option>
              <option value="group_by">Group By</option>
              <option value="group_by_minute">Group By Minute</option>
              <option value="group_by_hour">Group By Hour</option>
              <option value="group_by_day">Group By Day</option>
            </select>
          </div>

          {renderOperationControls()}

          <div className="col-span-6">
            <button
              type="button"
              onClick={addOperation}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Add to Pipeline
            </button>
          </div>
        </div>

        {/* Display pipeline */}
        {pipeline.length > 0 && (
          <div className="mt-6">
            <h4 className="text-sm font-medium text-gray-900">Current Pipeline</h4>
            <ul className="mt-2 divide-y divide-gray-200 border-t border-b border-gray-200">
              {pipeline.map((op, index) => (
                <li key={index} className="py-3 flex justify-between items-center">
                  <div>
                    <span className="text-sm">{formatOperation(op)}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeOperation(index)}
                    className="ml-4 text-sm font-medium text-red-600 hover:text-red-500"
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
            <div className="mt-4 flex space-x-3">
              <button
                type="button"
                onClick={applyTransformations}
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Apply Transformations
              </button>
              <button
                type="button"
                onClick={clearPipeline}
                className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Clear Pipeline
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}