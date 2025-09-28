import yaml

class RuleEngine:
    def __init__(self, path: str = "rules/rules.yaml"):
        self.path = path
        self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.rules = yaml.safe_load(f) or []
        except FileNotFoundError:
            self.rules = []

    def apply(self, case: dict):
        loc = {"case": case}
        actions = []
        for r in self.rules:
            try:
                if eval(r.get("when", "False"), {}, loc):
                    actions.extend(r.get("actions", []))
            except Exception:
                continue
        return actions

def exec_actions(actions, obj):
    for act in actions:
        if act.startswith("set_priority("):
            val = act.split("set_priority(")[1].rstrip(")").strip("'\"")
            obj.priority = val
        elif act.startswith("assign("):
            val = act.split("assign(")[1].rstrip(")").strip("'\"")
            obj.owner = val
        elif act.startswith("update_status("):
            val = act.split("update_status(")[1].rstrip(")").strip("'\"")
            obj.status = val
    return obj
