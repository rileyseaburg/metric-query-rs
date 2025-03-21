use pyo3::prelude::*;
use std::collections::HashMap;

use crate::errors::{MetricQueryError, MetricQueryResult};
use crate::models::Metric;
use crate::plugins::{
    FilterPlugin, AggregationPlugin, TimeGroupingPlugin,
    with_registry
};
use crate::plugin_impls::{LabelFilter, LabelInFilter};

/// Trait for transformation strategies
pub trait TransformationStrategy: Send + Sync {
    /// Apply the transformation to a collection of metrics
    fn apply(&self, metrics: &[Metric]) -> MetricQueryResult<Vec<Metric>>;
}

/// Filter transformation strategy
pub struct FilterTransformation {
    filter: Box<dyn FilterPlugin>,
}

impl FilterTransformation {
    /// Create a new filter transformation
    pub fn new(filter: Box<dyn FilterPlugin>) -> Self {
        Self { filter }
    }
}

impl TransformationStrategy for FilterTransformation {
    fn apply(&self, metrics: &[Metric]) -> MetricQueryResult<Vec<Metric>> {
        // Pre-allocate with an estimated capacity to avoid multiple reallocations
        // For filters, we'll estimate half the metrics might pass (a reasonable heuristic)
        let estimated_capacity = metrics.len() / 2;
        let mut result = Vec::with_capacity(estimated_capacity);
        
        // Only clone metrics that pass the filter
        for metric in metrics {
            if self.filter.apply(metric) {
                result.push(metric.clone());
            }
        }
        
        Ok(result)
    }
}

/// Aggregation transformation strategy
pub struct AggregationTransformation {
    aggregation: Box<dyn AggregationPlugin>,
}

impl AggregationTransformation {
    /// Create a new aggregation transformation
    pub fn new(aggregation: Box<dyn AggregationPlugin>) -> Self {
        Self { aggregation }
    }
}

impl TransformationStrategy for AggregationTransformation {
    fn apply(&self, metrics: &[Metric]) -> MetricQueryResult<Vec<Metric>> {
        if metrics.is_empty() {
            return Err(MetricQueryError::EmptyMetricStream);
        }
        
        // Use the first timestamp as a representative timestamp
        let timestamp = metrics[0].timestamp;
        
        // Apply the aggregation to get a single value
        let value = self.aggregation.apply(metrics)?;
        
        // Use with_capacity for optimal memory allocation
        let mut result = Vec::with_capacity(1);
        // Preserve label if present in first metric
        let label = metrics[0].label.clone();
        result.push(Metric { value, timestamp, label });
        
        Ok(result)
    }
}

/// Time grouping transformation strategy
pub struct TimeGroupingTransformation {
    time_grouping: Box<dyn TimeGroupingPlugin>,
    aggregation: Box<dyn AggregationPlugin>,
}

impl TimeGroupingTransformation {
    /// Create a new time grouping transformation with an aggregation
    pub fn new(time_grouping: Box<dyn TimeGroupingPlugin>, aggregation: Box<dyn AggregationPlugin>) -> Self {
        Self { time_grouping, aggregation }
    }
}

impl TransformationStrategy for TimeGroupingTransformation {
    fn apply(&self, metrics: &[Metric]) -> MetricQueryResult<Vec<Metric>> {
        if metrics.is_empty() {
            return Err(MetricQueryError::EmptyMetricStream);
        }
        
        // Performance optimization: Instead of cloning each metric into groups,
        // just collect their values by timestamp groups
        let mut group_values: HashMap<i64, Vec<i64>> = HashMap::new();
        
        for metric in metrics {
            // Get the group timestamp for this metric
            let group_timestamp = self.time_grouping.get_group_timestamp(metric.timestamp)?;
            
            // Store just the value in the appropriate group (avoids cloning the entire Metric)
            group_values
                .entry(group_timestamp)
                .or_insert_with(Vec::new)
                .push(metric.value);
        }
        
        // Apply aggregation to each group
        let mut result = Vec::with_capacity(group_values.len());
        
        for (timestamp, values) in group_values {
            // Create temporary metrics for the aggregation
            let group_metrics: Vec<Metric> = values
                .into_iter()
                .map(|value| Metric { value, timestamp: 0, label: None }) // Timestamp doesn't matter for aggregation
                .collect();
            
            let value = self.aggregation.apply(&group_metrics)?;
            // For grouped metrics, we don't have a meaningful label to preserve
            result.push(Metric { value, timestamp, label: None });
        }
        
        Ok(result)
    }
}

/// Pipeline for chaining transformations
#[pyclass]
pub struct MetricPipeline {
    #[pyo3(get)]
    metrics: Vec<Metric>,
    // We'll use an internal Vec for strategies
    strategies: Vec<Box<dyn TransformationStrategy>>,
}

