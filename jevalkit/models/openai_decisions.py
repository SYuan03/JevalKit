"""Native OpenAI Decisions transport and typed response conversion."""

from ._http import HttpDecisionModel, api_state
from ..io import dumps
from ..schema import Unsupported


class OpenAIDecisions(HttpDecisionModel):
    """Contract: https://developers.openai.com/api/reference/resources/decisions/methods/create"""

    def __init__(
        self,
        model="gpt-6-luna",
        endpoint="https://api.openai.com/v1/decisions",
        token_env="OPENAI_API_KEY",
        **options,
    ):
        super().__init__(endpoint=endpoint, model=model, token_env=token_env, **options)

    def build_payload(self, request, media_root=None):
        questions = []
        for qid, q in request["questions"].items():
            kind = q["type"]
            native = {
                "name": qid,
                "type": "predicate" if kind == "noul" else kind,
                "instructions": q["instructions"],
            }
            if kind == "choice":
                if len(q["criteria"]) > 255:
                    raise Unsupported("OpenAI Decisions permits at most 255 choices")
                native["choices"] = [
                    {
                        "value": key,
                        "description": (
                            value if isinstance(value, str) else key if value is None else dumps(value)
                        ),
                    }
                    for key, value in q["criteria"].items()
                ]
            elif kind == "score":
                native["levels"] = [
                    {"label": str(i), "description": value if isinstance(value, str) else dumps(value)}
                    for i, value in enumerate(q["criteria"])
                ]
            elif q.get("criteria"):
                native["instructions"] += (
                    "\nTrue criterion: "
                    + str(q["criteria"]["true"])
                    + "\nFalse criterion: "
                    + str(q["criteria"]["false"])
                )
            questions.append(native)
        if not 1 <= len(questions) <= 200:
            raise Unsupported("OpenAI Decisions requires 1–200 questions per request")
        return {
            "model": self.model,
            "input": api_state(request["state"], media_root, openai=True),
            "questions": questions,
        }

    @staticmethod
    def convert_response(response, questions):
        native = response["answers"]
        if not isinstance(native, list) or len(native) != len(questions):
            raise ValueError("OpenAI answer count mismatch")
        answers = {}
        for (qid, q), answer in zip(questions.items(), native):
            if answer.get("name") != qid or qid in answers:
                raise ValueError("OpenAI question name/order mismatch")
            if answer["type"] == "refusal":
                answers[qid] = {"type": "refusal"}
            elif q["type"] == "noul" and answer["type"] == "predicate":
                answers[qid] = {"type": "noul", "noul": answer["probability"]}
            elif answer["type"] == q["type"]:
                entries = answer["probabilities"]
                keys = [str(item["value"]) for item in entries]
                if len(set(keys)) != len(keys):
                    raise ValueError("Duplicate OpenAI probability values")
                answers[qid] = {
                    "type": q["type"],
                    "probabilities": dict(zip(keys, [p["probability"] for p in entries])),
                }
            else:
                raise ValueError("OpenAI answer type mismatch")
        return {"answers": answers, "usage": response.get("usage", {}), "model": response.get("model")}

    def predict(self, request, *, media_root=None, assets=None):
        payload = self.build_payload(request, media_root)
        return self.convert_response(self.post(payload), request["questions"])
