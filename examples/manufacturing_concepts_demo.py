#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manufacturing Concepts Demonstration Script
展示制造工艺概念的专业英文描述和功能

This script demonstrates the comprehensive manufacturing domain classes
with their professional English terminology and Chinese names.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from schemas.code_style.manufacturing_schema import *

def demonstrate_hybrid_machining():
    """演示复合加工类概念"""
    print("=" * 70)
    print("复合加工类 (Hybrid Machining Concepts)")
    print("=" * 70)
    
    # 复合加工
    hybrid_machining = HybridMachining()
    print(f"• {hybrid_machining.name} ({hybrid_machining.chinese_name})")
    print(f"  描述: {hybrid_machining.description}\n")
    
    # 车铣复合
    turn_mill = TurnMill()
    print(f"• {turn_mill.name} ({turn_mill.chinese_name})")
    print(f"  描述: {turn_mill.description}\n")
    
    # 铣车复合
    mill_turn = MillTurn()
    print(f"• {mill_turn.name} ({mill_turn.chinese_name})")
    print(f"  描述: {mill_turn.description}\n")
    
    # 纳米加工
    nano_machining = NanoMachining()
    print(f"• {nano_machining.name} ({nano_machining.chinese_name})")
    print(f"  描述: {nano_machining.description}\n")

def demonstrate_standards_and_quality():
    """演示标准和质量类概念"""
    print("=" * 70)
    print("标准和质量类 (Standards and Quality Concepts)")
    print("=" * 70)
    
    # ISO标准
    iso_standard = ISOStandard("9001", "Quality Management Systems")
    print(f"• {iso_standard.name} ({iso_standard.chinese_name})")
    print(f"  标准号: {iso_standard.standard_number}")
    print(f"  描述: {iso_standard.description}\n")
    
    # DIN标准
    din_standard = DINStandard("6930", "Hexagon Socket Head Cap Screws")
    print(f"• {din_standard.name} ({din_standard.chinese_name})")
    print(f"  标准号: {din_standard.standard_number}")
    print(f"  描述: {din_standard.description}\n")
    
    # 质量等级
    quality_grade = QualityGrade("Grade A", "Premium quality with strict tolerances")
    print(f"• {quality_grade.name} ({quality_grade.chinese_name})")
    print(f"  等级: {quality_grade.grade}")
    print(f"  描述: {quality_grade.description}\n")
    
    # 公差等级
    tolerance_class = ToleranceClass("IT7", 0.025)
    print(f"• {tolerance_class.name} ({tolerance_class.chinese_name})")
    print(f"  公差等级: {tolerance_class.tolerance_class}")
    print(f"  描述: {tolerance_class.description}\n")

def demonstrate_gear_manufacturing():
    """演示齿轮加工类概念"""
    print("=" * 70)
    print("齿轮加工类 (Gear Manufacturing Concepts)")
    print("=" * 70)
    
    # 齿轮加工基础类
    gear_manufacturing = GearManufacturing("gear_manufacturing")
    print(f"• {gear_manufacturing.name} ({gear_manufacturing.chinese_name})")
    print(f"  描述: {gear_manufacturing.description}\n")
    
    gear_processes = [
        GearHobbing(),
        GearShaping(), 
        GearShaving(),
        GearGrinding(),
        GearHoning()
    ]
    
    for process in gear_processes:
        print(f"• {process.name} ({process.chinese_name})")
        print(f"  描述: {process.description}\n")

def demonstrate_thread_manufacturing():
    """演示螺纹加工类概念"""
    print("=" * 70)
    print("螺纹加工类 (Thread Manufacturing Concepts)")
    print("=" * 70)
    
    # 螺纹加工基础类
    thread_manufacturing = ThreadManufacturing("thread_manufacturing")
    print(f"• {thread_manufacturing.name} ({thread_manufacturing.chinese_name})")
    print(f"  描述: {thread_manufacturing.description}\n")
    
    thread_processes = [
        ThreadCutting(),
        ThreadRolling(),
        ThreadGrinding()
    ]
    
    for process in thread_processes:
        print(f"• {process.name} ({process.chinese_name})")
        print(f"  描述: {process.description}\n")

