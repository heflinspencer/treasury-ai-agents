# Rate Decision Extraction

This script takes short synthetic central bank rate-decision statements and feeds them into the Claude Haiku 5.5 model, getting a structured output of what happened in the meeting.

## What It Does

The input is a sentence describing what the bank decided during the meeting and what day the meeting occurred. The output is structured with 6 different fields: 
- `central_bank` = the central bank making the decision 
- `decision_date` = date the meeting happened
- `new_rate_pct` = new rate the committee decided on 
- `change_bp` = the difference between the new rate and the old rate in basis points, negative for a cut
- `votes_for` = how many people voted for the decision
- `votes_against` = how many people voted against the decision

The evaluation checks 5 of the 6 fields.
`central_bank` is extracted but not yet tested.

## How To Run

Requires Python 3.10 or newer and a Claude API key.

```bash
git clone https://github.com/heflinspencer/treasury-ai-agents.git
cd treasury-ai-agents
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your API key to `.env`, then:

```bash
python 00-first-call/first_call.py
python 00-first-call/rate_eval.py
```

The evaluation makes five API calls and prints
PASS or FAIL for each field.

## Results

- **First run:** 22 of 25 (5 statements against 5 checked fields). The model invented 0-0 votes when none were stated and read 5/11 as 11 May.
- **After fixes:** 25 of 25, over 3 runs

## What I Changed and Why

**The 0-0 votes problem:**
I made a type change because the schema required an integer and had no way to say "not stated". The model used 0 as a best guess.

Before: 
```python
votes_for: int
```


After: 
```python
votes_for: int | None = Field(
        description="Null if not stated.")
```

**The misread date problem:**
I added a rule to read numeric dates as day/month/year.

## Limitations

1. The evaluation set is tiny, only 5, tuned to its own test. I edited the prompt until these 5 passed and there are no held-out cases, so 25 out of 25 is the best case.
2. The inputs are synthetic and written by me, not real central bank statements.
3. The date rule is a hard-coded assumption. It would misread a US bank's numeric dates.
4. The schema can't represent two rates changing at once, or a rate range, like the Fed's target band.