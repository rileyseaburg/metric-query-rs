pub mod models;
pub mod errors;
pub mod plugins;
pub mod transformations;
pub mod plugin_impls;

// Include tests module only when running tests
#[cfg(test)]
mod tests;

// Import everything we need
use models::metric::{Metric, LabeledMetric};
use plugins::{TransformationRegistry};
use transformations::MetricPipeline;
use plugin_impls::{
    init_registry,
    py_create_filter, py_create_aggregation, py_create_time_grouping
};
use pyo3::prelude::*;

// Legacy filter enum for backward compatibility
#[pyclass]
#[derive(Debug, Clone)]
pub enum Filter {
    GreaterThan { value: i64 },
    LessThan { value: i64 },
    GreaterThanOrEqual { value: i64 },
    LessThanOrEqual { value: i64 },
    Equal { value: i64 },
}

#[pymethods]
impl Filter {
    #[new]
    pub fn new(filter_type: &str, value: i64) -> PyResult<Self> {
        match filter_type {
            "gt" => Ok(Filter::GreaterThan { value }),
            "lt" => Ok(Filter::LessThan { value }),
            "ge" => Ok(Filter::GreaterThanOrEqual { value }),
            "le" => Ok(Filter::LessThanOrEqual { value }),
            "eq" => Ok(Filter::Equal { value }),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid filter type. Expected one of: gt, lt, ge, le, eq",
            )),
        }
    }
}

// Legacy aggregation enum for backward compatibility
#[pyclass]
#[derive(Debug, Clone)]
pub enum Aggregation {
    Sum,
    Avg,
    Min,
    Max,
}

#[pymethods]
impl Aggregation {
    #[new]
    pub fn new(agg_type: &str) -> PyResult<Self> {
        match agg_type {
            "sum" => Ok(Aggregation::Sum),
            "avg" => Ok(Aggregation::Avg),
            "min" => Ok(Aggregation::Min),
            "max" => Ok(Aggregation::Max),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid aggregation type. Expected one of: sum, avg, min, max",
            )),
        }
    }
}

// Legacy time grouping enum for backward compatibility
#[pyclass]
#[derive(Debug, Clone)]
pub enum TimeGrouping {
    Hour,
    Minute,
    Day,
}

#[pymethods]
impl TimeGrouping {
    #[new]
    pub fn new(time_group_type: &str) -> PyResult<Self> {
        match time_group_type {
            "hour" => Ok(TimeGrouping::Hour),
            "minute" => Ok(TimeGrouping::Minute),
            "day" => Ok(TimeGrouping::Day),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid time grouping. Expected one of: hour, minute, day",
            )),
        }
    }
}

// Legacy transformation struct for backward compatibility
#[pyclass]
#[derive(Debug, Clone)]
pub struct Transformation {
    #[pyo3(get, set)]
    pub filter: Option<Filter>,
    #[pyo3(get, set)]
    pub aggregation: Option<Aggregation>,
    #[pyo3(get, set)]
    pub time_grouping: Option<TimeGrouping>,
}

#[pymethods]
impl Transformation {
    #[new]
    pub fn new() -> Self {
        Self {
            filter: None,
            aggregation: None,
            time_grouping: None,
        }
    }
}

/// Convert legacy Filter to a filter type string
fn filter_to_string(filter: &Filter) -> &'static str {
    match filter {
        Filter::GreaterThan { .. } => "gt",
        Filter::LessThan { .. } => "lt",
        Filter::GreaterThanOrEqual { .. } => "ge",
        Filter::LessThanOrEqual { .. } => "le",
        Filter::Equal { .. } => "eq",
    }
}

/// Extract value from legacy Filter
fn filter_to_value(filter: &Filter) -> i64 {
    match filter {
        Filter::GreaterThan { value } => *value,
        Filter::LessThan { value } => *value,
        Filter::GreaterThanOrEqual { value } => *value,
        Filter::LessThanOrEqual { value } => *value,
        Filter::Equal { value } => *value,
    }
}