def demonstrate_manufacturing_relations():
    """演示制造关系类概念"""
    print("=" * 70)
    print("制造关系类 (Manufacturing Relation Concepts)")
    print("=" * 70)
    
    # 创建示例实体
    rough_turning = RoughTurning()
    finish_turning = FinishTurning()
    lathe = Lathe("CNC_Lathe_001")
    operator = Operator("张师傅", skill_level="expert")
    surface_roughness = SurfaceRoughness(1.6, "μm")
    
    # 创建各种关系
    relations = [
        ProcessSequenceRelation(rough_turning, finish_turning, sequence_order=1),
        SurfaceRoughnessRequirementRelation(finish_turning, surface_roughness),
        OperatorAssignmentRelation(lathe, operator),
        ToolPositionCountRelation(lathe, 16),
        MaxAccuracyRelation(lathe, "IT4"),
        LocationRelation(lathe, "车间A-3号位"),
    ]
    
    for relation in relations:
        print(f"• {relation.__class__.__name__} ({relation.chinese_name})")
        print(f"  描述: {relation.description}")
        print(f"  关系: {relation.head_entity.name} -> {relation.tail_entity.name}\n")

def demonstrate_comprehensive_machining_scenario():
    """演示综合加工场景"""
    print("=" * 80)
    print("综合制造场景演示 (Comprehensive Manufacturing Scenario)")
    print("=" * 80)
    
    # 材料和工件
    titanium_part = Entity("titanium_aerospace_component", chinese_name="钛合金航空零件")
    ti_alloy = Material("Ti-6Al-4V", "titanium_alloy", "aerospace_grade", chinese_name="钛合金")
    
    # 工艺序列
    processes = [
        RoughTurning(),
        SemiFinishTurning(), 
        FinishTurning(),
        CylindricalGrinding(),
        Superfinishing()
    ]
    
    # 设备
    turn_mill_center = TurnMill()
    grinding_machine = GrindingMachine("precision_grinder_001")
    
    # 工艺参数
    spindle_speed = SpindleSpeed(600, "rpm")
    feed_rate = FeedRate(0.15, "mm/rev")
    surface_finish = SurfaceRoughness(0.8, "μm", "Ra")
    tolerance = ToleranceClass("IT6", 0.016)
    
    # 创建关系网络
    material_rel = MaterialRelation(titanium_part, ti_alloy)
    
    print("加工场景信息:")
    print(f"零件: {titanium_part.name} ({titanium_part.chinese_name})")
    print(f"材料: {ti_alloy.name} ({ti_alloy.chinese_name})")
    print(f"宏观能力指数: {ti_alloy.calculate_machinability_index()}")
    print()
    
    print("工艺序列:")
    for i, process in enumerate(processes, 1):
        print(f"{i}. {process.name} ({process.chinese_name})")
        print(f"   描述: {process.description}")
    print()
    
    print("关键参数:")
    print(f"• 主轴转速: {spindle_speed.value} {spindle_speed.unit}")
    print(f"• 进给量: {feed_rate.value} {feed_rate.unit}")
    print(f"• 表面粗糙度要求: Ra {surface_finish.value} {surface_finish.unit}")
    print(f"• 公差等级: {tolerance.tolerance_class}")
    print()
    
    print("设备配置:")
    print(f"• 复合加工: {turn_mill_center.name} ({turn_mill_center.chinese_name})")
    print(f"• 精密磨削: {grinding_machine.name} ({grinding_machine.chinese_name})")

if __name__ == "__main__":
    print("制造领域Code-Style知识表示架构演示")
    print("Manufacturing Domain Code-Style Knowledge Representation Demo")
    print("=" * 80)
    
    # 运行各个演示函数
    demonstrate_hybrid_machining()
    demonstrate_standards_and_quality()
    demonstrate_gear_manufacturing()
    demonstrate_thread_manufacturing()
    demonstrate_manufacturing_relations()
    demonstrate_comprehensive_machining_scenario()
    
    print("\n演示完成！所有制造工艺概念已完整展示。")
    print("Demo completed! All manufacturing process concepts have been demonstrated.")