from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List
import math

app = FastAPI(title="Pricing Analyzer Prototype")

class AnalyzeRequest(BaseModel):
    city: Optional[str] = ""
    address: Optional[str] = ""
    category: Optional[str] = Field("其他", description="商品类别，用于默认弹性")
    current_price: float
    unit_cost: float
    daily_sales: float
    daily_rent: float = 0.0
    daily_labor: float = 0.0
    other_fixed_daily: float = 0.0
    elasticity: Optional[float] = None  # price elasticity (negative)

class Scenario(BaseModel):
    label: str
    price: float
    est_sales: float
    profit: float

class AnalyzeResponse(BaseModel):
    used_elasticity: float
    current_profit: float
    scenarios: List[Scenario]
    optimal_price: Optional[float]
    optimal_profit: Optional[float]
    recommendation: str

DEFAULT_ELASTICITIES = {
    "生鲜": -0.6,
    "快消": -0.8,
    "餐饮": -0.7,
    "服装/非必需": -1.2,
    "其他": -0.8,
}

def compute_linear_params(p0, Q0, eps):
    # b = -eps * Q0 / p0  (eps is negative, so b>0)
    b = -eps * Q0 / p0
    a = Q0 + b * p0
    return a, b

@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    p0 = req.current_price
    c = req.unit_cost
    Q0 = req.daily_sales
    F = req.daily_rent + req.daily_labor + req.other_fixed_daily

    eps = req.elasticity if req.elasticity is not None else DEFAULT_ELASTICITIES.get(req.category, DEFAULT_ELASTICITIES["其他"])
    used_eps = eps

    # Guardrails
    if p0 <= 0 or Q0 <= 0:
        return AnalyzeResponse(
            used_elasticity=used_eps,
            current_profit=0.0,
            scenarios=[],
            optimal_price=None,
            optimal_profit=None,
            recommendation="请填写正数的当前售价和日销量。"
        )

    a, b = compute_linear_params(p0, Q0, eps)

    def profit_at(price):
        q = max(a - b * price, 0.0)
        return q * (price - c) - F, q

    current_profit, _ = profit_at(p0)

    scenarios = []
    for pct in [-10, -5, 0, 5, 10, 15]:
        price = round(p0 * (1 + pct/100), 4)
        profit, q = profit_at(price)
        scenarios.append(Scenario(label=f"{pct:+}%", price=price, est_sales=round(q,4), profit=round(profit,4)))

    # compute optimal price for linear demand
    # p* = (a + b*c) / (2*b)
    try:
        p_star = (a + b * c) / (2 * b)
        if not math.isfinite(p_star) or p_star <= 0:
            p_star = None
            profit_star = None
        else:
            profit_star, q_star = profit_at(p_star)
            profit_star = round(profit_star,4)
            p_star = round(p_star,4)
    except Exception:
        p_star = None
        profit_star = None

    # recommendation logic (simple)
    rec = "保持当前价格"
    if p_star is not None and profit_star is not None:
        if profit_star > current_profit:
            # sanity: only recommend if p_star not absurdly far (e.g., within 2x)
            if 0.5 * p0 <= p_star <= 2.0 * p0:
                rec = f"建议将价格调整为 {p_star} 元（模型预计日净利 {profit_star} 元，高于当前 {round(current_profit,4)} 元）"
            else:
                rec = f"模型给出最优价格 {p_star} 元，但幅度较大，建议做小规模 A/B 测试或收集更多数据再调整。"
        else:
            rec = "当前价格已接近模型下的利润最优点，或提高价格会使利润下降。建议维持或小幅试验。"

    return AnalyzeResponse(
        used_elasticity=used_eps,
        current_profit=round(current_profit,4),
        scenarios=scenarios,
        optimal_price=p_star,
        optimal_profit=profit_star,
        recommendation=rec
    )
