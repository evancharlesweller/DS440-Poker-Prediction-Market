from typing import List, Optional, Dict

from market.pricing import price_contract


def contract_decimal_odds(contract) -> float:
    if contract.price <= 0:
        return 0.0
    return round(1.0 / contract.price, 2)


def rank_contracts(contracts, state) -> List[dict]:
    ranked = []
    for contract in contracts:
        probability = price_contract(contract, state)
        odds = contract_decimal_odds(contract)
        edge = round(probability - contract.price, 6)
        ranked.append({
            "contract": contract,
            "probability": probability,
            "odds": odds,
            "edge": edge,
        })

    ranked.sort(
        key=lambda item: (
            item["edge"],
            item["probability"],
            -item["odds"],
            item["contract"].description,
        ),
        reverse=True,
    )
    return ranked


def _item_payload(item: Optional[Dict]) -> Optional[Dict]:
    if not item:
        return None
    contract = item["contract"]
    return {
        "description": contract.description,
        "probability": item["probability"],
        "odds": item["odds"],
        "edge": item["edge"],
    }


def recommendation_payload(contracts, state) -> Dict:
    if state is None:
        return {"kind": "text", "text": "Start a hand first. I need a live game state to recommend bets."}
    if not contracts:
        return {"kind": "text", "text": "There are no open contracts available right now."}

    ranked = rank_contracts(contracts, state)
    if not ranked:
        return {"kind": "text", "text": "There are no open contracts available right now."}

    safe = max(ranked, key=lambda item: (item["probability"], -item["odds"]))
    upside = max(ranked, key=lambda item: (item["odds"], -item["probability"]))
    balanced = ranked[0]
    positive_edges = [item for item in ranked if item["edge"] > 0.0001]

    intro = (
        "There is a real pricing edge right now, so the best values are the contracts with the strongest gap between current price and true hit probability."
        if positive_edges else
        "Under pure probability pricing, nothing looks meaningfully underpriced right now, so the best choice depends more on whether you want safety or upside."
    )

    return {
        "kind": "recommendation",
        "intro": intro,
        "safe": _item_payload(safe),
        "balanced": _item_payload(balanced),
        "upside": _item_payload(upside),
    }


def highest_payout_payload(contracts, state) -> Dict:
    if state is None:
        return {"kind": "text", "text": "Start a hand first so I can compare live payouts."}
    if not contracts:
        return {"kind": "text", "text": "There are no open contracts right now."}
    ranked = rank_contracts(contracts, state)
    if not ranked:
        return {"kind": "text", "text": "There are no open contracts right now."}
    top = max(ranked, key=lambda item: (item["odds"], -item["probability"]))
    return {
        "kind": "highest_payout",
        "top": _item_payload(top),
    }
