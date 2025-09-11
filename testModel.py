from transformers import AutoModelForCausalLM, AutoTokenizer

# 设置模型路径
model_path = "/root/autodl-tmp/models"

# 尝试加载分词器
try:
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    print(" 分词器加载成功")
except Exception as e:
    print(f" 分词器加载失败: {e}")

# 尝试加载模型
try:
    model = AutoModelForCausalLM.from_pretrained(
        model_path, 
        device_map="auto",  # 自动选择设备
        torch_dtype="auto"  # 自动选择数据类型
    )
    print(" 模型加载成功")
except Exception as e:
    print(f" 模型加载失败: {e}")

# 简单测试模型
if 'model' in locals() and 'tokenizer' in locals():
    prompt = "Hello, how are you?"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    try:
        outputs = model.generate(**inputs, max_length=100)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("\n模型测试输出:")
        print(response)
        print("\n 模型可以正常生成输出")
    except Exception as e:
        print(f" 模型生成测试失败: {e}")
