use pyo3::prelude::*;
use chrono::{DateTime, Timelike, Utc};

use crate::errors::{MetricQueryError, MetricQueryResult};
use crate::models::Metric;
use crate::plugins::{
    FilterPlugin, AggregationPlugin, TimeGroupingPlugin, 
    with_registry_mut
};

// ----- Filter Plugin Implementations -----

/// Greater than filter
#[derive(Clone)]
pub struct GreaterThanFilter {
    value: i64,
}

impl GreaterThanFilter {
    pub fn new(value: i64) -> Self {
        Self { value }
    }
}

impl FilterPlugin for GreaterThanFilter {
    fn name(&self) -> &str {
        "gt"
    }
    
    fn apply(&self, metric: &Metric) -> bool {
        metric.value > self.value
    }
    
    fn clone_box(&self) -> Box<dyn FilterPlugin> {
        Box::new(self.clone())
    }
}

/// Less than filter
#[derive(Clone)]
pub struct LessThanFilter {
    value: i64,
}

impl LessThanFilter {
    pub fn new(value: i64) -> Self {
        Self { value }
    }
}

impl FilterPlugin for LessThanFilter {
    fn name(&self) -> &str {
        "lt"
    }
    
    fn apply(&self, metric: &Metric) -> bool {
        metric.value < self.value
    }
    
    fn clone_box(&self) -> Box<dyn FilterPlugin> {
        Box::new(self.clone())
    }
}

/// Greater than or equal filter
#[derive(Clone)]
pub struct GreaterThanOrEqualFilter {
    value: i64,
}

impl GreaterThanOrEqualFilter {
    pub fn new(value: i64) -> Self {
        Self { value }
    }
}

impl FilterPlugin for GreaterThanOrEqualFilter {
    fn name(&self) -> &str {
        "ge"
    }
    
    fn apply(&self, metric: &Metric) -> bool {
        metric.value >= self.value
    }
    
    fn clone_box(&self) -> Box<dyn FilterPlugin> {
        Box::new(self.clone())
    }
}

/// Less than or equal filter
#[derive(Clone)]
pub struct LessThanOrEqualFilter {
    value: i64,
}

impl LessThanOrEqualFilter {
    pub fn new(value: i64) -> Self {
        Self { value }
    }
}

impl FilterPlugin for LessThanOrEqualFilter {
    fn name(&self) -> &str {
        "le"
    }
    
    fn apply(&self, metric: &Metric) -> bool {
        metric.value <= self.value
    }
    
    fn clone_box(&self) -> Box<dyn FilterPlugin> {
        Box::new(self.clone())
    }
}

/// Equal filter
#[derive(Clone)]
pub struct EqualFilter {
    value: i64,
}

impl EqualFilter {
    pub fn new(value: i64) -> Self {
        Self { value }
    }
}

impl FilterPlugin for EqualFilter {
    fn name(&self) -> &str {
        "eq"
    }
    
    fn apply(&self, metric: &Metric) -> bool {
        metric.value == self.value
    }
    
    fn clone_box(&self) -> Box<dyn FilterPlugin> {
        Box::new(self.clone())
    }
}

// ----- Aggregation Plugin Implementations -----

/// Sum aggregation
#[derive(Clone)]
pub struct SumAggregation;

impl AggregationPlugin for SumAggregation {
    fn name(&self) -> &str {
        "sum"
    }
    
    fn apply(&self, metrics: &[Metric]) -> MetricQueryResult<i64> {
        if metrics.is_empty() {
            return Err(MetricQueryError::EmptyMetricStream);
        }
        
        Ok(metrics.iter().map(|m| m.value).sum())
    }
    
    fn clone_box(&self) -> Box<dyn AggregationPlugin> {
        Box::new(self.clone())
    }
}

/// Average aggregation
#[derive(Clone)]
pub struct AvgAggregation;

impl AggregationPlugin for AvgAggregation {
    fn name(&self) -> &str {
        "avg"
    }
    
    fn apply(&self, metrics: &[Metric]) -> MetricQueryResult<i64> {
        if metrics.is_empty() {
            return Err(MetricQueryError::EmptyMetricStream);
        }
        
        let sum: i64 = metrics.iter().map(|m| m.value).sum();
        Ok(sum / metrics.len() as i64)
    }
    
