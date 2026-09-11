import os
import json
import math
import urllib.request
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = os.getenv("GITHUB_USERNAME", "bhav-17")
TOKEN = os.getenv("GITHUB_TOKEN")

OUTPUT_DIR = "assets"
OUTPUT_FILE = f"{OUTPUT_DIR}/contribution-galaxy.svg"

WIDTH = 1200
HEIGHT = 650

BACKGROUND = "#0D1117"
CYAN = "#00F7FF"
BLUE = "#00B8FF"
DIM_CYAN = "#007C86"
TEXT = "#8B949E"

CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2 + 25

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# GET REAL GITHUB CONTRIBUTION DATA
# ============================================================

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions

        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

payload = {
    "query": QUERY,
    "variables": {
        "login": USERNAME
    }
}

request_data = json.dumps(payload).encode("utf-8")

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Bhavya-Contribution-Galaxy"
}

if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=request_data,
    headers=headers
)


try:

    with urllib.request.urlopen(request) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    calendar = (
        result["data"]["user"]
        ["contributionsCollection"]
        ["contributionCalendar"]
    )

    total_contributions = calendar["totalContributions"]

    contributions = []

    for week in calendar["weeks"]:

        for day in week["contributionDays"]:

            contributions.append({
                "date": day["date"],
                "count": day["contributionCount"]
            })

    print(
        f"Fetched {len(contributions)} contribution days"
    )

    print(
        f"Total contributions: {total_contributions}"
    )


except Exception as error:

    print("ERROR FETCHING CONTRIBUTIONS:")
    print(error)

    contributions = [
        {
            "date": "",
            "count": 0
        }
        for _ in range(365)
    ]

    total_contributions = 0


# ============================================================
# CONTRIBUTION NORMALIZATION
# ============================================================

max_contribution = max(
    day["count"]
    for day in contributions
)

if max_contribution == 0:
    max_contribution = 1


def normalize(value):

    return min(
        value / max_contribution,
        1
    )


# ============================================================
# GENERATE GALAXY STARS
# ============================================================

stars = []
orbit_particles = []

TOTAL_DAYS = len(contributions)

if TOTAL_DAYS == 0:
    TOTAL_DAYS = 1


for index, day in enumerate(contributions):

    contribution_count = day["count"]

    activity = normalize(contribution_count)

    progress = index / TOTAL_DAYS


    # --------------------------------------------------------
    # SPIRAL GALAXY POSITION
    # --------------------------------------------------------

    arm = index % 3

    arm_offset = arm * (
        2 * math.pi / 3
    )

    angle = (
        progress * math.pi * 8
        + arm_offset
    )


    # Distance from the center
    radius = (
        30
        + progress * 250
    )


    # Spiral distortion
    wave = math.sin(
        progress * math.pi * 14
    ) * 25


    x = (
        CENTER_X
        + math.cos(angle)
        * (radius + wave)
    )


    y = (
        CENTER_Y
        + math.sin(angle)
        * (radius * 0.45 + wave * 0.2)
    )


    # --------------------------------------------------------
    # STAR SIZE BASED ON REAL ACTIVITY
    # --------------------------------------------------------

    star_radius = (
        1.5
        + activity * 7
    )


    opacity = (
        0.20
        + activity * 0.80
    )


    glow_radius = (
        star_radius * 2
    )


    animation_delay = (
        index % 40
    ) * 0.12


    # --------------------------------------------------------
    # COLOR BASED ON CONTRIBUTION ACTIVITY
    # --------------------------------------------------------

    if activity > 0.70:
        color = CYAN

    elif activity > 0.35:
        color = BLUE

    elif activity > 0:
        color = DIM_CYAN

    else:
        color = "#12313A"


    # --------------------------------------------------------
    # ONLY STRONGER CONTRIBUTIONS GET LARGE GLOW
    # --------------------------------------------------------

    glow = ""

    if contribution_count > 0:

        glow = f'''
        <circle
            cx="{x:.2f}"
            cy="{y:.2f}"
            r="{glow_radius:.2f}"
            fill="{color}"
            opacity="0.12"
            filter="url(#softGlow)"
        />
        '''


    stars.append(
        f'''
        {glow}

        <circle
            cx="{x:.2f}"
            cy="{y:.2f}"
            r="{star_radius:.2f}"
            fill="{color}"
            opacity="{opacity:.2f}"
            filter="url(#starGlow)"
        >

            <animate
                attributeName="opacity"
                values="{opacity:.2f};1;{opacity:.2f}"
                dur="3s"
                begin="{animation_delay:.2f}s"
                repeatCount="indefinite"
            />

            <animate
                attributeName="r"
                values="{star_radius:.2f};{star_radius + 1.5:.2f};{star_radius:.2f}"
                dur="3s"
                begin="{animation_delay:.2f}s"
                repeatCount="indefinite"
            />

        </circle>
        '''
    )


