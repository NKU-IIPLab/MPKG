#!/usr/bin/env python3
"""
Code-Style制造业领域知识表示使用示例
演示如何从JSON定义创建和使用制造业领域的类
"""
import json
from typing import Union

class ManufacturingKnowledgeSystem:
    """制造业知识系统，基于Code-Style架构"""
    
    def __init__(self):
        self.entity_classes = {}
        self.relation_classes = {}
        self.event_classes = {}
        self.load_class_definitions()
    
    def load_class_definitions(self):
        """从JSON文件加载类定义"""
        try:
            # 加载实体类定义
            with open('schemas/code_style/entity_class_defs.json', 'r', encoding='utf-8') as f:
                self.entity_defs = json.load(f)
            
            # 加载关系类定义  
            with open('schemas/code_style/relation_class_defs.json', 'r', encoding='utf-8') as f:
                self.relation_defs = json.load(f)
                
            # 加载事件类定义
            with open('schemas/code_style/event_class_defs.json', 'r', encoding='utf-8') as f:
                self.event_defs = json.load(f)
                
            print("✓ 成功加载所有类定义文件")
            print(f"  - 实体类: {len(self.entity_defs)} 个")
            print(f"  - 关系类: {len(self.relation_defs)} 个") 
            print(f"  - 事件类: {len(self.event_defs)} 个")
            
        except Exception as e:
            print(f"❌ 加载类定义失败: {e}")
    
    def create_entity_classes(self):
        """动态创建实体类"""
        # 首先创建基础Entity类
        exec(self.entity_defs["Entity"], globals())
        
        # 创建ProcessParameter基类
        exec(self.entity_defs["ProcessParameter"], globals())
        
        # 创建其他基础类
        for base_class in ["Equipment", "CuttingTool", "Material", "MachiningProcess"]:
            if base_class in self.entity_defs:
                exec(self.entity_defs[base_class], globals())
        
        # 创建具体类
        for class_name, class_def in self.entity_defs.items():
            if class_name not in ["Entity", "ProcessParameter", "Equipment", "CuttingTool", "Material", "MachiningProcess"]:
                try:
                    exec(class_def, globals())
                    self.entity_classes[class_name] = eval(class_name)
                except Exception as e:
                    print(f"警告: 创建类 {class_name} 失败: {e}")
        
        print(f"✓ 成功创建 {len(self.entity_classes)} 个实体类")
    
    def demonstrate_usage(self):
        """演示制造业知识表示的使用"""
        print("\n=== Code-Style制造业知识表示演示 ===")
        
        # 创建主轴转速参数
        spindle_speed = SpindleSpeed(800, "rpm")
        print(f"主轴转速: {spindle_speed.value}{spindle_speed.unit} (中文: {spindle_speed.chinese_name})")
        
        # 创建进给量参数
        feed_rate = FeedRate(0.2, "mm/r")
        print(f"进给量: {feed_rate.value}{feed_rate.unit} (中文: {feed_rate.chinese_name})")
        
        # 创建车床设备
        lathe = Lathe("KBSZ车床840", "KBSZ-840")
        print(f"设备: {lathe.name}, 型号: {lathe.model} (中文: {lathe.chinese_name})")
        
        # 创建钛合金材料
        titanium = TitaniumAlloy("Ti-6Al-4V")
        print(f"材料: {titanium.name}, 成分: {titanium.composition} (中文: {titanium.chinese_name})")
        
        # 创建车削工艺
        turning = Turning()
        print(f"工艺: {turning.name} (中文: {turning.chinese_name})")
        
        # 演示切削速度计算
        cutting_speed = spindle_speed.calculate_cutting_speed(50.0)  # 直径50mm
        if cutting_speed:
            print(f"计算的切削速度: {cutting_speed:.2f} m/min")
    
    def show_class_hierarchy(self):
        """显示类层次结构信息"""
        print("\n=== 制造业领域类层次结构 ===")
        
        # 统计各类别的数量
        process_classes = [name for name in self.entity_defs.keys() 
                          if 'Process' in name or name in ['Turning', 'Milling', 'Grinding', 'Drilling']]
        equipment_classes = [name for name in self.entity_defs.keys() 
                            if 'Machine' in name or name == 'Lathe']
        parameter_classes = [name for name in self.entity_defs.keys() 
                            if 'Speed' in name or 'Rate' in name or 'Depth' in name]
        
        print(f"加工工艺类: {len(process_classes)} 个")
        print(f"设备类: {len(equipment_classes)} 个") 
        print(f"参数类: {len(parameter_classes)} 个")
        
        # 显示关系类型
        print(f"\n关系类型: {len(self.relation_defs)} 个")
        for rel_name in list(self.relation_defs.keys())[:5]:  # 显示前5个
            print(f"  - {rel_name}")
        
    def generate_knowledge_graph_example(self):
        """生成知识图谱示例"""
        print("\n=== 制造业知识图谱示例 ===")
        
        # 模拟一个完整的加工场景
        scenario = {
            "工艺": "钛合金零件车削加工",
            "设备": "KBSZ车床840",
            "刀具": "CBN刀具",
            "材料": "Ti-6Al-4V钛合金",
            "参数": {
                "主轴转速": "800rpm",
                "进给量": "0.2mm/r",
                "切削深度": "1.5mm",
                "表面粗糙度要求": "Ra1.6"
            },
            "操作人员": "刘思嫄",
            "质量检验": "尺寸检验"
        }
        
        print("加工场景知识表示:")
        for key, value in scenario.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  - {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")

def main():
    """主函数"""
    print("Code-Style制造业领域知识表示系统")
    print("=" * 50)
    
    # 创建知识系统
    mfg_system = ManufacturingKnowledgeSystem()
    
    # 创建实体类
    mfg_system.create_entity_classes()
    
    # 演示使用
    mfg_system.demonstrate_usage()
    
    # 显示类层次结构
    mfg_system.show_class_hierarchy()
    
    # 生成知识图谱示例
    mfg_system.generate_knowledge_graph_example()
    
    print("\n" + "=" * 50)
    print("✓ Code-Style制造业知识表示系统演示完成")

if __name__ == "__main__":
    main()