#[pymethods]
impl MetricPipeline {
    /// Create a new pipeline with the given metrics
    #[new]
    pub fn new(metrics: Vec<Metric>) -> Self {
        // Estimate initial capacity for strategies
        // Most pipelines have 2-5 transformations, so 5 is a reasonable starting point
        Self {
            metrics,
            strategies: Vec::with_capacity(5),
        }
    }
    
    /// Add a filter transformation to the pipeline
    pub fn filter(&mut self, _py: Python<'_>, filter_type: &str, _filter_value: i64) -> PyResult<()> {
        with_registry(|registry| {
            // Find the filter
            if let Some(filter) = registry.get_filter(filter_type) {
                self.strategies.push(Box::new(FilterTransformation::new(filter.clone())));
                Ok(())
            } else {
                Err(pyo3::exceptions::PyValueError::new_err(
                    format!("Unknown filter type: {}", filter_type)
                ))
            }
        })
    }
    
    /// Add an aggregation transformation to the pipeline
    pub fn aggregate(&mut self, _py: Python<'_>, agg_type: &str) -> PyResult<()> {
        with_registry(|registry| {
            // Find the aggregation
            if let Some(aggregation) = registry.get_aggregation(agg_type) {
                self.strategies.push(Box::new(AggregationTransformation::new(aggregation.clone())));
                Ok(())
            } else {
                Err(pyo3::exceptions::PyValueError::new_err(
                    format!("Unknown aggregation type: {}", agg_type)
                ))
            }
        })
    }
    
    /// Add a time grouping transformation with an aggregation to the pipeline
    pub fn group_by_time(
        &mut self,
        _py: Python<'_>,
        time_grouping_type: &str,
        agg_type: &str,
    ) -> PyResult<()> {
        with_registry(|registry| {
            // Find the time grouping and aggregation
            let time_grouping = registry.get_time_grouping(time_grouping_type)
                .ok_or_else(|| pyo3::exceptions::PyValueError::new_err(
                    format!("Unknown time grouping type: {}", time_grouping_type)
                ))?;
            
            let aggregation = registry.get_aggregation(agg_type)
                .ok_or_else(|| pyo3::exceptions::PyValueError::new_err(
                    format!("Unknown aggregation type: {}", agg_type)
                ))?;
            
            self.strategies.push(Box::new(TimeGroupingTransformation::new(
                time_grouping.clone(),
                aggregation.clone(),
            )));
            
            Ok(())
        })
    }
    
    /// Add a label filter transformation to the pipeline
    pub fn filter_by_label(&mut self, _py: Python<'_>, filter_type: &str, label: String) -> PyResult<()> {
        if filter_type == "label_eq" {
            // Create a new label filter directly
            let filter_box: Box<dyn FilterPlugin> = Box::new(LabelFilter::new(label));
            self.strategies.push(Box::new(FilterTransformation::new(filter_box)));
            Ok(())
        } else {
            Err(pyo3::exceptions::PyValueError::new_err(
                format!("Invalid label filter type: {}. Expected 'label_eq'", filter_type)
            ))
        }
    }
    
    /// Add a label inclusion filter transformation to the pipeline
    pub fn filter_by_labels(&mut self, _py: Python<'_>, filter_type: &str, labels: Vec<String>) -> PyResult<()> {
        if filter_type == "label_in" {
            // Create a new label_in filter directly
            let filter_box: Box<dyn FilterPlugin> = Box::new(LabelInFilter::new(labels));
            self.strategies.push(Box::new(FilterTransformation::new(filter_box)));
            Ok(())
        } else {
            Err(pyo3::exceptions::PyValueError::new_err(
                format!("Invalid label filter type: {}. Expected 'label_in'", filter_type)
            ))
        }
    }
    
    /// Execute the pipeline and return the result
    pub fn execute(&self) -> PyResult<Vec<Metric>> {
        // Only clone the metrics once at the end if no transformations are applied
        // This avoids unnecessary cloning during intermediate steps
        if self.strategies.is_empty() {
            return Ok(self.metrics.clone());
        }
        
        // Apply the first transformation directly on the original metrics
        let mut result = match self.strategies[0].apply(&self.metrics) {
            Ok(transformed) => transformed,
            Err(e) => return Err(pyo3::exceptions::PyValueError::new_err(
                format!("Error executing transformation: {:?}", e)
            )),
        };
        
        // Apply remaining transformations sequentially
        for strategy in &self.strategies[1..] {
            result = match strategy.apply(&result) {
                Ok(transformed) => transformed,
                Err(e) => return Err(pyo3::exceptions::PyValueError::new_err(
                    format!("Error executing transformation: {:?}", e)
                )),
            };
        }
        
        Ok(result)
    }
}