# ============================================================
# CREATE GALAXY ORBIT RINGS
# ============================================================

orbits = []

for orbit in range(1, 7):

    radius_x = 70 + orbit * 48
    radius_y = radius_x * 0.38

    rotation = orbit * 8 - 20

    orbits.append(
        f'''
        <ellipse
            cx="{CENTER_X}"
            cy="{CENTER_Y}"
            rx="{radius_x}"
            ry="{radius_y}"
            fill="none"
            stroke="{CYAN}"
            stroke-width="1"
            opacity="0.12"
            transform="
                rotate(
                    {rotation}
                    {CENTER_X}
                    {CENTER_Y}
                )
            "
        />
        '''
    )


# ============================================================
# BACKGROUND STARS
# ============================================================

background_stars = []

for i in range(110):

    # Deterministic pseudo-random placement
    x = (
        (i * 137 + 71)
        % (WIDTH - 40)
    ) + 20

    y = (
        (i * 83 + 47)
        % (HEIGHT - 100)
    ) + 70

    size = 1 + (i % 3) * 0.5

    opacity = 0.15 + (i % 5) * 0.08

    background_stars.append(
        f'''
        <circle
            cx="{x}"
            cy="{y}"
            r="{size}"
            fill="{CYAN}"
            opacity="{opacity}"
        />
        '''
    )


# ============================================================
# FINAL SVG
# ============================================================