    fn clone_box(&self) -> Box<dyn AggregationPlugin> {
        Box::new(self.clone())
    }
}

/// Minimum aggregation
#[derive(Clone)]
pub struct MinAggregation;

impl AggregationPlugin for MinAggregation {
    fn name(&self) -> &str {
        "min"
    }
    
    fn apply(&self, metrics: &[Metric]) -> MetricQueryResult<i64> {
        metrics.iter().map(|m| m.value).min().ok_or(MetricQueryError::EmptyMetricStream)
    }
    
    fn clone_box(&self) -> Box<dyn AggregationPlugin> {
        Box::new(self.clone())
    }
}

/// Maximum aggregation
#[derive(Clone)]
pub struct MaxAggregation;

impl AggregationPlugin for MaxAggregation {
    fn name(&self) -> &str {
        "max"
    }
    
    fn apply(&self, metrics: &[Metric]) -> MetricQueryResult<i64> {
        metrics.iter().map(|m| m.value).max().ok_or(MetricQueryError::EmptyMetricStream)
    }
    
    fn clone_box(&self) -> Box<dyn AggregationPlugin> {
        Box::new(self.clone())
    }
}

// ----- Time Grouping Plugin Implementations -----

/// Hour time grouping
#[derive(Clone)]
pub struct HourGrouping;

impl TimeGroupingPlugin for HourGrouping {
    fn name(&self) -> &str {
        "hour"
    }
    
    fn get_group_timestamp(&self, timestamp: i64) -> MetricQueryResult<i64> {
        let dt = DateTime::<Utc>::from_timestamp(timestamp, 0)
            .ok_or_else(|| MetricQueryError::InvalidTimeGrouping {
                reason: format!("Invalid timestamp: {}", timestamp),
            })?;
        
        let grouped_dt = dt
            .with_minute(0)
            .and_then(|dt| dt.with_second(0))
            .ok_or_else(|| MetricQueryError::OperationFailed {
                operation: "hour grouping".to_string(),
                reason: "Failed to set minute/second to 0".to_string(),
            })?;
        
        Ok(grouped_dt.timestamp())
    }
    
    fn clone_box(&self) -> Box<dyn TimeGroupingPlugin> {
        Box::new(self.clone())
    }
}

/// Minute time grouping
#[derive(Clone)]
pub struct MinuteGrouping;

impl TimeGroupingPlugin for MinuteGrouping {
    fn name(&self) -> &str {
        "minute"
    }
    
    fn get_group_timestamp(&self, timestamp: i64) -> MetricQueryResult<i64> {
        let dt = DateTime::<Utc>::from_timestamp(timestamp, 0)
            .ok_or_else(|| MetricQueryError::InvalidTimeGrouping {
                reason: format!("Invalid timestamp: {}", timestamp),
            })?;
        
        let grouped_dt = dt
            .with_second(0)
            .ok_or_else(|| MetricQueryError::OperationFailed {
                operation: "minute grouping".to_string(),
                reason: "Failed to set second to 0".to_string(),
            })?;
        
        Ok(grouped_dt.timestamp())
    }
    
    fn clone_box(&self) -> Box<dyn TimeGroupingPlugin> {
        Box::new(self.clone())
    }
}

/// Day time grouping
#[derive(Clone)]
pub struct DayGrouping;

impl TimeGroupingPlugin for DayGrouping {
    fn name(&self) -> &str {
        "day"
    }
    
    fn get_group_timestamp(&self, timestamp: i64) -> MetricQueryResult<i64> {
        let dt = DateTime::<Utc>::from_timestamp(timestamp, 0)
            .ok_or_else(|| MetricQueryError::InvalidTimeGrouping {
                reason: format!("Invalid timestamp: {}", timestamp),
            })?;
        
        let grouped_dt = dt
            .with_hour(0)
            .and_then(|dt| dt.with_minute(0))
            .and_then(|dt| dt.with_second(0))
            .ok_or_else(|| MetricQueryError::OperationFailed {
                operation: "day grouping".to_string(),
                reason: "Failed to set hour/minute/second to 0".to_string(),
            })?;
        
        Ok(grouped_dt.timestamp())
    }
    
