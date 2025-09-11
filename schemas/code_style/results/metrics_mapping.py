#!/usr/bin/env python3
"""
指标映射和定义文件
包含论文中所有评估指标的详细定义和中英文对照
"""

# 指标完整映射
METRICS_MAPPING = {
    # 基础指标
    'Precision': {
        'full_name': 'Precision',
        'chinese': '精确率',
        'description': 'The ratio of correctly extracted triples to all extracted triples',
        'category': 'basic'
    },
    'Recall': {
        'full_name': 'Recall',
        'chinese': '召回率',
        'description': 'The ratio of correctly extracted triples to all ground truth triples',
        'category': 'basic'
    },
    'F1': {
        'full_name': 'F1 Score',
        'chinese': 'F1分数',
        'description': 'The harmonic mean of precision and recall',
        'category': 'basic'
    },
    
    # PPRA指标 - Process Parameter Recognition Accuracy
    'PPRA_V': {
        'full_name': 'Process Parameter Recognition Accuracy - Value',
        'chinese': '工艺参数识别准确率-数值',
        'description': 'Accuracy of recognizing numerical process parameters (e.g., Tool Rotation Speed: 120m/min)',
        'example': 'Tool Rotation Speed: 120m/min, Spindle Feed Rate: 0.15mm/r',
        'category': 'ppra'
    },
    'PPRA_R': {
        'full_name': 'Process Parameter Recognition Accuracy - Range',
        'chinese': '工艺参数识别准确率-范围',
        'description': 'Accuracy of recognizing range-based process parameters',
        'example': 'Cutting Speed Range: 100-150m/min',
        'category': 'ppra'
    },
    'PPRA_C': {
        'full_name': 'Process Parameter Recognition Accuracy - Conditional',
        'chinese': '工艺参数识别准确率-条件',
        'description': 'Accuracy of recognizing conditional process parameters',
        'example': 'When machining No.45 Steel, the cutting speed should be 120m/min',
        'category': 'ppra'
    },
    
    # PRCE指标 - Process Relationship Extraction Completeness
    'PRCE_Pre': {
        'full_name': 'Process Relationship Extraction Completeness - Prerequisite',
        'chinese': '工艺关系抽取完整性-前置',
        'description': 'Completeness of extracting prerequisite process logic',
        'example': 'Heat Treatment → Semi-finish Milling → Drilling → Tapping',
        'category': 'prce'
    },
    'PRCE_Par': {
        'full_name': 'Process Relationship Extraction Completeness - Parallel',
        'chinese': '工艺关系抽取完整性-并行',
        'description': 'Completeness of extracting parallel process logic',
        'example': 'Drilling ↔ Tapping (can be performed simultaneously)',
        'category': 'prce'
    },
    'PRCE_C': {
        'full_name': 'Process Relationship Extraction Completeness - Conditional',
        'chinese': '工艺关系抽取完整性-条件',
        'description': 'Completeness of extracting conditional process logic',
        'example': 'Fine Milling → [Ra≤1.6] → Polishing → Surface Treatment',
        'category': 'prce'
    },
    
    # EPMR指标 - Equipment-Parameter Mapping Reliability
    'EPMR_E': {
        'full_name': 'Equipment-Parameter Mapping Reliability - Equipment Level',
        'chinese': '设备参数映射可靠性-设备级',
        'description': 'Reliability of mapping equipment to their parameters',
        'example': 'Machining Center → Spindle Speed',
        'category': 'epmr'
    },
    'EPMR_P': {
        'full_name': 'Equipment-Parameter Mapping Reliability - Part Level',
        'chinese': '设备参数映射可靠性-零件级',
        'description': 'Reliability of mapping parts/tools to their parameters',
        'example': 'Cutting Tool → Tool Life',
        'category': 'epmr'
    },
    'EPMR_D': {
        'full_name': 'Equipment-Parameter Mapping Reliability - Data Level',
        'chinese': '设备参数映射可靠性-数据级',
        'description': 'Reliability of mapping specific data values',
        'example': 'Lathe Tool - Rake Angle → Angle Value 7.8°',
        'category': 'epmr'
    },
    
    # 效率指标
    'avg_tokens': {
        'full_name': 'Average Tokens',
        'chinese': '平均Token数',
        'description': 'Average number of tokens required for knowledge representation',
        'category': 'efficiency'
    },
    'avg_latency': {
        'full_name': 'Average Latency',
        'chinese': '平均延迟',
        'description': 'Average processing latency in milliseconds',
        'category': 'efficiency'
    }
}

# 指标类别
METRIC_CATEGORIES = {
    'basic': {
        'name': 'Basic Metrics',
        'chinese': '基础指标',
        'metrics': ['Precision', 'Recall', 'F1']
    },
    'ppra': {
        'name': 'Process Parameter Recognition Accuracy',
        'chinese': '工艺参数识别准确率',
        'metrics': ['PPRA_V', 'PPRA_R', 'PPRA_C']
    },
    'prce': {
        'name': 'Process Relationship Extraction Completeness',
        'chinese': '工艺关系抽取完整性',
        'metrics': ['PRCE_Pre', 'PRCE_Par', 'PRCE_C']
    },
    'epmr': {
        'name': 'Equipment-Parameter Mapping Reliability',
        'chinese': '设备参数映射可靠性',
        'metrics': ['EPMR_E', 'EPMR_P', 'EPMR_D']
    },
    'efficiency': {
        'name': 'Efficiency Metrics',
        'chinese': '效率指标',
        'metrics': ['avg_tokens', 'avg_latency']
    }
}

def get_metric_info(metric_name):
    if metric_name in METRICS_MAPPING:
        return METRICS_MAPPING[metric_name]
    return None

def get_category_metrics(category_name):
    if category_name in METRIC_CATEGORIES:
        category = METRIC_CATEGORIES[category_name]
        metrics = {}
        for metric_name in category['metrics']:
            metrics[metric_name] = METRICS_MAPPING[metric_name]
        return metrics
    return None

def print_all_metrics():
    for category_key, category in METRIC_CATEGORIES.items():
        print(f"\n=== {category['name']} ({category['chinese']}) ===")
        for metric_name in category['metrics']:
            metric = METRICS_MAPPING[metric_name]
            if 'example' in metric:
                print(f"  示例: {metric['example']}")

if __name__ == '__main__':
    print_all_metrics()