svg = f'''
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
>


<defs>

    <!-- BACKGROUND GRADIENT -->

    <linearGradient
        id="background"
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
            offset="55%"
            stop-color="#07131A"
        />

        <stop
            offset="100%"
            stop-color="#030609"
        />

    </linearGradient>


    <!-- GALAXY CORE GRADIENT -->

    <radialGradient
        id="core"
    >

        <stop
            offset="0%"
            stop-color="#FFFFFF"
            stop-opacity="1"
        />

        <stop
            offset="20%"
            stop-color="{CYAN}"
            stop-opacity="1"
        />

        <stop
            offset="55%"
            stop-color="{CYAN}"
            stop-opacity="0.35"
        />

        <stop
            offset="100%"
            stop-color="{CYAN}"
            stop-opacity="0"
        />

    </radialGradient>


    <!-- SOFT GLOW -->

    <filter
        id="softGlow"
    >

        <feGaussianBlur
            stdDeviation="6"
        />

    </filter>


    <!-- STAR GLOW -->

    <filter
        id="starGlow"
        x="-100%"
        y="-100%"
        width="300%"
        height="300%"
    >

        <feGaussianBlur
            stdDeviation="2"
            result="blur"
        />

        <feMerge>

            <feMergeNode
                in="blur"
            />

            <feMergeNode
                in="SourceGraphic"
            />

        </feMerge>

    </filter>


    <!-- GRID PATTERN -->

    <pattern
        id="grid"
        width="50"
        height="50"
        patternUnits="userSpaceOnUse"
    >

        <path
            d="M 50 0 L 0 0 0 50"
            fill="none"
            stroke="{CYAN}"
            stroke-width="0.4"
            opacity="0.05"
        />

    </pattern>

</defs>


<!-- ===================================================== -->
<!-- BACKGROUND -->
<!-- ===================================================== -->

<rect
    width="100%"
    height="100%"
    rx="18"
    fill="url(#background)"
/>


<rect
    width="100%"
    height="100%"
    rx="18"
    fill="url(#grid)"
/>


<!-- ===================================================== -->
<!-- BORDER -->
<!-- ===================================================== -->

<rect
    x="12"
    y="12"
    width="{WIDTH - 24}"
    height="{HEIGHT - 24}"
    rx="14"
    fill="none"
    stroke="{CYAN}"
    stroke-width="1"
    opacity="0.45"
/>


<!-- ===================================================== -->
<!-- BACKGROUND STARS -->
<!-- ===================================================== -->

{''.join(background_stars)}


<!-- ===================================================== -->
<!-- HEADER -->
<!-- ===================================================== -->

<text
    x="55"
    y="65"
    fill="{CYAN}"
    font-family="JetBrains Mono, monospace"
    font-size="28"
    font-weight="bold"
    letter-spacing="7"
>
    CONTRIBUTION GALAXY
</text>


<text
    x="58"
    y="94"
    fill="{TEXT}"
    font-family="JetBrains Mono, monospace"
    font-size="12"
    letter-spacing="4"
>
    EVERY CONTRIBUTION BECOMES A STAR
</text>


<!-- USER INFO -->

<text
    x="{WIDTH - 65}"
    y="60"
    text-anchor="end"
    fill="{CYAN}"
    font-family="JetBrains Mono, monospace"
    font-size="16"
    font-weight="bold"
    letter-spacing="3"
>
    BHAV-17
</text>


<text
    x="{WIDTH - 65}"
    y="84"
    text-anchor="end"
    fill="{TEXT}"
    font-family="JetBrains Mono, monospace"
    font-size="10"
    letter-spacing="3"
>
    GITHUB ACTIVITY
</text>


<!-- ===================================================== -->
<!-- ORBITS -->
<!-- ===================================================== -->

{''.join(orbits)}


<!-- ===================================================== -->
<!-- GALAXY CORE -->
<!-- ===================================================== -->

<circle
    cx="{CENTER_X}"
    cy="{CENTER_Y}"
    r="105"
    fill="url(#core)"
    opacity="0.22"
>


    <animate
        attributeName="r"
        values="95;115;95"
        dur="5s"
        repeatCount="indefinite"
    />

</circle>


<circle
    cx="{CENTER_X}"
    cy="{CENTER_Y}"
    r="38"
    fill="{CYAN}"
    opacity="0.16"
    filter="url(#softGlow)"
/>


<circle
    cx="{CENTER_X}"
    cy="{CENTER_Y}"
    r="20"
    fill="{CYAN}"
    opacity="0.85"
    filter="url(#starGlow)"
>


    <animate
        attributeName="opacity"
        values="0.6;1;0.6"
        dur="2.5s"
        repeatCount="indefinite"
    />

</circle>


<!-- CORE SYMBOL -->

<text
    x="{CENTER_X}"
    y="{CENTER_Y + 8}"
    text-anchor="middle"
    fill="#FFFFFF"
    font-family="Arial"
    font-size="22"
>
    ✦
</text>


<!-- ===================================================== -->
<!-- REAL CONTRIBUTION STARS -->
<!-- ===================================================== -->

{''.join(stars)}


<!-- ===================================================== -->
<!-- TOTAL CONTRIBUTIONS -->
<!-- ===================================================== -->

<g>

    <rect
        x="55"
        y="{HEIGHT - 105}"
        width="280"
        height="65"
        rx="8"
        fill="#07131A"
        stroke="{CYAN}"
        stroke-width="1"
        opacity="0.85"
    />

    <text
        x="78"
        y="{HEIGHT - 80}"
        fill="{TEXT}"
        font-family="JetBrains Mono, monospace"
        font-size="11"
        letter-spacing="2"
    >
        TOTAL CONTRIBUTIONS
    </text>


    <text
        x="78"
        y="{HEIGHT - 55}"
        fill="{CYAN}"
        font-family="JetBrains Mono, monospace"
        font-size="22"
        font-weight="bold"
    >
        {total_contributions}
    </text>

</g>


<!-- ===================================================== -->
<!-- LEGEND -->
<!-- ===================================================== -->

<text
    x="{WIDTH - 65}"
    y="{HEIGHT - 80}"
    text-anchor="end"
    fill="{TEXT}"
    font-family="JetBrains Mono, monospace"
    font-size="10"
    letter-spacing="2"
>
    CONTRIBUTION INTENSITY
</text>


<circle
    cx="{WIDTH - 240}"
    cy="{HEIGHT - 55}"
    r="4"
    fill="#12313A"
/>

<circle
    cx="{WIDTH - 210}"
    cy="{HEIGHT - 55}"
    r="5"
    fill="{DIM_CYAN}"
/>

<circle
    cx="{WIDTH - 175}"
    cy="{HEIGHT - 55}"
    r="7"
    fill="{BLUE}"
/>

<circle
    cx="{WIDTH - 130}"
    cy="{HEIGHT - 55}"
    r="9"
    fill="{CYAN}"
    filter="url(#starGlow)"
/>


<text
    x="{WIDTH - 65}"
    y="{HEIGHT - 50}"
    text-anchor="end"
    fill="{TEXT}"
    font-family="JetBrains Mono, monospace"
    font-size="10"
>
    LOW → HIGH
</text>


<!-- ===================================================== -->
<!-- FOOTER -->
<!-- ===================================================== -->

<text
    x="{WIDTH / 2}"
    y="{HEIGHT - 25}"
    text-anchor="middle"
    fill="{CYAN}"
    font-family="JetBrains Mono, monospace"
    font-size="10"
    letter-spacing="4"
    opacity="0.75"
>
    EXPLORE / CONTRIBUTE / EVOLVE
</text>


</svg>
'''


# ============================================================
# SAVE FILE
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(svg)


print()
print("=" * 55)
print("CONTRIBUTION GALAXY GENERATED SUCCESSFULLY")
print("=" * 55)
print(f"User: {USERNAME}")
print(f"Contributions: {total_contributions}")
print(f"Output: {OUTPUT_FILE}")
print("=" * 55)
