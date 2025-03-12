use crate::errors::MetricQueryResult;
use crate::models::Metric;
use crate::plugin_impls::{
    create_aggregation, create_filter, create_time_grouping,
    AvgAggregation, DayGrouping, EqualFilter, GreaterThanFilter, HourGrouping, MaxAggregation,
    MinAggregation, MinuteGrouping, SumAggregation,
};
use crate::plugins::{AggregationPlugin, FilterPlugin, TimeGroupingPlugin};
use crate::transformations::{
    AggregationTransformation, FilterTransformation, MetricPipeline, TimeGroupingTransformation,
    TransformationStrategy,
};
use chrono::{DateTime, NaiveDateTime, TimeZone, Utc};

#[cfg(test)]
mod test_filters {
    use super::*;

    fn create_test_metrics() -> Vec<Metric> {
        vec![
            Metric::new(10, 1000),
            Metric::new(20, 2000),
            Metric::new(30, 3000),
            Metric::new(15, 4000),
            Metric::new(25, 5000),
        ]
    }

    #[test]
    fn test_greater_than_filter() {
        let metrics = create_test_metrics();
        let filter = GreaterThanFilter::new(20);
        let transformer = FilterTransformation::new(Box::new(filter));
        
        let result = transformer.apply(&metrics).unwrap();
        
        assert_eq!(result.len(), 2);
        assert_eq!(result[0].value, 30);
        assert_eq!(result[1].value, 25);
    }

    #[test]
    fn test_equal_filter() {
        let metrics = create_test_metrics();
        let filter = EqualFilter::new(20);
        let transformer = FilterTransformation::new(Box::new(filter));
        
        let result = transformer.apply(&metrics).unwrap();
        
        assert_eq!(result.len(), 1);
        assert_eq!(result[0].value, 20);
    }

    #[test]
    fn test_filter_factory() {
        let metrics = create_test_metrics();
        
        // Test gt filter
        let gt_filter = create_filter("gt", 15).unwrap();
        let gt_transformer = FilterTransformation::new(gt_filter);
        let gt_result = gt_transformer.apply(&metrics).unwrap();
        assert_eq!(gt_result.len(), 3);
        
        // Test lt filter
        let lt_filter = create_filter("lt", 20).unwrap();
        let lt_transformer = FilterTransformation::new(lt_filter);
        let lt_result = lt_transformer.apply(&metrics).unwrap();
        assert_eq!(lt_result.len(), 2);
        
        // Test eq filter
        let eq_filter = create_filter("eq", 15).unwrap();
        let eq_transformer = FilterTransformation::new(eq_filter);
        let eq_result = eq_transformer.apply(&metrics).unwrap();
        assert_eq!(eq_result.len(), 1);
    }
}

#[cfg(test)]
mod test_aggregations {
    use super::*;
    
    fn create_test_metrics() -> Vec<Metric> {
        vec![
            Metric::new(10, 1000),
            Metric::new(20, 2000),
            Metric::new(30, 3000),
            Metric::new(40, 4000),
        ]
    }
    
    #[test]
    fn test_sum_aggregation() {
        let metrics = create_test_metrics();
        let aggregation = SumAggregation;
        let transformer = AggregationTransformation::new(Box::new(aggregation));
        
        let result = transformer.apply(&metrics).unwrap();
        
        assert_eq!(result.len(), 1);
        assert_eq!(result[0].value, 100); // 10 + 20 + 30 + 40 = 100
    }
    
    #[test]
    fn test_avg_aggregation() {
        let metrics = create_test_metrics();
        let aggregation = AvgAggregation;
        let transformer = AggregationTransformation::new(Box::new(aggregation));
        
        let result = transformer.apply(&metrics).unwrap();
        
        assert_eq!(result.len(), 1);
        assert_eq!(result[0].value, 25); // (10 + 20 + 30 + 40) / 4 = 25
    }
    
    #[test]
    fn test_min_aggregation() {
        let metrics = create_test_metrics();
        let aggregation = MinAggregation;
        let transformer = AggregationTransformation::new(Box::new(aggregation));
        
        let result = transformer.apply(&metrics).unwrap();
        
        assert_eq!(result.len(), 1);
        assert_eq!(result[0].value, 10);
    }
    
    #[test]
    fn test_max_aggregation() {
        let metrics = create_test_metrics();
        let aggregation = MaxAggregation;
        let transformer = AggregationTransformation::new(Box::new(aggregation));
        
        let result = transformer.apply(&metrics).unwrap();
        
        assert_eq!(result.len(), 1);
        assert_eq!(result[0].value, 40);
    }
    
