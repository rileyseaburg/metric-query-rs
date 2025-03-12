use pyo3::prelude::*;
use crate::errors::MetricQueryResult;
use crate::models::Metric;
use std::collections::HashMap;

/// Trait for filter plugins
pub trait FilterPlugin: Send + Sync {
    /// Get the name of the filter plugin
    fn name(&self) -> &str;
    
    /// Apply the filter to a metric
    fn apply(&self, metric: &Metric) -> bool; // Update parameter type
    
    /// Clone the plugin (required for trait objects)
    fn clone_box(&self) -> Box<dyn FilterPlugin>;
}

// Enable cloning of BoxedFilterPlugin
impl Clone for Box<dyn FilterPlugin> {
    fn clone(&self) -> Self {
        self.clone_box()
    }
}

/// Trait for aggregation plugins
pub trait AggregationPlugin: Send + Sync {
    /// Get the name of the aggregation plugin
    fn name(&self) -> &str;
    
    /// Apply the aggregation to a collection of metrics
    fn apply(&self, metrics: &[Metric]) -> MetricQueryResult<i64>;
    
    /// Clone the plugin (required for trait objects)
    fn clone_box(&self) -> Box<dyn AggregationPlugin>;
}

// Enable cloning of BoxedAggregationPlugin
impl Clone for Box<dyn AggregationPlugin> {
    fn clone(&self) -> Self {
        self.clone_box()
    }
}

/// Trait for time grouping plugins
pub trait TimeGroupingPlugin: Send + Sync {
    /// Get the name of the time grouping plugin
    fn name(&self) -> &str;
    
    /// Get the timestamp for the group that a metric belongs to
    fn get_group_timestamp(&self, timestamp: i64) -> MetricQueryResult<i64>;
    
    /// Clone the plugin (required for trait objects)
    fn clone_box(&self) -> Box<dyn TimeGroupingPlugin>;
}

// Enable cloning of BoxedTimeGroupingPlugin
impl Clone for Box<dyn TimeGroupingPlugin> {
    fn clone(&self) -> Self {
        self.clone_box()
    }
}

// Python-friendly wrappers for the plugin registry
#[pyclass]
#[derive(Clone)]
pub struct PyFilterPluginRef {
    #[pyo3(get)]
    pub name: String,
}

#[pyclass]
#[derive(Clone)]
pub struct PyAggregationPluginRef {
    #[pyo3(get)]
    pub name: String,
}

#[pyclass]
#[derive(Clone)]
pub struct PyTimeGroupingPluginRef {
    #[pyo3(get)]
    pub name: String,
}

// Global registry
// We're using thread-local storage to maintain a reference to the registry
thread_local! {
    static GLOBAL_REGISTRY: std::cell::RefCell<PluginRegistry> = std::cell::RefCell::new(PluginRegistry::new());
}

// Registry for transformation plugins
#[derive(Default)]
pub struct PluginRegistry {
    filters: HashMap<String, Box<dyn FilterPlugin>>,
    aggregations: HashMap<String, Box<dyn AggregationPlugin>>,
    time_groupings: HashMap<String, Box<dyn TimeGroupingPlugin>>,
}

impl PluginRegistry {
    /// Create a new empty registry
    pub fn new() -> Self {
        Self {
            filters: HashMap::new(),
            aggregations: HashMap::new(),
            time_groupings: HashMap::new(),
        }
    }
    
    /// Register a new filter plugin
    pub fn register_filter(&mut self, filter: Box<dyn FilterPlugin>) {
        self.filters.insert(filter.name().to_string(), filter);
    }
    
    /// Register a new aggregation plugin
    pub fn register_aggregation(&mut self, aggregation: Box<dyn AggregationPlugin>) {
        self.aggregations.insert(aggregation.name().to_string(), aggregation);
    }
    
    /// Register a new time grouping plugin
    pub fn register_time_grouping(&mut self, time_grouping: Box<dyn TimeGroupingPlugin>) {
        self.time_groupings.insert(time_grouping.name().to_string(), time_grouping);
    }
    
