# MySafar Flight Agent

MySafar is a travel planning assistant built to make trip preparation feel much more organized and practical. Instead of only searching for flights, the idea behind this project is to support the full travel workflow: creating traveler profiles, planning trips, comparing flight options, building a visit itinerary, and generating useful travel documents in one place. It is designed as a **Morocco-first AI travel agency assistant**, with a Streamlit interface and a modular backend that connects flight search, trip logic, itinerary generation, and document creation.

---

## Why I built this

Planning a trip usually means jumping between too many tools:
- one app for flights,
- another for trip notes,
- another for places to visit,
- and sometimes separate files for invoices, programs, or checklists.

I wanted to build a single application that brings these steps together into one smoother workflow.

The goal of **MySafar** is simple:  
help a traveler go from **trip idea** to **organized travel plan** with less friction.

---

## What the app does

### 1. User authentication
The app allows users to create an account, log in, and manage their own session securely using **Supabase Auth**.

### 2. Traveler profiles
A user can create and store traveler profiles such as:
- themselves,
- family members,
- or friends.

Each profile can include useful travel information such as birth date, passport number, visa number, and optional notes.

### 3. Trip creation
Users can create a trip for a selected traveler profile by entering:
- origin city,
- destination city,
- destination country,
- travel style,
- travel dates,
- and trip preferences.

The app also prevents overlapping trips for the same traveler, which makes the planning process more realistic and structured.

### 4. Flight search and ranking
For each trip, the application searches flights using **Duffel** and ranks offers based on the traveler’s preferences.

The scoring logic is not only based on price. It also considers practical criteria such as:
- total duration,
- number of stops,
- convenience,
- and airline preference rules depending on the trip type.

This makes the result feel closer to a travel agent recommendation than a raw API response.

### 5. Itinerary generation
Once the trip exists, the app can generate a visit itinerary using:
- city geocoding,
- OpenStreetMap points of interest,
- and opening-hours-aware logic when available.

The user can preview the itinerary, edit it, and then save it.

### 6. Travel documents
The app can generate useful trip-related PDF documents such as:
- a travel program,
- a safety/checklist document,
- and an invoice.

These files can then be stored and linked back to the trip.

---

## Project structure

```bash
MySafar_Flight_Agent/
│
├── app.py                  # Main Streamlit entry point
├── requirements.txt        # Project dependencies
├── README.md
│
├── pages/
│   ├── 1_Login.py          # Login / signup page
│   ├── 2_Profiles.py       # Traveler profiles
│   ├── 3_New_Trip.py       # Trip creation and trip management
│   ├── 4_Flights.py        # Duffel flight search and selection
│   ├── 5_Itinerary.py      # Itinerary generation and editing
│   └── 6_Documents.py      # PDF generation and document handling
│
└── services/
    ├── auth.py                 # Authentication helpers
    ├── supabase_client.py      # Supabase connection/session helpers
    ├── guard.py                # Route/page protection
    ├── db_profiles.py          # Profiles database logic
    ├── db_trips.py             # Trips database logic
    ├── db_flights.py           # Saved selected flights
    ├── db_itinerary.py         # Itinerary persistence
    ├── db_documents.py         # Documents persistence
    ├── duffel_client.py        # Duffel API integration
    ├── flight_scoring_duffel.py# Flight scoring and summarization
    ├── geocode_nominatim.py    # City geocoding
    ├── osm_overpass.py         # POI retrieval from OpenStreetMap
    ├── itinerary_gen.py        # Itinerary generation logic
    ├── pdfs.py                 # PDF creation
    └── storage_docs.py         # PDF upload / signed URL helpers
```

## Tech stack

- Python
- Streamlit for the app interface
- Supabase for authentication and database/storage
- Duffel API for flight search
- OpenStreetMap / Overpass / Nominatim for itinerary and place discovery
- Pandas for data handling
- ReportLab for PDF generation
  
## Example use case
Imagine a user wants to plan a trip from Casablanca to Barcelona.
With MySafar, they can:
- create the traveler profile,
- define the trip dates and preferences,
- search ranked flight options,
- generate a day-by-day itinerary,
- and export useful PDF documents for the trip.

#3 Setup
1. Clone the repository
- git clone https://github.com/rachidaj03/MySafar_Flight_Agent.git
- cd MySafar_Flight_Agent
2. Install dependencies
- pip install -r requirements.txt
3. Configure secrets
- You will need to add your Streamlit secrets for services such as:
* Supabase
* Duffel
These should be stored in your Streamlit secrets configuration, not directly inside the code.
4. Run the app
- streamlit run app.py

## What makes this project interesting

- user management,
- business logic,
- recommendation/scoring,
- travel planning,
- geospatial/place data,
- document generation.

## Author
Built by Rachid as a travel-tech project exploring how AI-style workflows can improve trip planning, flight selection, itinerary building, and customer-ready document generation.