/// Convert legacy Aggregation to an aggregation type string
fn aggregation_to_string(agg: &Aggregation) -> &'static str {
    match agg {
        Aggregation::Sum => "sum",
        Aggregation::Avg => "avg",
        Aggregation::Min => "min",
        Aggregation::Max => "max",
    }
}

/// Convert legacy TimeGrouping to a time grouping type string
fn time_grouping_to_string(time_grouping: &TimeGrouping) -> &'static str {
    match time_grouping {
        TimeGrouping::Hour => "hour",
        TimeGrouping::Minute => "minute",
        TimeGrouping::Day => "day",
    }
}

/// Helper function to apply transformations using our new architecture
fn apply_transformations(py: Python<'_>, metrics: &[Metric], transformations: &[Transformation]) -> PyResult<Vec<Metric>> {
    // Create a pipeline
    let mut pipeline = MetricPipeline::new(metrics.to_vec());
    
    // Apply each transformation
    for t in transformations {
        // Apply filter if present
        if let Some(filter) = &t.filter {
            let filter_type = filter_to_string(filter);
            let value = filter_to_value(filter);
            pipeline.filter(py, filter_type, value)?;
        }
        
        // Check if we have both aggregation and time grouping
        if let (Some(agg), Some(time_group)) = (&t.aggregation, &t.time_grouping) {
            let agg_type = aggregation_to_string(agg);
            let time_group_type = time_grouping_to_string(time_group);
            pipeline.group_by_time(py, time_group_type, agg_type)?;
        } else if let Some(agg) = &t.aggregation {
            // Only aggregation
            let agg_type = aggregation_to_string(agg);
            pipeline.aggregate(py, agg_type)?;
        }
    }
    
    // Execute the pipeline
    pipeline.execute()
}

/// Transforms a slice of Metrics according to a series of Transformations.
/// This function is intended to be exposed to other languages via FFI.
///
/// # Arguments
///
/// * `metrics` - A slice of `Metric` objects.
/// * `transformations` - A slice of `Transformation` structs, defining the transformations to be applied.
///
/// # Returns
///
/// A `Vec<Metric>` containing the transformed metrics.
#[pyfunction]
pub fn transform(py: Python<'_>, metrics: Vec<Metric>, transformations: Vec<Transformation>) -> PyResult<Vec<Metric>> {
    apply_transformations(py, &metrics, &transformations)
}

/// Creates a new metric pipeline with the given metrics.
/// This is part of the new fluent API.
#[pyfunction]
pub fn create_pipeline(metrics: Vec<Metric>) -> MetricPipeline {
    MetricPipeline::new(metrics)
}

/// Initializes and returns the transformation registry with built-in plugins
#[pyfunction]
pub fn get_registry(py: Python<'_>) -> PyResult<TransformationRegistry> {
    let mut registry = TransformationRegistry::new(py)?;
    registry.refresh(py)?;
    Ok(registry)
}

// Use the correct PyO3 module signature for newer versions
#[pymodule]
fn metric_query_library(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Initialize plugin registry
    init_registry();
    
    // Register legacy functions and types for backward compatibility
    m.add_function(wrap_pyfunction!(transform, m)?)?;
    m.add_class::<Metric>()?;
    m.add_class::<LabeledMetric>()?;
    m.add_class::<Filter>()?;
    m.add_class::<Aggregation>()?;
    m.add_class::<TimeGrouping>()?;
    m.add_class::<Transformation>()?;
    
    // Register new fluent API components
    m.add_function(wrap_pyfunction!(create_pipeline, m)?)?;
    m.add_function(wrap_pyfunction!(get_registry, m)?)?;
    m.add_class::<MetricPipeline>()?;
    m.add_class::<TransformationRegistry>()?;
    
    // Register helper functions for plugin creation
    m.add_function(wrap_pyfunction!(py_create_filter, m)?)?;
    m.add_function(wrap_pyfunction!(py_create_aggregation, m)?)?;
    m.add_function(wrap_pyfunction!(py_create_time_grouping, m)?)?;
    
    Ok(())
}
