import os
import json
import math
import urllib.request
from datetime import datetime


USERNAME = os.getenv("GITHUB_USERNAME", "bhav-17")
TOKEN = os.getenv("GITHUB_TOKEN")

OUTPUT_DIR = "assets"
OUTPUT_FILE = f"{OUTPUT_DIR}/contribution-dna.svg"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# --------------------------------------------------
# GET REAL GITHUB CONTRIBUTION DATA
# --------------------------------------------------

query = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
          }
        }
      }
    }
  }
}
"""

payload = {
    "query": query,
    "variables": {
        "login": USERNAME
    }
}

data = json.dumps(payload).encode("utf-8")

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=data,
    headers = {
    "Content-Type": "application/json",
    "User-Agent": "DNA-Contribution-Graph"
}

if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"
    }
)

try:
    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    weeks = (
        result["data"]["user"]
        ["contributionsCollection"]
        ["contributionCalendar"]
        ["weeks"]
    )

    contributions = []

    for week in weeks:
        for day in week["contributionDays"]:
            contributions.append(day["contributionCount"])

except Exception as error:
    print("Could not fetch contribution data:", error)

    # Fallback so the SVG still generates
    contributions = [0] * 365


# --------------------------------------------------
# REDUCE CONTRIBUTION DATA TO DNA NODES
# --------------------------------------------------

NODE_COUNT = 32

if len(contributions) < NODE_COUNT:
    contributions += [0] * (NODE_COUNT - len(contributions))

chunk_size = max(1, len(contributions) // NODE_COUNT)

node_values = []

for i in range(NODE_COUNT):

    start = i * chunk_size
    end = start + chunk_size

    chunk = contributions[start:end]

    if chunk:
        value = sum(chunk) / len(chunk)
    else:
        value = 0

    node_values.append(value)


max_value = max(node_values) if max(node_values) > 0 else 1


# --------------------------------------------------
# SVG SETTINGS
# --------------------------------------------------

WIDTH = 1100
HEIGHT = 420

BACKGROUND = "#0D1117"
CYAN = "#00F7FF"
DARK_CYAN = "#007C86"

CENTER_Y = HEIGHT / 2

START_X = 80
END_X = WIDTH - 80

AMPLITUDE = 105

NODE_RADIUS = 7


# --------------------------------------------------
# CREATE DNA NODES
# --------------------------------------------------

svg_nodes = []
svg_rungs = []

for i in range(NODE_COUNT):

    progress = i / (NODE_COUNT - 1)

    x = START_X + progress * (END_X - START_X)

    phase = progress * math.pi * 6

    y1 = CENTER_Y + math.sin(phase) * AMPLITUDE
    y2 = CENTER_Y - math.sin(phase) * AMPLITUDE

    intensity = node_values[i] / max_value

    radius = NODE_RADIUS + intensity * 5

    opacity = 0.35 + intensity * 0.65

    delay = i * 0.08

    # DNA connecting rung
    svg_rungs.append(f"""
        <line
            x1="{x:.2f}"
            y1="{y1:.2f}"
            x2="{x:.2f}"
            y2="{y2:.2f}"
            stroke="{CYAN}"
            stroke-width="1.5"
            opacity="{0.15 + intensity * 0.35:.2f}"
        />
    """)

    # First DNA strand
    svg_nodes.append(f"""
        <circle
            cx="{x:.2f}"
            cy="{y1:.2f}"
            r="{radius:.2f}"
            fill="{CYAN}"
            opacity="{opacity:.2f}"
            filter="url(#glow)"
        >
            <animate
                attributeName="r"
                values="{radius:.2f};{radius + 3:.2f};{radius:.2f}"
                dur="2.8s"
                begin="{delay:.2f}s"
                repeatCount="indefinite"
            />

            <animate
                attributeName="opacity"
                values="{opacity:.2f};1;{opacity:.2f}"
                dur="2.8s"
                begin="{delay:.2f}s"
                repeatCount="indefinite"
            />
        </circle>
    """)

    # Second DNA strand
    svg_nodes.append(f"""
        <circle
            cx="{x:.2f}"
            cy="{y2:.2f}"
            r="{radius:.2f}"
            fill="{CYAN}"
            opacity="{opacity:.2f}"
            filter="url(#glow)"
        >
            <animate
                attributeName="r"
                values="{radius:.2f};{radius + 3:.2f};{radius:.2f}"
                dur="2.8s"
                begin="{delay + 0.35:.2f}s"
                repeatCount="indefinite"
            />

            <animate
                attributeName="opacity"
                values="{opacity:.2f};1;{opacity:.2f}"
                dur="2.8s"
                begin="{delay + 0.35:.2f}s"
                repeatCount="indefinite"
            />
        </circle>
    """)


# --------------------------------------------------
# CREATE DNA CURVES
# --------------------------------------------------

points1 = []
points2 = []

CURVE_POINTS = 250

for i in range(CURVE_POINTS):

    progress = i / (CURVE_POINTS - 1)

    x = START_X + progress * (END_X - START_X)

    phase = progress * math.pi * 6

    y1 = CENTER_Y + math.sin(phase) * AMPLITUDE
    y2 = CENTER_Y - math.sin(phase) * AMPLITUDE

    points1.append(f"{x:.2f},{y1:.2f}")
    points2.append(f"{x:.2f},{y2:.2f}")


# --------------------------------------------------
# FINAL SVG
# --------------------------------------------------

svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
>

<defs>

    <filter id="glow">

        <feGaussianBlur
            stdDeviation="4"
            result="blur"
        />

        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>

    </filter>

    <linearGradient
        id="backgroundGradient"
        x1="0"
        y1="0"
        x2="1"
        y2="1"
    >

        <stop
            offset="0%"
            stop-color="#0D1117"
        />

        <stop
            offset="100%"
            stop-color="#05080C"
        />

    </linearGradient>

</defs>


<!-- BACKGROUND -->

<rect
    width="100%"
    height="100%"
    rx="18"
    fill="url(#backgroundGradient)"
/>


<!-- TITLE -->

<text
    x="50%"
    y="55"
    text-anchor="middle"
    fill="#00F7FF"
    font-family="JetBrains Mono, monospace"
    font-size="22"
    letter-spacing="5"
>
    CONTRIBUTION DNA
</text>


<text
    x="50%"
    y="82"
    text-anchor="middle"
    fill="#8B949E"
    font-family="JetBrains Mono, monospace"
    font-size="12"
    letter-spacing="2"
>
    {USERNAME.upper()} • GITHUB ACTIVITY SEQUENCE
</text>


<!-- DNA STRANDS -->

<polyline
    points="{' '.join(points1)}"
    fill="none"
    stroke="{CYAN}"
    stroke-width="2.5"
    opacity="0.55"
    filter="url(#glow)"
>
    <animate
        attributeName="opacity"
        values="0.35;0.8;0.35"
        dur="4s"
        repeatCount="indefinite"
    />
</polyline>


<polyline
    points="{' '.join(points2)}"
    fill="none"
    stroke="{CYAN}"
    stroke-width="2.5"
    opacity="0.55"
    filter="url(#glow)"
>
    <animate
        attributeName="opacity"
        values="0.8;0.35;0.8"
        dur="4s"
        repeatCount="indefinite"
    />
</polyline>


<!-- DNA CONNECTIONS -->

{''.join(svg_rungs)}


<!-- CONTRIBUTION NODES -->

{''.join(svg_nodes)}


<!-- LEGEND -->

<text
    x="70"
    y="{HEIGHT - 35}"
    fill="#8B949E"
    font-family="JetBrains Mono, monospace"
    font-size="11"
>
    LOW ACTIVITY
</text>


<line
    x1="180"
    y1="{HEIGHT - 40}"
    x2="280"
    y2="{HEIGHT - 40}"
    stroke="{CYAN}"
    stroke-width="3"
    opacity="0.35"
/>


<line
    x1="290"
    y1="{HEIGHT - 40}"
    x2="390"
    y2="{HEIGHT - 40}"
    stroke="{CYAN}"
    stroke-width="3"
    opacity="0.7"
/>


<line
    x1="400"
    y1="{HEIGHT - 40}"
    x2="500"
    y2="{HEIGHT - 40}"
    stroke="{CYAN}"
    stroke-width="3"
    opacity="1"
/>


<text
    x="515"
    y="{HEIGHT - 35}"
    fill="#00F7FF"
    font-family="JetBrains Mono, monospace"
    font-size="11"
>
    HIGH ACTIVITY
</text>


</svg>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    file.write(svg)

print(f"Successfully generated {OUTPUT_FILE}")
