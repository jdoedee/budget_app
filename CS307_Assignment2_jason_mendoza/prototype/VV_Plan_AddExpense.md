# Verification & Validation (V&V) Plan – Add Expense Feature

## Feature Under Test
Add Expense: User submits an expense entry (amount, category, date, optional note).  
System validates input, saves the transaction, and updates monthly totals used in reports.

## Scope
- Functional correctness (validation + persistence + totals update)
- Quality attribute focus: reliability/maintainability (clear errors, consistent rules, modular design)

## Test Cases

### TC-1: Valid Expense Entry Saves Successfully (Functional)
**Preconditions:** User exists; data store available.  
**Steps:**  
1) Enter amount `45.90`  
2) Enter category `Groceries`  
3) Enter date `2026-02-10`  
4) Enter note `Food4Less run`  
5) Click/submit “Save Expense”  
**Expected Results:**  
- Transaction ID generated  
- Expense saved to repository  
- Updated totals reflect new expense  
- Confirmation message displayed

### TC-2: Invalid Amount is Rejected (Reliability)
**Preconditions:** User exists.  
**Steps:**  
1) Enter amount `-5` (or `abc`)  
2) Enter valid category and date  
3) Submit  
**Expected Results:**  
- Clear validation error returned  
- No transaction saved  
- Totals remain unchanged

### TC-3: Blank Category is Rejected (Reliability/Maintainability)
**Preconditions:** User exists.  
**Steps:**  
1) Enter amount `10.00`  
2) Leave category blank  
3) Enter valid date  
4) Submit  
**Expected Results:**  
- Clear validation error returned  
- No transaction saved  
- Consistent error messaging (same structure each time)

## Test Evidence
Record results in a small table (Pass/Fail, notes).  
Optional: attach console output or screenshot of the confirmation/error.
