#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manufacturing Domain Code-Style Schema Definition
Based on Paper Section 4.2 and KnowCoder Architecture

This file implements the Code-Style knowledge representation for manufacturing domain,
following the four-layer hierarchical framework defined in the paper.

All class names use professional English terminology from mechanical engineering,
with Chinese names stored in the 'chinese_name' attribute for reference.
"""

from typing import List, Optional, Union
from abc import ABC, abstractmethod
import math

# =============================================================================
# Base Classes - Foundation of the Code-Style Architecture
# =============================================================================

class Entity:
    """Base entity class for all manufacturing entities."""
    def __init__(self, name: str, chinese_name: str = "", 
                 supporting_chunks: Optional[List[str]] = None, 
                 description: Optional[str] = None, summary: Optional[str] = None):
        self.name = name
        self.chinese_name = chinese_name
        self.supporting_chunks = supporting_chunks or []
        self.description = description
        self.summary = summary

class Relation:
    """Base relation class for all manufacturing relations."""
    def __init__(self, head_entity: Entity, tail_entity: Entity,
                 chinese_name: str = "", supporting_chunks: Optional[List[str]] = None,
                 description: Optional[str] = None, confidence: float = 1.0):
        self.head_entity = head_entity
        self.tail_entity = tail_entity
        self.chinese_name = chinese_name
        self.supporting_chunks = supporting_chunks or []
        self.description = description
        self.confidence = confidence

class Event:
    """Base event class for all manufacturing events."""
    def __init__(self, event_type: str, chinese_name: str = "",
                 timestamp: Optional[str] = None,
                 supporting_chunks: Optional[List[str]] = None,
                 description: Optional[str] = None):
        self.event_type = event_type
        self.chinese_name = chinese_name
        self.timestamp = timestamp
        self.supporting_chunks = supporting_chunks or []
        self.description = description

# =============================================================================
# Layer 1: Processing Parameter Data Layer
# =============================================================================

class ProcessParameter(Entity):
    """Base class for all process parameters."""
    def __init__(self, name: str, value: Union[str, float, int], unit: str,
                 chinese_name: str = "", tolerance: Optional[str] = None, **kwargs):
        super().__init__(name, chinese_name, **kwargs)
        self.value = value
        self.unit = unit
        self.tolerance = tolerance

class SpindleSpeed(ProcessParameter):
    """Spindle rotation speed parameter."""
    def __init__(self, value: Union[str, float], unit: str = "rpm", **kwargs):
        super().__init__("spindle_speed", value, unit, chinese_name="主轴转速", **kwargs)
        
    def is_valid_range(self, min_speed: float = 0, max_speed: float = 10000) -> bool:
        """Validate spindle speed within operational range."""
        if isinstance(self.value, (int, float)):
            return min_speed <= self.value <= max_speed
        return True
    
    def calculate_cutting_speed(self, diameter: float) -> float:
        """Calculate cutting speed from spindle speed and workpiece diameter."""
        if isinstance(self.value, (int, float)):
            return math.pi * diameter * self.value / 1000
        return 0.0

class CuttingSpeed(ProcessParameter):
    """Cutting speed parameter."""
    def __init__(self, value: Union[str, float], unit: str = "m/min", **kwargs):
        super().__init__("cutting_speed", value, unit, chinese_name="切削速度", **kwargs)
    
    def calculate_spindle_speed(self, diameter: float) -> float:
        """Calculate required spindle speed for given diameter."""
        if isinstance(self.value, (int, float)) and diameter > 0:
            return (self.value * 1000) / (math.pi * diameter)
        return 0.0

class FeedRate(ProcessParameter):
    """Feed rate parameter."""
    def __init__(self, value: Union[str, float], unit: str = "mm/rev", **kwargs):
        super().__init__("feed_rate", value, unit, chinese_name="进给量", **kwargs)
    
    def calculate_feed_speed(self, spindle_speed: float) -> float:
        """Calculate feed speed in mm/min."""
        if isinstance(self.value, (int, float)):
            return self.value * spindle_speed
        return 0.0

class DepthOfCut(ProcessParameter):
    """Depth of cut parameter."""
    def __init__(self, value: Union[str, float], unit: str = "mm", **kwargs):
        super().__init__("depth_of_cut", value, unit, chinese_name="切削深度", **kwargs)

class MachiningAllowance(ProcessParameter):
    """Machining allowance parameter."""
    def __init__(self, value: Union[str, float], unit: str = "mm", **kwargs):
        super().__init__("machining_allowance", value, unit, chinese_name="加工余量", **kwargs)

class SurfaceRoughness(ProcessParameter):
    """Surface roughness requirement."""
    def __init__(self, value: Union[str, float], unit: str = "μm", 
                 roughness_type: str = "Ra", **kwargs):
        super().__init__("surface_roughness", value, unit, chinese_name="表面粗糙度要求", **kwargs)
        self.roughness_type = roughness_type
    
    def is_within_tolerance(self, measured_value: float) -> bool:
        """Check if measured roughness is within tolerance."""
        if isinstance(self.value, (int, float)):
            return measured_value <= self.value
        return False

class HardnessRequirement(ProcessParameter):
    """Hardness requirement parameter."""
    def __init__(self, value: Union[str, float], unit: str = "HRC", **kwargs):
        super().__init__("hardness_requirement", value, unit, chinese_name="硬度要求", **kwargs)

class ToleranceGrade(ProcessParameter):
    """Target tolerance parameter."""
    def __init__(self, value: str, unit: str = "", **kwargs):
        super().__init__("tolerance_grade", value, unit, chinese_name="目标公差", **kwargs)

# =============================================================================
# Layer 2: Equipment Resource Layer
# =============================================================================

class Resource(Entity):
    """Base class for all manufacturing resources."""
    def __init__(self, name: str, resource_type: str, chinese_name: str = "", **kwargs):
        super().__init__(name, chinese_name, **kwargs)
        self.resource_type = resource_type

class Material(Resource):
    """Manufacturing materials."""
    def __init__(self, name: str, material_type: str = "metal", 
                 grade: Optional[str] = None, chinese_name: str = "材料", **kwargs):
        super().__init__(name, "material", chinese_name, **kwargs)
        self.material_type = material_type
        self.grade = grade

    def is_compatible_with_process(self, process: str) -> bool:
        """Check if material is suitable for specific machining process."""
        compatibility_map = {
            "titanium_alloy": ["turning", "milling", "grinding", "edm", "laser_cutting"],
            "carbon_steel_45": ["turning", "milling", "planing", "grinding", "drilling", "forging"],
            "stainless_steel": ["turning", "milling", "drilling", "laser_cutting", "waterjet"],
            "aluminum_alloy": ["milling", "turning", "drilling", "laser_cutting", "waterjet"],
            "copper_alloy": ["turning", "milling", "ecm", "laser_cutting"],
            "superalloy": ["grinding", "edm", "laser_machining"],
            "cemented_carbide": ["grinding", "edm", "laser_machining"]
        }
        return process in compatibility_map.get(self.material_type, [])
    
    def calculate_machinability_index(self) -> float:
        """Calculate machinability index (relative to free-cutting steel = 100)."""
        machinability_map = {
            "free_cutting_steel": 100,
            "carbon_steel_45": 65,
            "stainless_steel": 45,
            "titanium_alloy": 20,
            "superalloy": 15,
            "cemented_carbide": 5
        }
        return machinability_map.get(self.material_type, 50)

class CuttingTool(Resource):
    """Cutting tools."""
    def __init__(self, name: str, tool_type: str, tool_material: str = "carbide", 
                 chinese_name: str = "刀具", **kwargs):
        super().__init__(name, "cutting_tool", chinese_name, **kwargs)
        self.tool_type = tool_type
        self.tool_material = tool_material
    
    def get_recommended_cutting_speed(self, workpiece_material: str) -> float:
        """Get recommended cutting speed for given material."""
        speed_map = {
            ("carbide", "steel"): 150,
            ("carbide", "stainless_steel"): 80,
            ("cbn", "hardened_steel"): 200,
            ("ceramic", "cast_iron"): 300,
            ("hss", "aluminum"): 200
        }
        return speed_map.get((self.tool_material, workpiece_material), 100)

class CarbideTool(CuttingTool):
    """Carbide cutting tools."""
    def __init__(self, name: str, **kwargs):
        super().__init__(name, "carbide_tool", "carbide", chinese_name="硬质合金刀具", **kwargs)

class CBNTool(CuttingTool):
    """CBN (Cubic Boron Nitride) cutting tools."""
    def __init__(self, name: str, **kwargs):
        super().__init__(name, "cbn_tool", "cbn", chinese_name="CBN刀具", **kwargs)

class CeramicTool(CuttingTool):
    """Ceramic cutting tools."""
    def __init__(self, name: str, **kwargs):
        super().__init__(name, "ceramic_tool", "ceramic", chinese_name="陶瓷刀具", **kwargs)

class DiamondTool(CuttingTool):
    """Diamond cutting tools."""
    def __init__(self, name: str, **kwargs):
        super().__init__(name, "diamond_tool", "diamond", chinese_name="金刚石刀具", **kwargs)

# =============================================================================
# Layer 3: Process Equipment Layer
# =============================================================================

class Equipment(Entity):
    """Base class for all manufacturing equipment."""
    def __init__(self, name: str, equipment_type: str, model: Optional[str] = None,
                 chinese_name: str = "", **kwargs):
        super().__init__(name, chinese_name, **kwargs)
        self.equipment_type = equipment_type
        self.model = model

class CNCMachiningCenter(Equipment):
    """CNC machining center."""
    def __init__(self, name: str, model: Optional[str] = None, 
                 tool_positions: int = 16, max_accuracy: str = "IT4", **kwargs):
        super().__init__(name, "cnc_machining_center", model, 
                        chinese_name="数控加工中心", **kwargs)
        self.tool_positions = tool_positions
        self.max_accuracy = max_accuracy
        
    def can_perform_operation(self, operation: str) -> bool:
        """Check if machining center can perform specific operation."""
        supported_operations = ["milling", "drilling", "boring", "tapping", "contouring",
                              "pocketing", "surface_machining", "thread_milling"]
        return operation in supported_operations
    
    def estimate_setup_time(self, tool_changes: int) -> float:
        """Estimate setup time based on tool changes required."""
        base_setup_time = 15  # minutes
        tool_change_time = 0.5  # minutes per tool
        return base_setup_time + (tool_changes * tool_change_time)

class Lathe(Equipment):
    """Lathe machine."""
    def __init__(self, name: str, model: Optional[str] = None, **kwargs):
        super().__init__(name, "lathe", model, chinese_name="车床", **kwargs)
    
    def calculate_taper_angle(self, large_dia: float, small_dia: float, length: float) -> float:
        """Calculate taper angle for taper turning."""
        if length > 0:
            return math.degrees(math.atan((large_dia - small_dia) / (2 * length)))
        return 0.0

class MillingMachine(Equipment):
    """Milling machine."""
    def __init__(self, name: str, model: Optional[str] = None, **kwargs):
        super().__init__(name, "milling_machine", model, chinese_name="铣床", **kwargs)

class GrindingMachine(Equipment):
    """Grinding machine."""
    def __init__(self, name: str, model: Optional[str] = None, **kwargs):
        super().__init__(name, "grinding_machine", model, chinese_name="磨床", **kwargs)

class DrillingMachine(Equipment):
    """Drilling machine."""
    def __init__(self, name: str, model: Optional[str] = None, **kwargs):
        super().__init__(name, "drilling_machine", model, chinese_name="钻床", **kwargs)

class EDMMachine(Equipment):
    """Electrical Discharge Machine."""
    def __init__(self, name: str, model: Optional[str] = None, **kwargs):
        super().__init__(name, "edm_machine", model, chinese_name="电火花机", **kwargs)

class LaserCuttingMachine(Equipment):
    """Laser cutting machine."""
    def __init__(self, name: str, power: float = 1000, model: Optional[str] = None, **kwargs):
        super().__init__(name, "laser_cutting_machine", model, chinese_name="激光切割机", **kwargs)
        self.power = power  # watts

class Operator(Entity):
    """Machine operator."""
    def __init__(self, name: str, skill_level: str = "skilled", **kwargs):
        super().__init__(name, chinese_name="操作人员", **kwargs)
        self.skill_level = skill_level

# =============================================================================
# Layer 4: Machining Process Layer
# =============================================================================

class ManufacturingProcess(Entity):
    """Base class for all manufacturing processes."""
    def __init__(self, name: str, process_type: str, chinese_name: str = "", **kwargs):
        super().__init__(name, chinese_name, **kwargs)
        self.process_type = process_type
        
    def calculate_machining_time(self, workpiece_volume: float, removal_rate: float) -> float:
        """Calculate estimated machining time based on material removal."""
        if removal_rate > 0:
            return workpiece_volume / removal_rate
        return 0.0

class MechanicalMachining(ManufacturingProcess):
    """Mechanical machining base class."""
    def __init__(self, name: str, chinese_name: str = "机械加工", **kwargs):
        super().__init__(name, "mechanical_machining", chinese_name, **kwargs)

class CuttingProcess(MechanicalMachining):
    """Cutting machining processes."""
    def __init__(self, name: str, chinese_name: str = "切削加工", **kwargs):
        super().__init__(name, chinese_name, **kwargs)
        self.process_type = "cutting_process"
    
    def calculate_material_removal_rate(self, cutting_speed: float, feed: float, depth: float) -> float:
        """Calculate material removal rate in cm³/min."""
        return cutting_speed * feed * depth / 1000

class Turning(CuttingProcess):
    """Turning process."""
    def __init__(self, name: str = "turning", **kwargs):
        super().__init__(name, chinese_name="车削", **kwargs)
        
    def calculate_cutting_time(self, length: float, spindle_speed: float, feed_rate: float) -> float:
        """Calculate cutting time for turning operation."""
        if spindle_speed > 0 and feed_rate > 0:
            return length / (feed_rate * spindle_speed)
        return 0.0
    
    def calculate_cutting_speed(self, diameter: float, spindle_speed: float) -> float:
        """Calculate cutting speed in m/min."""
        return math.pi * diameter * spindle_speed / 1000

class RoughTurning(Turning):
    """Rough turning process."""
    def __init__(self, **kwargs):
        super().__init__("rough_turning", **kwargs)
        self.chinese_name = "粗车"

class SemiFinishTurning(Turning):
    """Semi-finish turning process."""
    def __init__(self, **kwargs):
        super().__init__("semi_finish_turning", **kwargs)
        self.chinese_name = "半精车"

class FinishTurning(Turning):
    """Finish turning process."""
    def __init__(self, **kwargs):
        super().__init__("finish_turning", **kwargs)
        self.chinese_name = "精车"

class Milling(CuttingProcess):
    """Milling process."""
    def __init__(self, name: str = "milling", **kwargs):
        super().__init__(name, chinese_name="铣削", **kwargs)
    
    def calculate_table_feed(self, feed_per_tooth: float, teeth: int, spindle_speed: float) -> float:
        """Calculate table feed speed in mm/min."""
        return feed_per_tooth * teeth * spindle_speed

class FaceMilling(Milling):
    """Face milling process."""
    def __init__(self, **kwargs):
        super().__init__("face_milling", **kwargs)
        self.chinese_name = "面铣"

class EndMilling(Milling):
    """End milling process."""
    def __init__(self, **kwargs):
        super().__init__("end_milling", **kwargs)
        self.chinese_name = "立铣"

class SlotMilling(Milling):
    """Slot milling process."""
    def __init__(self, **kwargs):
        super().__init__("slot_milling", **kwargs)
        self.chinese_name = "铣槽"

class Drilling(CuttingProcess):
    """Drilling process."""
    def __init__(self, name: str = "drilling", **kwargs):
        super().__init__(name, chinese_name="钻削", **kwargs)
    
    def calculate_drilling_time(self, depth: float, feed: float, spindle_speed: float) -> float:
        """Calculate drilling time in minutes."""
        if feed > 0 and spindle_speed > 0:
            feed_rate = feed * spindle_speed
            return depth / feed_rate
        return 0.0

class Reaming(CuttingProcess):
    """Reaming process for precision hole finishing."""
    def __init__(self, **kwargs):
        super().__init__("reaming", chinese_name="铰削", **kwargs)

class Boring(CuttingProcess):
    """Boring process for internal machining."""
    def __init__(self, **kwargs):
        super().__init__("boring", chinese_name="镗削", **kwargs)

class Tapping(CuttingProcess):
    """Tapping process for thread cutting."""
    def __init__(self, **kwargs):
        super().__init__("tapping", chinese_name="攻丝", **kwargs)

class Grinding(CuttingProcess):
    """Grinding process."""
    def __init__(self, name: str = "grinding", **kwargs):
        super().__init__(name, chinese_name="磨削", **kwargs)

class CylindricalGrinding(Grinding):
    """Cylindrical grinding."""
    def __init__(self, **kwargs):
        super().__init__("cylindrical_grinding", **kwargs)
        self.chinese_name = "外圆磨削"

class SurfaceGrinding(Grinding):
    """Surface grinding."""
    def __init__(self, **kwargs):
        super().__init__("surface_grinding", **kwargs)
        self.chinese_name = "平面磨削"

class InternalGrinding(Grinding):
    """Internal grinding."""
    def __init__(self, **kwargs):
        super().__init__("internal_grinding", **kwargs)
        self.chinese_name = "内圆磨削"

class CenterlessGrinding(Grinding):
    """Centerless grinding."""
    def __init__(self, **kwargs):
        super().__init__("centerless_grinding", **kwargs)
        self.chinese_name = "无心磨削"

class Planing(CuttingProcess):
    """Planing process."""
    def __init__(self, **kwargs):
        super().__init__("planing", chinese_name="刨削", **kwargs)

class Shaping(CuttingProcess):
    """Shaping process."""
    def __init__(self, **kwargs):
        super().__init__("shaping", chinese_name="插削", **kwargs)

class Broaching(CuttingProcess):
    """Broaching process."""
    def __init__(self, **kwargs):
        super().__init__("broaching", chinese_name="拉削", **kwargs)

class Honing(ManufacturingProcess):
    """Honing process for surface finishing."""
    def __init__(self, **kwargs):
        super().__init__("honing", "finishing_process", chinese_name="珩磨", **kwargs)

class Lapping(ManufacturingProcess):
    """Lapping process for ultra-precision finishing."""
    def __init__(self, **kwargs):
        super().__init__("lapping", "finishing_process", chinese_name="研磨", **kwargs)

class Polishing(ManufacturingProcess):
    """Polishing process for surface quality."""
    def __init__(self, **kwargs):
        super().__init__("polishing", "surface_treatment", chinese_name="抛光", **kwargs)

class Superfinishing(ManufacturingProcess):
    """Superfinishing process."""
    def __init__(self, **kwargs):
        super().__init__("superfinishing", "finishing_process", chinese_name="超精加工", **kwargs)

# Heat Treatment Processes
class HeatTreatment(ManufacturingProcess):
    """Heat treatment process."""
    def __init__(self, name: str, treatment_type: str, chinese_name: str = "热处理", **kwargs):
        super().__init__(name, "heat_treatment", chinese_name, **kwargs)
        self.treatment_type = treatment_type

class Carburizing(HeatTreatment):
    """Carburizing process."""
    def __init__(self, **kwargs):
        super().__init__("carburizing", "chemical_heat_treatment", chinese_name="渗碳", **kwargs)

class Nitriding(HeatTreatment):
    """Nitriding process."""
    def __init__(self, **kwargs):
        super().__init__("nitriding", "chemical_heat_treatment", chinese_name="渗氮", **kwargs)

class Quenching(HeatTreatment):
    """Quenching process."""
    def __init__(self, **kwargs):
        super().__init__("quenching", "thermal_treatment", chinese_name="淬火", **kwargs)

class Tempering(HeatTreatment):
    """Tempering process."""
    def __init__(self, **kwargs):
        super().__init__("tempering", "thermal_treatment", chinese_name="回火", **kwargs)

class Annealing(HeatTreatment):
    """Annealing process."""
    def __init__(self, **kwargs):
        super().__init__("annealing", "thermal_treatment", chinese_name="退火", **kwargs)

class Normalizing(HeatTreatment):
    """Normalizing process."""
    def __init__(self, **kwargs):
        super().__init__("normalizing", "thermal_treatment", chinese_name="正火", **kwargs)

# Special Machining Processes
class EDM(ManufacturingProcess):
    """Electrical Discharge Machining."""
    def __init__(self, **kwargs):
        super().__init__("edm", "special_machining", chinese_name="电火花加工", **kwargs)

class WireEDM(EDM):
    """Wire electrical discharge machining."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "wire_edm"
        self.chinese_name = "线切割"

