# Business Analyst System - Demo Script

**Target Audience:** Non-technical local shop owners  
**Duration:** 5-7 minutes  
**Format:** Screen-share with Streamlit app

---

## 1. Opening (30-45 seconds)

**What to say:**

"Hi, I want to show you something that might save you time and help you catch problems before they cost you sales.

This is a weekly business check-up tool for small retail shops. It looks at your inventory and sales data and tells you what needs attention—like products that might run out of stock.

Here's what I like about it: you don't need to log in every day, you don't need to learn a dashboard, and you don't need to give us access to your systems. You just upload a simple spreadsheet once a week, and it gives you a plain-English report.

Let me show you how it works."

---

## 2. Data Explanation (1 minute)

**What to say:**

"First, let's talk about the data. You need one spreadsheet with two things in it:

**One:** Your inventory snapshot—what you had in stock on a specific date. Like, 'On December 1st, I had 150 widgets.'

**Two:** Your daily sales after that date. Like, 'On December 2nd, I sold 3 widgets. On December 3rd, I sold 5 widgets.'

That's it. No customer names, no credit card numbers, no personal information. Just product names, quantities, and sales dates.

The system uses this to figure out how fast things are selling and when you might run out. If you don't have sales data, it still works—it just uses industry estimates, which are less precise but still useful.

**Pause and ask:** "Does this sound like data you could pull together? Most shops can export this from their point-of-sale system or even just track it in a spreadsheet."

---

## 3. Live Walkthrough (2-3 minutes)

**What to do and say:**

### Upload the CSV
"Let me upload a sample file... [Upload `sample_unified_data.csv`] ...Okay, I'll select 'retail' as the business type and enter a business name... Now I'll click 'Run Business Check-Up'."

### Executive Summary
"Here's what it found. [Point to summary metrics] The report shows how many items need immediate attention versus things to just keep an eye on.

The executive summary at the top tells you right away: 'What needs attention this week.' No scrolling, no hunting—just the most urgent items."

### Immediate Attention Section
"Let's look at the 'Immediate attention' section. [Expand the first insight]

This says 'Stock-Out Risk: 2 products need immediate attention.' 

It lists the products by name and tells you when they might run out. Notice it says 'at the current rate of sales'—that's important. It's not predicting the future, it's saying 'if sales continue like they have been, this is when you'll run out.'

Then it explains the business impact: 'This could result in missed sales and customer dissatisfaction.' That's the kind of thing a human analyst would tell you."

### Action Needed Soon Section
"Below that, there's 'Action needed soon'—products that aren't urgent this week but should be on your reorder list soon.

And then 'Monitor'—things to keep an eye on but don't need action right now."

### Recommendations
"At the bottom, it gives you specific recommendations: 'Prioritize reordering items that may run out this week at the current rate of sales.'

These aren't generic tips—they're based on what it found in your data."

**Pause and ask:** "Does this format make sense? Is this the kind of information you'd want to see?"

---

## 4. Interpretation (1-2 minutes)

**What to say:**

"Let me explain why a product gets flagged. [Point to a specific product in the report]

This product, Widget A, has 150 units in stock. Over the past week, it's been selling about 4 units per day on average. So 150 divided by 4 is about 37 days—but wait, that's not right.

Actually, the system looks at recent sales. If sales have been picking up, it uses that trend. So if it's been selling 5 units a day recently, that's 30 days of stock. But if it's a top seller—meaning it's one of your highest-revenue products—the system treats it as more urgent because running out of a top seller hurts more.

Notice the language: 'may run out this week at the current rate of sales.' That's intentional. It's not saying 'will definitely run out'—it's saying 'based on how fast it's been selling, this is when it could happen.'

Also notice this note at the bottom: 'This assessment is based on recent sales at the current rate of sales and may change if demand shifts.' That's the system being honest about what it knows and what it doesn't.

This is how a human analyst would think: look at the numbers, make a judgment call, explain the reasoning, and acknowledge uncertainty."

**Pause and ask:** "Does this level of detail feel right? Too much? Too little?"

---

## 5. Close (30-60 seconds)

**What to say:**

"I want to ask you a few questions to see if this would actually be useful for you.

**First:** Think about last month. Was there a time when you ran out of something and wished you'd known it was coming? Would having this kind of heads-up have helped?

**Second:** If you got a report like this every Monday morning—just a quick read, maybe 5 minutes—would that be valuable? Or is weekly too often, or not often enough?

**Third:** What else would you want to know? Are there other things about your inventory or sales that would be helpful to track?

I'm not asking you to commit to anything. I'm just trying to understand if this solves a real problem for you, or if we're missing something important.

What do you think?"

---

## Speaker Notes

### Key Phrases to Use
- "At the current rate of sales" (not "AI predicts" or "algorithm calculates")
- "Based on your actual data" (emphasize it's their numbers, not estimates)
- "This is how a human analyst would think" (build trust through familiarity)
- "May change if demand shifts" (acknowledge uncertainty)

### Things to Avoid
- ❌ "AI-powered" or "machine learning"
- ❌ "Advanced analytics" or "data science"
- ❌ "99% accurate" or any accuracy claims
- ❌ "Coming soon" features
- ❌ Technical terms like "days-of-stock calculation" or "severity thresholds"

### Pause Moments
Use these natural pauses to gauge interest:
- After explaining the data format
- After showing the executive summary
- After walking through a specific insight
- Before asking validation questions

### Handling Questions

**"How accurate is this?"**
"It's based on your actual sales data, so it's as accurate as your data is recent. If you have good sales history, it's quite reliable. If you don't have sales data, it uses industry estimates, which are less precise but still give you a starting point."

**"What if sales change?"**
"That's exactly why it says 'at the current rate of sales' and 'may change if demand shifts.' It's not a crystal ball—it's a tool that says 'based on what's been happening, here's what to watch.'"

**"Do I need to use this every week?"**
"No. You can run it whenever you want. Some shops do it weekly, some do it monthly, some just when they're planning orders. It's up to you."

**"Can I customize the thresholds?"**
"Right now, it uses industry-standard thresholds that work for most small retail shops. We're keeping it simple so you don't have to configure anything."

---

## Demo Checklist

- [ ] Have `sample_unified_data.csv` ready to upload
- [ ] Test the Streamlit app before the demo
- [ ] Have browser open to `http://localhost:8501`
- [ ] Know which products will be flagged in the sample data
- [ ] Be ready to explain why specific products were flagged
- [ ] Have validation questions prepared
- [ ] Be ready to listen more than talk during Q&A

---

**Remember:** You're not selling software. You're showing a tool that might help. Let the value speak for itself.
