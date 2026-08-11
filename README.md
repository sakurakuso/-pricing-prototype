快速说明（本地运行）
1) 后端 (端口 8000)
   - 进入 backend 目录
   - python -m venv .venv
   - 在 PowerShell 中激活虚拟环境： .\.venv\Scripts\Activate.ps1
   - pip install -r requirements.txt
   - uvicorn main:app --reload --port 8000

2) 前端 (端口 3000)
   - 进入 frontend 目录
   - npm install
   - npm start
   前端已在 package.json 中配置了 "proxy": "http://localhost:8000" ，开发时会把 /api 请求代理到后端。

示例输入（可在前端填写）：
 - 城市: 北京
 - 商品类别: 餐饮
 - 当前售价: 20
 - 单位进价: 10
 - 日销量估计: 50
 - 日租金: 200
 - 日人工: 100
 - 其他固定成本(每日): 0
 - 价格弹性（可选）: 不填则使用类别默认

说明
- 模型：使用线性需求 Q(p)=a - b p，b 由价格弹性 ε 与 (p0,Q0) 反推： b = -ε * Q0 / p0；a = Q0 + b*p0。
- 在此基础上计算最优价格 p* = (a + b c) / (2 b)（线性需求下的解析解）。
- 输出当前利润、情景（-10%,-5%,0,5%,10%,15%）以及 p* 与对应利润，给出简单推荐。
