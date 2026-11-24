from dotenv import load_dotenv
from anthropic import Anthropic
from pydantic import BaseModel, Field

load_dotenv()
client = Anthropic()

STATEMENT = (
    "The Monetary Policy Committee of the Bank of "
    "Northland voted 7-2 on 5 November 2026 to cut "
    "the policy rate by 25 basis points to 3.50%."
)

class RateDecision(BaseModel):
    central_bank: str
    decision_date: str = Field(
        description="ISO format, YYYY-MM-DD")
    new_rate_pct: float
    change_bp: int = Field(
        description="Signed. Negative for a cut.")
    votes_for: int
    votes_against: int

response = client.messages.parse(
    model="claude-haiku-5-5",
    max_tokens=1024,
    output_format=RateDecision,
    messages=[
        {"role": "user",
         "content": f"Extract the decision:\n{STATEMENT}"}
    ],
)

d = response.parsed_output
print(d)

assert d.change_bp == -25
assert d.new_rate_pct == 3.5
assert d.decision_date == "2026-11-05"
assert (d.votes_for, d.votes_against) == (7,2)
print("All checks passed")
print(response.usage)