    fn clone_box(&self) -> Box<dyn TimeGroupingPlugin> {
        Box::new(self.clone())
    }
}

// ----- Factory Functions -----

/// Create a filter from type and value
pub fn create_filter(filter_type: &str, value: i64) -> MetricQueryResult<Box<dyn FilterPlugin>> {
    match filter_type {
        "gt" => Ok(Box::new(GreaterThanFilter::new(value))),
        "lt" => Ok(Box::new(LessThanFilter::new(value))),
        "ge" => Ok(Box::new(GreaterThanOrEqualFilter::new(value))),
        "le" => Ok(Box::new(LessThanOrEqualFilter::new(value))),
        "eq" => Ok(Box::new(EqualFilter::new(value))),
        _ => Err(MetricQueryError::InvalidFilter {
            reason: format!("Unknown filter type: {}", filter_type),
        }),
    }
}

/// Create an aggregation from type
pub fn create_aggregation(agg_type: &str) -> MetricQueryResult<Box<dyn AggregationPlugin>> {
    match agg_type {
        "sum" => Ok(Box::new(SumAggregation)),
        "avg" => Ok(Box::new(AvgAggregation)),
        "min" => Ok(Box::new(MinAggregation)),
        "max" => Ok(Box::new(MaxAggregation)),
        _ => Err(MetricQueryError::InvalidAggregation {
            reason: format!("Unknown aggregation type: {}", agg_type),
        }),
    }
}

/// Create a time grouping from type
pub fn create_time_grouping(grouping_type: &str) -> MetricQueryResult<Box<dyn TimeGroupingPlugin>> {
    match grouping_type {
        "hour" => Ok(Box::new(HourGrouping)),
        "minute" => Ok(Box::new(MinuteGrouping)),
        "day" => Ok(Box::new(DayGrouping)),
        _ => Err(MetricQueryError::InvalidTimeGrouping {
            reason: format!("Unknown time grouping type: {}", grouping_type),
        }),
    }
}

/// Initialize the global plugin registry with built-in plugins
pub fn init_registry() {
    with_registry_mut(|registry| {
        // Register filters
        registry.register_filter(Box::new(GreaterThanFilter::new(0)));
        registry.register_filter(Box::new(LessThanFilter::new(0)));
        registry.register_filter(Box::new(GreaterThanOrEqualFilter::new(0)));
        registry.register_filter(Box::new(LessThanOrEqualFilter::new(0)));
        registry.register_filter(Box::new(EqualFilter::new(0)));
        
        // Register aggregations
        registry.register_aggregation(Box::new(SumAggregation));
        registry.register_aggregation(Box::new(AvgAggregation));
        registry.register_aggregation(Box::new(MinAggregation));
        registry.register_aggregation(Box::new(MaxAggregation));
        
        // Register time groupings
        registry.register_time_grouping(Box::new(HourGrouping));
        registry.register_time_grouping(Box::new(MinuteGrouping));
        registry.register_time_grouping(Box::new(DayGrouping));
    });
}

// Python wrapper functions for creating plugins
#[pyfunction]
pub fn py_create_filter(filter_type: &str, value: i64) -> PyResult<String> {
    match create_filter(filter_type, value) {
        Ok(filter) => Ok(filter.name().to_string()),
        Err(e) => Err(pyo3::exceptions::PyValueError::new_err(format!("{:?}", e))),
    }
}

#[pyfunction]
pub fn py_create_aggregation(agg_type: &str) -> PyResult<String> {
    match create_aggregation(agg_type) {
        Ok(agg) => Ok(agg.name().to_string()),
        Err(e) => Err(pyo3::exceptions::PyValueError::new_err(format!("{:?}", e))),
    }
}

#[pyfunction]
pub fn py_create_time_grouping(grouping_type: &str) -> PyResult<String> {
    match create_time_grouping(grouping_type) {
        Ok(group) => Ok(group.name().to_string()),
        Err(e) => Err(pyo3::exceptions::PyValueError::new_err(format!("{:?}", e))),
    }
}