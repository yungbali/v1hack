# How to Use the Debt Restructuring Simulator

## Overview

The Country Scenario Simulator allows you to model different debt restructuring options and see their immediate impact on fiscal space and social spending.

## What You're Seeing

### Current State (Left Side - Gray Card)
Shows the baseline metrics for the selected country:
- **Annual debt service**: Current yearly debt payments
- **Debt-to-GDP ratio**: Total debt as % of GDP
- **Fiscal space available**: Revenue minus debt service

### Reform Scenario (Right Side - Green Card)
Shows projected metrics after applying reforms:
- **New annual debt service**: Projected yearly payments
- **Debt-to-GDP (Year 5)**: Projected ratio after 5 years
- **Fiscal space freed**: Annual savings from restructuring
- **Opportunity cost**: What the freed funds could buy

## How to Use the Sliders

### 1. Interest Rate Reduction (0-5%)
**What it does**: Reduces the interest rate on the debt

**Example**: 
- Current rate: 5%
- Reduction: 2%
- New rate: 3%

**Impact**: Lower interest = lower annual payments

**Try**: Move slider to 2% and watch fiscal space increase

---

### 2. Maturity Extension (0-10 years)
**What it does**: Extends the repayment period

**Example**:
- Current maturity: 10 years
- Extension: 5 years
- New maturity: 15 years

**Impact**: Longer period = payments spread over more years = lower annual payment

**Try**: Move slider to 5 years and see the effect

---

### 3. Principal Haircut (0-50%)
**What it does**: Reduces the total amount owed

**Example**:
- Current debt: $100B
- Haircut: 20%
- New debt: $80B

**Impact**: Less debt = lower payments

**Try**: Move slider to 20% and observe the savings

---

## Understanding the Results

### When Sliders are at Zero
- **Fiscal space freed**: $0.00B ✓ This is correct!
- **New payment**: Should equal current payment
- **No reforms = No savings**

### When You Apply Reforms
Watch these metrics change:
1. **Instant Impact** (white box): Shows immediate annual savings
2. **New annual debt service**: Should be lower than current
3. **Fiscal space freed**: Shows how much money is available
4. **Opportunity cost cards**: Shows what freed funds could buy

## Example Scenarios to Try

### Scenario 1: Modest Reform
- Interest reduction: 1%
- Maturity extension: 3 years
- Haircut: 0%

**Expected**: Moderate fiscal space freed

### Scenario 2: Aggressive Reform
- Interest reduction: 3%
- Maturity extension: 7 years
- Haircut: 30%

**Expected**: Significant fiscal space freed

### Scenario 3: Interest-Only Relief
- Interest reduction: 5%
- Maturity extension: 0 years
- Haircut: 0%

**Expected**: Lower payments without changing debt amount

### Scenario 4: Maturity-Only Extension
- Interest reduction: 0%
- Maturity extension: 10 years
- Haircut: 0%

**Expected**: Payments spread over longer period

## Interpreting Opportunity Costs

The simulator shows what freed fiscal space could fund:

**Example**: If fiscal space freed = $1B annually

- **Schools**: ~1,142 primary schools ($875k each)
- **Hospitals**: ~86 district hospitals ($11.6M each)
- **Vaccines**: ~20 million doses ($50 each)
- **Teachers**: ~125,000 teachers ($8k salary each)

This helps communicate the human impact of debt relief.

## Tips for Best Results

### 1. Start with One Slider
- Move just one slider first
- Observe the impact
- Then try combinations

### 2. Compare Scenarios
- Try different combinations
- Note which has the biggest impact
- Consider political feasibility

### 3. Realistic Scenarios
- Interest reductions: 1-3% is realistic
- Maturity extensions: 5-10 years is common
- Haircuts: 20-40% in severe cases

### 4. Consider Creditor Mix
- Check the Creditor Mix page first
- Multilateral debt rarely gets haircuts
- Commercial debt is easier to restructure
- Bilateral debt depends on politics

## Common Questions

### Q: Why does "New annual debt service" seem high when sliders are at zero?
**A**: This is because we're using estimated default interest rates and maturities. The actual current debt service (shown in the Current State card) is the accurate baseline. When you apply reforms, the calculations show the change from this baseline.

### Q: What's a realistic restructuring scenario?
**A**: Most real-world restructurings combine:
- 1-2% interest reduction
- 5-7 year maturity extension
- 10-30% haircut (in severe cases)

### Q: Can I save these scenarios?
**A**: Currently no, but you can:
- Take screenshots
- Note the slider values
- Record the fiscal space freed

### Q: Why doesn't the simulator show my country?
**A**: Check if:
- Data exists for your country
- Filters aren't excluding it
- Country is in the dataset

## Technical Notes

### Calculation Method
The simulator uses the standard annuity formula:
```
Payment = Principal × (r × (1 + r)^n) / ((1 + r)^n - 1)
```

Where:
- Principal = Total debt (after haircut)
- r = Interest rate (after reduction)
- n = Maturity (after extension)

### Assumptions
- Constant interest rate over the period
- Equal annual payments (annuity)
- No additional borrowing
- GDP growth not modeled (for simplicity)

### Limitations
- Simplified model (real restructurings are more complex)
- Doesn't account for creditor negotiations
- Doesn't model economic growth effects
- Assumes all debt can be restructured equally

## Next Steps

After using the simulator:

1. **Explore Creditor Mix page**: Understand who holds the debt
2. **Check Social Spending page**: See current trade-offs
3. **Visit Country Deep Dive**: See historical trends
4. **Compare countries**: Try different countries in the simulator

## Need Help?

If the simulator isn't working:
1. Run: `python diagnose_simulator.py`
2. Check for error messages in the app
3. Verify data is loaded
4. Try refreshing the page

---

**Remember**: The simulator is a tool for exploration and education. Real debt restructuring involves complex negotiations with multiple creditors and political considerations.
