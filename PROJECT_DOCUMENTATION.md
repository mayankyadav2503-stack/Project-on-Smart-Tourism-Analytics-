# Smart Tourism Analytics Platform

---

## So, What Are We Building Here?

You know how planning a trip usually means having seventeen browser tabs open — checking reviews here, prices there, weather somewhere else, and still ending up with a messy spreadsheet that kinda-sorta works?

Yeah, we got tired of that too. So we built a thing.

It's a travel planning system that actually remembers what you like. Tell it your vibe and your budget, and it'll throw back destinations, hotels, restaurants, and activities that fit *you* — not some generic "top 10 places to visit" list. It checks the weather, converts currency, tells you if a place is going to be swamped with tourists, and even builds a full day-by-day itinerary so you don't have to. And the whole thing runs on your laptop with zero internet once it's set up. Four machine learning models we trained ourselves, all talking to each other, all completely free.

---

## Why Bother?

Because planning travel genuinely sucks right now.

Your options are basically:
- **TripAdvisor** — good for reviews, terrible for actual planning
- **Booking.com/Expedia** — great for hotels, useless for everything else
- **Random blog posts** — maybe useful, maybe five years out of date
- **Google Maps** — somehow you end up lost in a rabbit hole of street view

None of these actually *learn* what you like. They show the same thing to everyone. They don't know you're a broke student who'd rather eat street food than sit in a fancy restaurant. They don't know you hate crowded beaches. They just throw popular stuff at you and call it a day.

We wanted something that actually pays attention.

---

## What We Were Going For

Kept it simple — five goals:

1. **Recommend things that don't suck for *you*** — Not "what's popular on Instagram," but "what would *you* actually enjoy based on what you've liked before."
2. **Plan a whole trip in one go** — Type in where, when, and how much, and get back a full day-by-day plan with hotel, food, activities, and a budget breakdown.
3. **Tell you if a place is going to be a zoo** — Before you book, check how crowded it'll be next week. Avoid the chaos.
4. **Chat with it like a person** — "Hey, what's the weather in Tokyo?" "Find me cheap Italian food in Rome." It just answers. No clicking through menus.
5. **One screen to rule them all** — A dark-mode dashboard that shows your spending, trending spots, crowd forecasts, and what categories of travel you lean toward. All at once.

---

## Who's Gonna Use This Thing?

- **Anyone planning a vacation** who wants suggestions that actually match their style, not just what's trending.
- **People organizing multi-day trips** who'd rather not juggle fifteen browser tabs and a spreadsheet.
- **Whoever's grading this project** and wants to see Flask, Streamlit, SQLite, and four different ML models playing nice together.

---

## Alright, What Does It Actually *Do*?

**Browse and discover stuff:**
- Flip through all destinations, filter by category (beaches, museums, landmarks, whatever)
- Click any destination to see its hotels, restaurants, activities, and reviews
- Search by name or city — "Paris", "Tokyo", "beach in Bali"

**Get suggestions that make sense:**
- A "For You" tab that learns from your history and recommends accordingly
- A "Popular" tab showing what everyone else is booking
- A "Similar" feature — liked Rome? Here's Florence, Barcelona, and Athens

**Plan your trip from soup to nuts:**
- Pick a destination, dates, and a budget
- Hit generate and get back a day-by-day plan with:
  - A hotel that fits your budget
  - Restaurants picked for each meal
  - Activities slotted into morning/afternoon/evening
  - A running cost breakdown so you don't overspend

**Check conditions before you go:**
- Weather for any city (local data, no API calls)
- Currency conversion on the fly
- Crowd predictions — see if a place is going to be packed next week
- Demand forecasts — is this destination getting more or less popular?

**Chat with the assistant:**
- Ask about destinations, weather, hotels, food, activities, currency, budget tips, crowd levels — fifteen different types of questions
- It remembers context within a conversation
- Quick action buttons so you don't have to type everything

**See the big picture on the dashboard:**
- How much you've spent and where
- Which categories you lean toward (museums? beaches? shopping?)
- Monthly crowd trends across all destinations
- Top destinations by bookings and revenue
- Category distribution — how many of each type exist in the system

**Everything's on a map:**
- All destinations plotted on a dark-mode Folium world map
- Filter by category
- Color-coded by rating (green = great, orange = okay, red = meh)
- Click any marker for quick details

---

## Performance? It's Snappy Enough

Most pages load in under half a second. Itineraries generate in about two to three seconds. The chatbot answers instantly since it's rule-based — no waiting for a model to warm up.

Everything runs entirely offline. Weather data? Local profiles for fifteen major cities with a little random jitter so it's not identical every time. Currency rates? Stored in SQLite. Recommendations? Local models. Zero external API calls. No internet required.

SQLite handles thousands of rows without breaking a sweat. Our models trained on a couple hundred records, but the pipeline would work fine with way more.

The UI is dark mode throughout — black backgrounds, dark cards, subtle borders. Interactive Folium map, real-time Plotly charts, collapsible sections. One `pip install -r requirements.txt` and you're running on any OS with Python 3.12. No Docker, no cloud, no accounts.

Oh, and security? There isn't any. We ripped out auth entirely. Hardcoded user ID for the demo. For a college project, it frees us from dealing with login forms and session management so we can focus on the interesting stuff.