    #[test]
    fn test_aggregation_factory() {
        let metrics = create_test_metrics();
        
        // Test sum aggregation
        let sum_agg = create_aggregation("sum").unwrap();
        let sum_transformer = AggregationTransformation::new(sum_agg);
        let sum_result = sum_transformer.apply(&metrics).unwrap();
        assert_eq!(sum_result[0].value, 100);
        
        // Test avg aggregation
        let avg_agg = create_aggregation("avg").unwrap();
        let avg_transformer = AggregationTransformation::new(avg_agg);
        let avg_result = avg_transformer.apply(&metrics).unwrap();
        assert_eq!(avg_result[0].value, 25);
    }
}

#[cfg(test)]
mod test_time_groupings {
    use super::*;
    
    fn timestamp(year: i32, month: u32, day: u32, hour: u32, min: u32, sec: u32) -> i64 {
        Utc.with_ymd_and_hms(year, month, day, hour, min, sec)
            .unwrap()
            .timestamp()
    }
    
    fn create_test_metrics() -> Vec<Metric> {
        vec![
            // 2023-01-01 10:15:30
            Metric::new(10, timestamp(2023, 1, 1, 10, 15, 30)),
            // 2023-01-01 10:30:45
            Metric::new(20, timestamp(2023, 1, 1, 10, 30, 45)),
            // 2023-01-01 11:15:30
            Metric::new(30, timestamp(2023, 1, 1, 11, 15, 30)),
            // 2023-01-02 10:15:30
            Metric::new(40, timestamp(2023, 1, 2, 10, 15, 30)),
        ]
    }
    
    #[test]
    fn test_hour_grouping() {
        let metrics = create_test_metrics();
        let time_grouping = HourGrouping;
        let aggregation = SumAggregation;
        let transformer = TimeGroupingTransformation::new(
            Box::new(time_grouping),
            Box::new(aggregation),
        );
        
        let result = transformer.apply(&metrics).unwrap();
        
        // Should be grouped into 3 hours
        assert_eq!(result.len(), 3);
        
        // Sort by timestamp to ensure consistent order
        let mut sorted_result = result.clone();
        sorted_result.sort_by_key(|m| m.timestamp);
        
        // First hour: 2023-01-01 10:00:00 (two metrics: 10 + 20 = 30)
        let hour1_ts = timestamp(2023, 1, 1, 10, 0, 0);
        assert_eq!(sorted_result[0].timestamp, hour1_ts);
        assert_eq!(sorted_result[0].value, 30);
        
        // Second hour: 2023-01-01 11:00:00 (one metric: 30)
        let hour2_ts = timestamp(2023, 1, 1, 11, 0, 0);
        assert_eq!(sorted_result[1].timestamp, hour2_ts);
        assert_eq!(sorted_result[1].value, 30);
        
        // Third hour: 2023-01-02 10:00:00 (one metric: 40)
        let hour3_ts = timestamp(2023, 1, 2, 10, 0, 0);
        assert_eq!(sorted_result[2].timestamp, hour3_ts);
        assert_eq!(sorted_result[2].value, 40);
    }
    
    #[test]
    fn test_day_grouping() {
        let metrics = create_test_metrics();
        let time_grouping = DayGrouping;
        let aggregation = SumAggregation;
        let transformer = TimeGroupingTransformation::new(
            Box::new(time_grouping),
            Box::new(aggregation),
        );
        
        let result = transformer.apply(&metrics).unwrap();
        
        // Should be grouped into 2 days
        assert_eq!(result.len(), 2);
        
        // Sort by timestamp to ensure consistent order
        let mut sorted_result = result.clone();
        sorted_result.sort_by_key(|m| m.timestamp);
        
        // First day: 2023-01-01 00:00:00 (three metrics: 10 + 20 + 30 = 60)
        let day1_ts = timestamp(2023, 1, 1, 0, 0, 0);
        assert_eq!(sorted_result[0].timestamp, day1_ts);
        assert_eq!(sorted_result[0].value, 60);
        
        // Second day: 2023-01-02 00:00:00 (one metric: 40)
        let day2_ts = timestamp(2023, 1, 2, 0, 0, 0);
        assert_eq!(sorted_result[1].timestamp, day2_ts);
        assert_eq!(sorted_result[1].value, 40);
    }
    
