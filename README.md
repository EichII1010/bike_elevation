# bike_elevation
categorizes the altitude/gradients for a bike ride
# 🚴‍♂️ GPX Climb Analyzer – Classify "Good" vs "Bad" Elevation Gain

This Streamlit app allows cyclists to upload a GPX track and automatically classify elevation gains into **good**, **bad**, and **neutral** types:

- ✅ **Good climbs** are those where you can carry momentum into the ascent.
- 😤 **Bad climbs** are steep and require grinding in small gears.
- 😐 **Neutral climbs** are somewhere in between.

The app provides a visual elevation profile, a color-coded map, and a detailed summary of your ride.

---

## 🧠 How it works

The app segments your GPX file and calculates:

- Gradient between each GPS point
- Whether a climb is "good", "bad", or "neutral"
  - Based on a 500 m window before each segment: if the prior terrain was downhill (momentum) and the upcoming climb is manageable, it's "good"
  - Steep climbs with no run-up are "bad"
- Positive elevation gain is split into the three categories

---

## 🖥️ Demo features

- Upload your `.gpx` file
- Automatic classification of elevation gain
- **Interactive elevation plot** (color-coded)
- **Interactive map** with start/end markers and color-coded segments
- Summary report of:
  - Total distance
  - Total positive elevation gain
  - Good / bad / neutral elevation meters

---

## 🚀 Getting started

### 1. Clone this repository

```bash
git clone https://github.com/yourusername/gpx-climb-analyzer.git
cd gpx-climb-analyzer