    /// Get a filter plugin by name
    pub fn get_filter(&self, name: &str) -> Option<&Box<dyn FilterPlugin>> {
        self.filters.get(name)
    }
    
    /// Get an aggregation plugin by name
    pub fn get_aggregation(&self, name: &str) -> Option<&Box<dyn AggregationPlugin>> {
        self.aggregations.get(name)
    }
    
    /// Get a time grouping plugin by name
    pub fn get_time_grouping(&self, name: &str) -> Option<&Box<dyn TimeGroupingPlugin>> {
        self.time_groupings.get(name)
    }
    
    /// Get list of available filter names
    pub fn get_filter_names(&self) -> Vec<String> {
        self.filters.keys().cloned().collect()
    }
    
    /// Get list of available aggregation names
    pub fn get_aggregation_names(&self) -> Vec<String> {
        self.aggregations.keys().cloned().collect()
    }
    
    /// Get list of available time grouping names
    pub fn get_time_grouping_names(&self) -> Vec<String> {
        self.time_groupings.keys().cloned().collect()
    }
    
    /// Get Python-friendly references to all filters
    pub fn get_py_filters(&self) -> Vec<PyFilterPluginRef> {
        self.filters.keys().map(|name| PyFilterPluginRef { name: name.clone() }).collect()
    }
    
    /// Get Python-friendly references to all aggregations
    pub fn get_py_aggregations(&self) -> Vec<PyAggregationPluginRef> {
        self.aggregations.keys().map(|name| PyAggregationPluginRef { name: name.clone() }).collect()
    }
    
    /// Get Python-friendly references to all time groupings
    pub fn get_py_time_groupings(&self) -> Vec<PyTimeGroupingPluginRef> {
        self.time_groupings.keys().map(|name| PyTimeGroupingPluginRef { name: name.clone() }).collect()
    }
}

/// Helper function to access the global registry
pub fn with_registry<F, R>(f: F) -> R
where
    F: FnOnce(&PluginRegistry) -> R,
{
    GLOBAL_REGISTRY.with(|registry| {
        let registry = registry.borrow();
        f(&registry)
    })
}

/// Helper function to mutate the global registry
pub fn with_registry_mut<F, R>(f: F) -> R
where
    F: FnOnce(&mut PluginRegistry) -> R,
{
    GLOBAL_REGISTRY.with(|registry| {
        let mut registry = registry.borrow_mut();
        f(&mut registry)
    })
}

/// Python wrapper for the plugin registry
#[pyclass]
pub struct TransformationRegistry {
    #[pyo3(get)]
    pub filters: Vec<PyFilterPluginRef>,
    #[pyo3(get)]
    pub aggregations: Vec<PyAggregationPluginRef>,
    #[pyo3(get)]
    pub time_groupings: Vec<PyTimeGroupingPluginRef>,
}

#[pymethods]
impl TransformationRegistry {
    #[new]
    pub fn new(_py: Python) -> PyResult<Self> {
        Ok(Self {
            filters: Vec::new(),
            aggregations: Vec::new(),
            time_groupings: Vec::new(),
        })
    }
    
    /// Update the references to match the current plugins
    pub fn refresh(&mut self, _py: Python) -> PyResult<()> {
        with_registry(|registry| {
            self.filters = registry.get_py_filters();
            self.aggregations = registry.get_py_aggregations();
            self.time_groupings = registry.get_py_time_groupings();
        });
        
        Ok(())
    }
    
    /// Check if a filter exists
    pub fn has_filter(&self, name: &str) -> bool {
        self.filters.iter().any(|f| f.name == name)
    }
    
    /// Check if an aggregation exists
    pub fn has_aggregation(&self, name: &str) -> bool {
        self.aggregations.iter().any(|a| a.name == name)
    }
    
    /// Check if a time grouping exists
    pub fn has_time_grouping(&self, name: &str) -> bool {
        self.time_groupings.iter().any(|t| t.name == name)
    }
}