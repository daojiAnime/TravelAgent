# 旅行规划工具

## 使用说明

### 环境变量配置

```bash
# 生成 .env 文件
cp .env.sample .env

# 编辑 .env 文件
# vim .env
```

### 安装依赖
```bash
# uv 安装 https://docs.astral.sh/uv/
uv venv -p 3.12

# 安装依赖
uv sync
```

### 运行

```bash
uv run main.py
```