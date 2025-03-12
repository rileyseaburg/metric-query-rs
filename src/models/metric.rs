use pyo3::prelude::*;

/// A metric is a single data point that is collected at a specific time.
///
/// # Properties
///
/// * `value` - The value of the metric.
/// * `timestamp` - The time at which the metric was collected.
#[pyclass]
#[derive(Debug, Clone)]
pub struct Metric {
    /// The value of the metric.
    #[pyo3(get, set)]
    pub value: i64,
    /// The time at which the metric was collected.
    #[pyo3(get, set)]
    pub timestamp: i64,
    #[pyo3(get, set)]
    pub label: Option<String>, // Add optional label
}

#[pymethods]
impl Metric {
    /// Create a new Metric
    #[new]
    pub fn new(value: i64, timestamp: i64, label: Option<String>) -> Self {
        Self { value, timestamp, label }
    }
}

/// Extended Metric struct (for multiple metric types)
#[pyclass]
#[derive(Debug, Clone)]
pub struct LabeledMetric {
    /// The label of the metric (e.g., "cpu", "memory").
    #[pyo3(get, set)]
    pub label: String,
    /// The value of the metric.
    #[pyo3(get, set)]
    pub value: i64,
    /// The time at which the metric was collected.
    #[pyo3(get, set)]
    pub timestamp: i64,
}

#[pymethods]
impl LabeledMetric {
    /// Create a new LabeledMetric
    #[new]
    pub fn new(label: String, value: i64, timestamp: i64) -> Self {
        Self { label, value, timestamp }
    }
}
