### AK_Subject_One
- 该工具使用tesseract进行OCR识别，因此你需要将tesseract安装到te_exe或者手动更改tesseract路径
- 不过我有打包tesseract，貌似也不需要安装
- 默认模型供应商为Ollama，默认模型为qwen2.5-coder:7b，需要确保安装了ollama且有该模型
- OCRdebug功能
- 非必要组件折叠功能

#### Install
```text
git clone https://github.com/micr0softDrestlife/AK_Subject_One.git

pip install -r requirements.txt

python main.py
```

#### v2
- 完善了部分模型供应商
- 增加了修改模式
- 进行了页面美化
- 打包了相关的python库依赖