---

## The ML Models — What's Actually Going On Under the Hood

**Collaborative Filtering (the "people like you also liked" engine)**

This is the classic Netflix-style recommender. It uses a technique called Non-Negative Matrix Factorization — which sounds fancy but basically means it breaks down the giant grid of "who rated what how much" into hidden patterns. If you and I rated the same five destinations similarly, the model figures we have similar taste and recommends things you liked that I haven't seen yet.

Trained on 189 user reviews. Uses scikit-learn's NMF implementation with 20 latent factors and up to 500 iterations. Saves as a `.pkl` file using joblib.

**Demand Forecasting (what's going to be popular next week)**

This is XGBoost — the workhorse of tabular machine learning. It looks at past booking patterns, day of week, month, whether it's a holiday, and the destination's popularity score, then predicts how much demand to expect over the next seven days.

Trained on 73 real booking records plus 900 synthetic crowd data rows. Uses 100 trees with a max depth of 6 and a learning rate of 0.1.

**Crowd Prediction (how packed will it be?)**

Random Forest — basically a hundred decision trees voting together. Takes into account the day of week, month, holiday status, the destination's popularity, average rating, and review count, then spits out a crowd level from 1 to 5 with a friendly label (Low/Medium/High).

Trained on 900 labeled crowd records. Uses scikit-learn with 100 trees, depth 10, running on all available CPU cores.

**Sentiment Analysis (is this review happy or angry?)**

DistilBERT — a smaller, faster version of Google's BERT, fine-tuned on the Stanford Sentiment Treebank. It reads review text and tells you whether it's positive or negative with a confidence score. Uses HuggingFace's pipeline API, so loading the model is basically one line of Python.

We had to prefix the model name with `distilbert/` because newer versions of Transformers got strict about namespacing — more on that in the "stuff that went wrong" section.

**The Hybrid Recommender (gluing it all together)**

The final recommendation you see isn't just the collaborative filtering score. It's a blend: the CF prediction plus a content-based score that considers whether the destination matches your preferred category, fits your budget, and has good ratings. Custom Python logic in `recommendation_service.py`, with adjustable weights for each factor.

All models live in the `models_saved/` folder. Total disk footprint is about 300 MB, most of which is the DistilBERT reference.

---

## Stuff That Went Wrong (And How We Unstuck Ourselves)

**The HuggingFace naming thing that made no sense**

We loaded our sentiment model with the name `distilbert-base-uncased-finetuned-sst-2-english`. Worked fine for weeks. Then we updated the Transformers library and suddenly the pipeline started treating our text model like it was an image model. The error message was something like `"Cannot read image.png (this model does not support image input)"` — which is deeply confusing when you're analyzing *text*.

Turns out Transformers v5 changed how it resolves model names. Without the organization prefix, it was misrouting to a completely different model. The fix was adding `distilbert/` at the front: `distilbert/distilbert-base-uncased-finetuned-sst-2-english`. One slash, hours of debugging.

**Streamlit and Flask don't share the driver's seat**

At one point we ran `streamlit run app.py` — which is the Flask file, not the Streamlit one. Streamlit tries to register a signal handler when it starts, but Flask's `app.run()` was already running on the main thread. Python doesn't let you do that from a background thread, so it crashed with a `ValueError`.

The fix was obvious in retrospect: keep them in separate files. Flask runs from `app.py` in one terminal, Streamlit runs from `streamlit_app.py` in another. They talk over HTTP. Problem solved.

**When we ripped out auth, everything broke**

The original design had login, registration, session cookies — the whole auth flow. Midway through we decided it was overkill for a demo and removed it all. Bad call to do it incrementally: every single endpoint, every frontend page, every service method referenced the logged-in user's ID somehow. We spent a solid afternoon chasing down `KeyError: 'user_id'` crashes.

Fix was brutal but effective: hardcode `DEFAULT_USER = 1` everywhere and move on. Not production-ready, but for a college demo it keeps the focus on the ML and the UI rather than password forms.

---

## If We Kept Going...

- Live price scraping from Skyscanner and Booking.com
- Chatbot that speaks multiple languages
- Upload a photo of a place and let the system recognize and recommend it
- Share trips with friends, plan collaboratively
- Turn it into a mobile app with offline support
- Smarter itineraries that re-optimize as plans change (reinforcement learning)
- One-click booking through partner APIs
- Proper login with Google or GitHub
- Push notifications when prices drop or weather looks bad
- A/B testing different recommendation algorithms to see which one actually works better

---

## So, Did It Work?

Yeah. It actually works.

We took four different ML models — a matrix factorization recommender, an XGBoost forecaster, a Random Forest crowd predictor, and a DistilBERT sentiment analyzer — and wired them into a single travel planning system. The whole thing runs entirely offline. No API keys, no cloud credits, no internet required.

You get personalized recommendations that actually consider what you like. You get full itineraries generated in seconds. You get crowd forecasts, budget analytics, a chatbot that understands travel questions, and a dark-mode dashboard that ties it all together with interactive charts and a world map.

Everything loads fast. The models predict reasonably well on our data. You can spin the whole thing up on any laptop with a single `pip install`.

Bottom line: you can build a genuinely useful AI travel assistant with nothing but Python, open-source libraries, and some stubbornness. No funding round required.