class ECM(ManufacturingProcess):
    """Electrochemical machining."""
    def __init__(self, **kwargs):
        super().__init__("ecm", "special_machining", chinese_name="电解加工", **kwargs)

class LaserMachining(ManufacturingProcess):
    """Laser machining process."""
    def __init__(self, **kwargs):
        super().__init__("laser_machining", "special_machining", chinese_name="激光加工", **kwargs)

class LaserCutting(LaserMachining):
    """Laser cutting process."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "laser_cutting"
        self.chinese_name = "激光切割"

class WaterjetCutting(ManufacturingProcess):
    """Waterjet cutting process."""
    def __init__(self, **kwargs):
        super().__init__("waterjet_cutting", "special_machining", chinese_name="水切割", **kwargs)

class UltrasonicMachining(ManufacturingProcess):
    """Ultrasonic machining process."""
    def __init__(self, **kwargs):
        super().__init__("ultrasonic_machining", "special_machining", chinese_name="超声波加工", **kwargs)

class ElectronBeamMachining(ManufacturingProcess):
    """Electron beam machining."""
    def __init__(self, **kwargs):
        super().__init__("electron_beam_machining", "special_machining", chinese_name="电子束加工", **kwargs)

class IonBeamMachining(ManufacturingProcess):
    """Ion beam machining."""
    def __init__(self, **kwargs):
        super().__init__("ion_beam_machining", "special_machining", chinese_name="离子束加工", **kwargs)

class PlasmaMachining(ManufacturingProcess):
    """Plasma machining."""
    def __init__(self, **kwargs):
        super().__init__("plasma_machining", "special_machining", chinese_name="等离子加工", **kwargs)

# Forming Processes
class FormingProcess(ManufacturingProcess):
    """Base class for forming processes."""
    def __init__(self, name: str, chinese_name: str = "", **kwargs):
        super().__init__(name, "forming_process", chinese_name, **kwargs)

class Casting(FormingProcess):
    """Casting process."""
    def __init__(self, **kwargs):
        super().__init__("casting", chinese_name="铸造", **kwargs)

class Forging(FormingProcess):
    """Forging process."""
    def __init__(self, **kwargs):
        super().__init__("forging", chinese_name="锻造", **kwargs)

class Stamping(FormingProcess):
    """Stamping process."""
    def __init__(self, **kwargs):
        super().__init__("stamping", chinese_name="冲压", **kwargs)

class Extrusion(FormingProcess):
    """Extrusion process."""
    def __init__(self, **kwargs):
        super().__init__("extrusion", chinese_name="挤压", **kwargs)

class Rolling(FormingProcess):
    """Rolling process."""
    def __init__(self, **kwargs):
        super().__init__("rolling", chinese_name="滚压", **kwargs)

class Bending(FormingProcess):
    """Bending process."""
    def __init__(self, **kwargs):
        super().__init__("bending", chinese_name="弯曲", **kwargs)

class DeepDrawing(FormingProcess):
    """Deep drawing process."""
    def __init__(self, **kwargs):
        super().__init__("deep_drawing", chinese_name="拉深", **kwargs)

# Advanced Manufacturing Processes
class AdditiveManufacturing(ManufacturingProcess):
    """Additive manufacturing (3D Printing)."""
    def __init__(self, technology: str = "SLM", **kwargs):
        super().__init__("additive_manufacturing", "advanced_manufacturing", 
                        chinese_name="增材制造", **kwargs)
        self.technology = technology

class HybridMachining(ManufacturingProcess):
    """Hybrid machining process."""
    def __init__(self, **kwargs):
        super().__init__("hybrid_machining", "advanced_manufacturing", 
                        chinese_name="复合加工", **kwargs)

class TurnMill(HybridMachining):
    """Turn-mill complex machining."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "turn_mill"
        self.chinese_name = "车铣复合"