    #[test]
    fn test_time_grouping_factory() {
        let metrics = create_test_metrics();
        let aggregation = SumAggregation;
        
        // Test hour grouping
        let hour_group = create_time_grouping("hour").unwrap();
        let hour_transformer = TimeGroupingTransformation::new(
            hour_group, 
            Box::new(aggregation.clone()),
        );
        let hour_result = hour_transformer.apply(&metrics).unwrap();
        assert_eq!(hour_result.len(), 3);
        
        // Test day grouping
        let day_group = create_time_grouping("day").unwrap();
        let day_transformer = TimeGroupingTransformation::new(
            day_group,
            Box::new(aggregation),
        );
        let day_result = day_transformer.apply(&metrics).unwrap();
        assert_eq!(day_result.len(), 2);
    }
}

#[cfg(test)]
mod test_pipeline {
    use super::*;
    
    fn timestamp(year: i32, month: u32, day: u32, hour: u32, min: u32, sec: u32) -> i64 {
        Utc.with_ymd_and_hms(year, month, day, hour, min, sec)
            .unwrap()
            .timestamp()
    }
    
    fn create_test_metrics() -> Vec<Metric> {
        vec![
            // 2023-01-01 10:15:30
            Metric::new(10, timestamp(2023, 1, 1, 10, 15, 30)),
            // 2023-01-01 10:30:45
            Metric::new(20, timestamp(2023, 1, 1, 10, 30, 45)),
            // 2023-01-01 11:15:30
            Metric::new(5, timestamp(2023, 1, 1, 11, 15, 30)),
            // 2023-01-01 11:45:00
            Metric::new(15, timestamp(2023, 1, 1, 11, 45, 0)),
            // 2023-01-02 10:15:30
            Metric::new(40, timestamp(2023, 1, 2, 10, 15, 30)),
            // 2023-01-02 10:45:30
            Metric::new(50, timestamp(2023, 1, 2, 10, 45, 30)),
        ]
    }
    
    #[test]
    fn test_pipeline_filter_and_aggregate() {
        let metrics = create_test_metrics();
        let mut pipeline = MetricPipeline::new(metrics);
        
        // Add filter for values > 15
        pipeline.filter(Box::new(GreaterThanFilter::new(15))).unwrap();
        
        // Add sum aggregation
        pipeline.aggregate(Box::new(SumAggregation)).unwrap();
        
        let result = pipeline.execute().unwrap();
        
        assert_eq!(result.len(), 1);
        assert_eq!(result[0].value, 110); // 20 + 40 + 50 = 110
    }
    
    #[test]
    fn test_pipeline_filter_and_group_by_day() {
        let metrics = create_test_metrics();
        let mut pipeline = MetricPipeline::new(metrics);
        
        // Add filter for values > 10
        pipeline.filter(Box::new(GreaterThanFilter::new(10))).unwrap();
        
        // Add time grouping by day with sum aggregation
        pipeline.group_by_time(
            Box::new(DayGrouping),
            Box::new(SumAggregation),
        ).unwrap();
        
        let result = pipeline.execute().unwrap();
        
        // Should be grouped into 2 days (after filtering)
        assert_eq!(result.len(), 2);
        
        // Sort by timestamp to ensure consistent order
        let mut sorted_result = result.clone();
        sorted_result.sort_by_key(|m| m.timestamp);
        
        // First day: 2023-01-01 00:00:00 (only value > 10: 20 + 15 = 35)
        let day1_ts = timestamp(2023, 1, 1, 0, 0, 0);
        assert_eq!(sorted_result[0].timestamp, day1_ts);
        assert_eq!(sorted_result[0].value, 35);
        
        // Second day: 2023-01-02 00:00:00 (values > 10: 40 + 50 = 90)
        let day2_ts = timestamp(2023, 1, 2, 0, 0, 0);
        assert_eq!(sorted_result[1].timestamp, day2_ts);
        assert_eq!(sorted_result[1].value, 90);
    }
    
    #[test]
    fn test_complex_pipeline() {
        let metrics = create_test_metrics();
        let mut pipeline = MetricPipeline::new(metrics);
        
        // First filter values > 10
        pipeline.filter(Box::new(GreaterThanFilter::new(10))).unwrap();
        
        // Group by hour with sum aggregation
        pipeline.group_by_time(
            Box::new(HourGrouping),
            Box::new(SumAggregation),
        ).unwrap();
        
        // Then filter aggregated values > 30
        pipeline.filter(Box::new(GreaterThanFilter::new(30))).unwrap();
        
        let result = pipeline.execute().unwrap();
        
        // Should only include hours with sum > 30 (after initial filtering)
        assert_eq!(result.len(), 1);
        
        // Only the second day's 10:00 hour has a sum > 30 (40 + 50 = 90)
        let hour_ts = timestamp(2023, 1, 2, 10, 0, 0);
        assert_eq!(result[0].timestamp, hour_ts);
        assert_eq!(result[0].value, 90);
    }
}