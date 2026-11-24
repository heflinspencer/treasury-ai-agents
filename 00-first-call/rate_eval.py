from dotenv import load_dotenv
from anthropic import Anthropic
from pydantic import BaseModel, Field

load_dotenv()
client = Anthropic()

class RateDecision(BaseModel):
    central_bank: str
    decision_date: str = Field(
        description="ISO format, YYYY-MM-DD. "
        "Read numeric dates as day/month/year.")
    new_rate_pct: float
    change_bp: int = Field(
        description="Signed. Negative for a cut.")
    votes_for: int | None = Field(
        description="Null if not stated.")
    votes_against: int | None = Field(
        description="Null if not stated.")

def extract(statement: str) -> RateDecision:
    response = client.messages.parse(
        model="claude-haiku-5-5",
        max_tokens=1024,
        output_format = RateDecision,
        messages = [
            {"role": "user",
             "content": f"Extract the decision:\n{statement}"}
        ],
    )
    return response.parsed_output

CASES = [
    {
        "name": "cut",
        "statement": (
            "The Monetary Policy Committee of the Bank "
            "of Northland voted 7-2 on 5 November 2026 "
            "to cut the policy rate by 25 basis points "
            "to 3.50%."
        ),
        "expected": {
            "decision_date": "2026-11-05",
            "new_rate_pct": 3.5,
            "change_bp": -25,
            "votes_for": 7,
            "votes_against": 2,
        },
    },
    {
        "name": "hold",
        "statement": (
            "The Bank of Northland's Monetary Policy Committee "
            "voted 8-1 on 17 December 2026 to leave the policy "
            "rate unchanged at 3.50%."
        ),
        "expected": {
            "decision_date": "2026-12-17",
            "new_rate_pct": 3.5,
            "change_bp": 0,
            "votes_for": 8,
            "votes_against": 1,
        },
    },
    {
        "name": "hike",
        "statement": (
            "On 4 February 2027 the Reserve Bank of Eastmark "
            "raised its cash rate by 50 basis points to 4.75%, by a "
            "vote of 5-4."
        ),
        "expected": {
            "decision_date": "2027-02-04",
            "new_rate_pct": 4.75,
            "change_bp": 50,
            "votes_for": 5,
            "votes_against": 4,
        },
    },
    {
        "name": "no_votes",
        "statement": (
            "The Central Bank of Westria lowered its key rate by 25 "
            "basis points to 2.00% on 12 March 2027."
        ),
        "expected": {
            "decision_date": "2027-03-12",
            "new_rate_pct": 2.0,
            "change_bp": -25,
            "votes_for": None,
            "votes_against": None,
        },
    },
    {
        "name": "slash_date",
        "statement": (
            "At its meeting on 5/11/2026, the Bank of Northland cut "
            "the policy rate by 25 basis points to 3.50% in a 7-2 vote."
        ),
        "expected": {
            "decision_date": "2026-11-05",
            "new_rate_pct": 3.5,
            "change_bp": -25,
            "votes_for": 7,
            "votes_against": 2,
        },
    },
]

failures = 0
for case in CASES:
    d = extract(case["statement"])
    for field, want in case["expected"].items():
        got = getattr(d, field)
        ok = got == want
        if not ok:
            failures += 1
        mark = "PASS" if ok else "FAIL"
        print(f"{mark} {case['name']}.{field}: "
              f"got {got!r}, want {want!r}")
        
print(f"{failures} failures")