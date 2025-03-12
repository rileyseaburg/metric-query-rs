use pyo3::exceptions::PyValueError;
use pyo3::PyErr;

/// Custom error types for the metric query library
#[derive(Debug)]
pub enum MetricQueryError {
    /// Error when an invalid filter is provided
    InvalidFilter { reason: String },
    /// Error when an invalid aggregation is provided
    InvalidAggregation { reason: String },
    /// Error when an invalid time grouping is provided
    InvalidTimeGrouping { reason: String },
    /// Error when operation is performed on an empty metric stream
    EmptyMetricStream,
    /// Error when a transformation operation fails
    OperationFailed { operation: String, reason: String },
}

impl std::fmt::Display for MetricQueryError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::InvalidFilter { reason } => write!(f, "Invalid filter: {}", reason),
            Self::InvalidAggregation { reason } => write!(f, "Invalid aggregation: {}", reason),
            Self::InvalidTimeGrouping { reason } => write!(f, "Invalid time grouping: {}", reason),
            Self::EmptyMetricStream => write!(f, "Operation on empty metric stream"),
            Self::OperationFailed { operation, reason } => {
                write!(f, "Operation '{}' failed: {}", operation, reason)
            }
        }
    }
}

impl std::error::Error for MetricQueryError {}

impl From<MetricQueryError> for PyErr {
    fn from(err: MetricQueryError) -> PyErr {
        match err {
            MetricQueryError::InvalidFilter { reason } => {
                PyValueError::new_err(format!("Invalid filter: {}", reason))
            }
            MetricQueryError::InvalidAggregation { reason } => {
                PyValueError::new_err(format!("Invalid aggregation: {}", reason))
            }
            MetricQueryError::InvalidTimeGrouping { reason } => {
                PyValueError::new_err(format!("Invalid time grouping: {}", reason))
            }
            MetricQueryError::EmptyMetricStream => {
                PyValueError::new_err("Operation on empty metric stream")
            }
            MetricQueryError::OperationFailed { operation, reason } => {
                PyValueError::new_err(format!("Operation '{}' failed: {}", operation, reason))
            }
        }
    }
}

/// Result type for metric query operations
pub type MetricQueryResult<T> = Result<T, MetricQueryError>;