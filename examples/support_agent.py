"""A tiny fake support agent used by the example test. No LLM needed."""


def lookup_order(order_id: str) -> dict:
    return {"order_id": order_id, "status": "delivered", "amount": 499}


def issue_refund(order_id: str, amount: int) -> dict:
    return {"refunded": True, "order_id": order_id, "amount": amount}


def support_agent(prompt: str, rec):
    rec.log_llm(tokens=300, cost_usd=0.002, model="fake-model")
    order = rec.call_tool("lookup_order", order_id="123")
    rec.log_llm(tokens=250, cost_usd=0.002, model="fake-model")
    rec.call_tool("issue_refund", order_id="123", amount=order["amount"])
    return "Your refund has been issued."


TOOLS = {"lookup_order": lookup_order, "issue_refund": issue_refund}
