import os
import json
from pathlib import Path
from typing import Dict, Any, List

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"

class TaxRuleEngine:
    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_supported_years(cls) -> List[str]:
        cls._ensure_loaded()
        return sorted(list(cls._cache.keys()), reverse=True)

    @classmethod
    def get_rules(cls, assessment_year: str = "2025-26") -> Dict[str, Any]:
        cls._ensure_loaded()
        if assessment_year not in cls._cache:
            # Fallback to nearest default
            if "2025-26" in cls._cache:
                return cls._cache["2025-26"]
            elif cls._cache:
                return next(iter(cls._cache.values()))
            raise ValueError(f"No tax rules configured for Assessment Year {assessment_year}")
        return cls._cache[assessment_year]

    @classmethod
    def reload_rules(cls):
        cls._cache.clear()
        cls._ensure_loaded()

    @classmethod
    def _ensure_loaded(cls):
        if not cls._cache:
            if not RULES_DIR.exists():
                RULES_DIR.mkdir(parents=True, exist_ok=True)
            for file_path in RULES_DIR.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        ay = data.get("assessment_year")
                        if ay:
                            cls._cache[ay] = data
                except Exception as e:
                    print(f"Error loading tax rule {file_path}: {e}")

rule_engine = TaxRuleEngine()

