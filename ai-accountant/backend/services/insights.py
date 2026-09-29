import pandas as pd

async def generate_insights(df: pd.DataFrame):
    """Generate spending insights and recommendations."""
    if df.empty:
        return {
            "summary": ["No transactions to analyze"],
            "budget_tip": "Start tracking your expenses to get personalized insights.",
            "tax_hint": "Keep receipts for all business-related expenses."
        }
    
    # Calculate spending by category
    category_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    total_spending = df["amount"].sum()
    
    # Generate summary
    summary_lines = [
        f"Total spending: ${total_spending:.2f}",
        f"Top category: {category_totals.index[0]} (${category_totals.iloc[0]:.2f})",
        f"Number of transactions: {len(df)}"
    ]
    
    # Add top 3 categories
    if len(category_totals) >= 3:
        top_3 = category_totals.head(3)
        summary_lines.append(f"Top 3 categories: {', '.join([f'{cat} (${amt:.2f})' for cat, amt in top_3.items()])}")
    
    # Generate budget tip based on spending patterns
    if "Groceries" in category_totals and category_totals["Groceries"] > total_spending * 0.3:
        budget_tip = "Consider meal planning to reduce grocery spending."
    elif "Transport" in category_totals and category_totals["Transport"] > total_spending * 0.2:
        budget_tip = "Look into carpooling or public transport to reduce transport costs."
    elif "Dining" in category_totals and category_totals["Dining"] > total_spending * 0.25:
        budget_tip = "Try cooking more meals at home to reduce dining expenses."
    else:
        budget_tip = "Track your spending patterns to identify areas for improvement."
    
    # Generate tax hint
    business_categories = ["Health/Pharmacy", "Utilities", "Transport"]
    business_spending = sum(category_totals.get(cat, 0) for cat in business_categories)
    
    if business_spending > 0:
        tax_hint = f"Keep receipts for ${business_spending:.2f} in potentially deductible expenses (Health, Utilities, Transport)."
    else:
        tax_hint = "Save receipts for any business-related purchases for potential tax deductions."
    
    return {
        "summary": summary_lines,
        "budget_tip": budget_tip,
        "tax_hint": tax_hint
    }