class MillTurn(HybridMachining):
    """Mill-turn complex machining."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "mill_turn"
        self.chinese_name = "铣车复合"

class FiveAxisMachining(ManufacturingProcess):
    """Five-axis machining."""
    def __init__(self, **kwargs):
        super().__init__("five_axis_machining", "advanced_manufacturing",
                        chinese_name="五轴加工", **kwargs)

class MicroMachining(ManufacturingProcess):
    """Micro machining."""
    def __init__(self, **kwargs):
        super().__init__("micro_machining", "precision_machining",
                        chinese_name="微细加工", **kwargs)

class NanoMachining(ManufacturingProcess):
    """Nano machining."""
    def __init__(self, **kwargs):
        super().__init__("nano_machining", "ultra_precision_machining",
                        chinese_name="纳米加工", **kwargs)

# =============================================================================
# Manufacturing Relation Classes
# =============================================================================

class MaterialRelation(Relation):
    """Material relations."""
    def __init__(self, head_entity: Entity, tail_entity: Material, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="材料", **kwargs)
        
class ProcessingMethodRelation(Relation):
    """Processing method relation."""
    def __init__(self, head_entity: Entity, tail_entity: ManufacturingProcess, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="加工方法", **kwargs)

class ProcessSequenceRelation(Relation):
    """Process sequence relation."""
    def __init__(self, head_entity: ManufacturingProcess, tail_entity: ManufacturingProcess, 
                 sequence_order: int, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="加工工序", **kwargs)
        self.sequence_order = sequence_order

class SurfaceRoughnessRequirementRelation(Relation):
    """Surface roughness requirement relation."""
    def __init__(self, head_entity: Entity, tail_entity: SurfaceRoughness, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="表面粗糙度要求", **kwargs)

class EquipmentUsageRelation(Relation):
    """Equipment usage relation."""
    def __init__(self, head_entity: ManufacturingProcess, tail_entity: Equipment, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="使用设备", **kwargs)

class ToolUsageRelation(Relation):
    """Tool usage relation."""
    def __init__(self, head_entity: ManufacturingProcess, tail_entity: CuttingTool, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="使用刀具", **kwargs)

class SpindleSpeedSettingRelation(Relation):
    """Spindle speed setting relation."""
    def __init__(self, head_entity: ManufacturingProcess, tail_entity: SpindleSpeed, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="主轴转速", **kwargs)

class CuttingSpeedSettingRelation(Relation):
    """Cutting speed setting relation."""
    def __init__(self, head_entity: ManufacturingProcess, tail_entity: CuttingSpeed, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="切削速度", **kwargs)

class FeedRateSettingRelation(Relation):
    """Feed rate setting relation."""
    def __init__(self, head_entity: ManufacturingProcess, tail_entity: FeedRate, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="进给量", **kwargs)

class CoolingMethodRelation(Relation):
    """Cooling method relation."""
    def __init__(self, head_entity: ManufacturingProcess, tail_entity: str, 
                 cooling_type: str, **kwargs):
        super().__init__(head_entity, Entity(tail_entity), chinese_name="冷却方式", **kwargs)
        self.cooling_type = cooling_type

class DepthOfCutSettingRelation(Relation):
    """Depth of cut setting relation."""
    def __init__(self, head_entity: ManufacturingProcess, tail_entity: DepthOfCut, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="切削深度", **kwargs)

class MachiningAllowanceRelation(Relation):
    """Machining allowance relation."""
    def __init__(self, head_entity: ManufacturingProcess, tail_entity: MachiningAllowance, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="加工余量", **kwargs)

class HeatTreatmentMethodRelation(Relation):
    """Heat treatment method relation."""
    def __init__(self, head_entity: Entity, tail_entity: HeatTreatment, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="热处理方式", **kwargs)

class HardnessRequirementRelation(Relation):
    """Hardness requirement relation."""
    def __init__(self, head_entity: Entity, tail_entity: HardnessRequirement, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="硬度要求", **kwargs)

class ToleranceRequirementRelation(Relation):
    """Tolerance requirement relation."""
    def __init__(self, head_entity: Entity, tail_entity: ToleranceGrade, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="目标公差", **kwargs)

class OperatorAssignmentRelation(Relation):
    """Operator assignment relation."""
    def __init__(self, head_entity: Equipment, tail_entity: Operator, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="操作人员", **kwargs)

class ToolPositionCountRelation(Relation):
    """Tool position count relation."""
    def __init__(self, head_entity: Equipment, tail_entity: int, **kwargs):
        super().__init__(head_entity, Entity(str(tail_entity)), chinese_name="刀位数量", **kwargs)
        self.tool_count = tail_entity

class SuitableForRelation(Relation):
    """Suitable for relation."""
    def __init__(self, head_entity: Entity, tail_entity: Entity, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="适用于", **kwargs)

class MaxAccuracyRelation(Relation):
    """Maximum accuracy relation."""
    def __init__(self, head_entity: Equipment, tail_entity: str, **kwargs):
        super().__init__(head_entity, Entity(tail_entity), chinese_name="最高精度", **kwargs)

class LocationRelation(Relation):
    """Location relation."""
    def __init__(self, head_entity: Equipment, tail_entity: str, **kwargs):
        super().__init__(head_entity, Entity(tail_entity), chinese_name="所在位置", **kwargs)

class BelongsToProcessRelation(Relation):
    """Belongs to process relation."""
    def __init__(self, head_entity: ManufacturingProcess, tail_entity: ManufacturingProcess, **kwargs):
        super().__init__(head_entity, tail_entity, chinese_name="属于（工艺）", **kwargs)

# =============================================================================
# Manufacturing Event Classes
# =============================================================================

class ProcessEvent(Event):
    """Base manufacturing process event."""
    def __init__(self, event_type: str, process: ManufacturingProcess, 
                 chinese_name: str = "", **kwargs):
        super().__init__(event_type, chinese_name, **kwargs)
        self.process = process

class ProcessStartEvent(ProcessEvent):
    """Process start event."""
    def __init__(self, process: ManufacturingProcess, **kwargs):
        super().__init__("process_start", process, chinese_name="工艺开始", **kwargs)

class ProcessCompleteEvent(ProcessEvent):
    """Process completion event."""
    def __init__(self, process: ManufacturingProcess, **kwargs):
        super().__init__("process_complete", process, chinese_name="工艺完成", **kwargs)

class QualityInspectionEvent(Event):
    """Quality inspection event."""
    def __init__(self, inspection_type: str, result: str, **kwargs):
        super().__init__("quality_inspection", chinese_name="质量检测", **kwargs)
        self.inspection_type = inspection_type
        self.result = result

class ToolChangeEvent(Event):
    """Tool change event."""
    def __init__(self, old_tool: CuttingTool, new_tool: CuttingTool, **kwargs):
        super().__init__("tool_change", chinese_name="换刀", **kwargs)
        self.old_tool = old_tool
        self.new_tool = new_tool

class MaintenanceEvent(Event):
    """Equipment maintenance event."""
    def __init__(self, equipment: Equipment, maintenance_type: str, **kwargs):
        super().__init__("maintenance", chinese_name="设备维护", **kwargs)
        self.equipment = equipment
        self.maintenance_type = maintenance_type

class BreakdownEvent(Event):
    """Equipment breakdown event."""
    def __init__(self, equipment: Equipment, failure_mode: str, **kwargs):
        super().__init__("breakdown", chinese_name="设备故障", **kwargs)
        self.equipment = equipment
        self.failure_mode = failure_mode

# =============================================================================
# Manufacturing Standards and Quality
# =============================================================================

class ISOStandard(Entity):
    """ISO standards."""
    def __init__(self, standard_number: str, title: str, **kwargs):
        super().__init__(f"ISO_{standard_number}", chinese_name="ISO标准", **kwargs)
        self.standard_number = standard_number
        self.title = title

class DINStandard(Entity):
    """DIN standards."""
    def __init__(self, standard_number: str, title: str, **kwargs):
        super().__init__(f"DIN_{standard_number}", chinese_name="DIN标准", **kwargs)
        self.standard_number = standard_number
        self.title = title

class QualityGrade(Entity):
    """Quality grade classification."""
    def __init__(self, grade: str, description: str, **kwargs):
        super().__init__(grade, chinese_name="质量等级", **kwargs)
        self.grade = grade
        self.description = description

class ToleranceClass(Entity):
    """Tolerance class specification."""
    def __init__(self, tolerance_class: str, tolerance_value: float, **kwargs):
        super().__init__(tolerance_class, chinese_name="公差等级", **kwargs)
        self.tolerance_class = tolerance_class
        self.tolerance_value = tolerance_value

# =============================================================================
# Gear Manufacturing Processes (Special Category from CSV)
# =============================================================================

class GearManufacturing(ManufacturingProcess):
    """Base class for gear manufacturing processes."""
    def __init__(self, name: str, chinese_name: str = "", **kwargs):
        super().__init__(name, "gear_manufacturing", chinese_name, **kwargs)

class GearHobbing(GearManufacturing):
    """Gear hobbing process."""
    def __init__(self, **kwargs):
        super().__init__("gear_hobbing", chinese_name="滚齿", **kwargs)

class GearShaping(GearManufacturing):
    """Gear shaping process."""
    def __init__(self, **kwargs):
        super().__init__("gear_shaping", chinese_name="插齿", **kwargs)

class GearShaving(GearManufacturing):
    """Gear shaving process."""
    def __init__(self, **kwargs):
        super().__init__("gear_shaving", chinese_name="剃齿", **kwargs)

class GearGrinding(GearManufacturing):
    """Gear grinding process."""
    def __init__(self, **kwargs):
        super().__init__("gear_grinding", chinese_name="磨齿", **kwargs)

class GearHoning(GearManufacturing):
    """Gear honing process."""
    def __init__(self, **kwargs):
        super().__init__("gear_honing", chinese_name="珩齿", **kwargs)

# =============================================================================
# Thread Manufacturing Processes
# =============================================================================

class ThreadManufacturing(ManufacturingProcess):
    """Base class for thread manufacturing processes."""
    def __init__(self, name: str, chinese_name: str = "", **kwargs):
        super().__init__(name, "thread_manufacturing", chinese_name, **kwargs)

class ThreadCutting(ThreadManufacturing):
    """Thread cutting process."""
    def __init__(self, thread_type: str = "external", **kwargs):
        super().__init__("thread_cutting", chinese_name="螺纹加工", **kwargs)
        self.thread_type = thread_type

class ThreadRolling(ThreadManufacturing):
    """Thread rolling process."""
    def __init__(self, **kwargs):
        super().__init__("thread_rolling", chinese_name="滚丝", **kwargs)

class ThreadGrinding(ThreadManufacturing):
    """Thread grinding process."""
    def __init__(self, **kwargs):
        super().__init__("thread_grinding", chinese_name="磨螺纹", **kwargs)

# Example usage and validation
if __name__ == "__main__":
    # Example: Create a typical machining scenario with English names
    titanium_alloy = Material("Ti-6Al-4V", "titanium_alloy", "aerospace_grade", chinese_name="钛合金")
    rough_turning = RoughTurning()
    lathe = Lathe("KBSZ_840", "KBSZ-840")
    carbide_tool = CarbideTool("carbide_turning_tool")
    spindle_speed = SpindleSpeed(800)
    feed_rate = FeedRate(0.2)
    
    # Create relations
    material_rel = MaterialRelation(Entity("titanium_part", chinese_name="钛合金零件"), titanium_alloy)
    equipment_rel = EquipmentUsageRelation(rough_turning, lathe)
    tool_rel = ToolUsageRelation(rough_turning, carbide_tool)
    spindle_rel = SpindleSpeedSettingRelation(rough_turning, spindle_speed)
    feed_rel = FeedRateSettingRelation(rough_turning, feed_rate)
    
    # Display information
    print("Manufacturing Code-Style Schema with Professional English Terminology")
    print("=" * 70)
    print(f"Material: {titanium_alloy.name} ({titanium_alloy.chinese_name})")
    print(f"Process: {rough_turning.name} ({rough_turning.chinese_name})")
    print(f"Equipment: {lathe.name} ({lathe.chinese_name})")
    print(f"Spindle Speed: {spindle_speed.value} {spindle_speed.unit}")
    print(f"Cutting Speed: {rough_turning.calculate_cutting_speed(50, spindle_speed.value):.2f} m/min")
    print(f"Machinability Index: {titanium_alloy.calculate_machinability_index()}")