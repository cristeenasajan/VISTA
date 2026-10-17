import json
import random
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# VISTA
# Verification Intelligence & Silicon Test Analyzer
# ============================================================

st.set_page_config(
    page_title="VISTA | Silicon Test Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

MASTER_FILE = DATA_DIR / "vista_master_results.json"


# ============================================================
# LOAD MASTER DATA
# ============================================================

@st.cache_data
def load_master_data():

    if not MASTER_FILE.exists():
        return {}

    try:
        with open(MASTER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return {}


data = load_master_data()


# ============================================================
# DATA HELPERS
# ============================================================

def get_benchmark_data(name):
    """Return benchmark data using a case-insensitive name match."""
    benchmarks = data.get("benchmarks", {})
    target = str(name).strip().casefold()

    if isinstance(benchmarks, dict):
        for benchmark_name, benchmark_data in benchmarks.items():
            if str(benchmark_name).strip().casefold() == target:
                return benchmark_data if isinstance(benchmark_data, dict) else {}

    elif isinstance(benchmarks, list):
        for item in benchmarks:
            if (
                isinstance(item, dict)
                and str(item.get("name", "")).strip().casefold() == target
            ):
                return item

    return {}


def find_value(obj, keys, default=0):

    if not isinstance(obj, dict):
        return default

    for key in keys:

        if key in obj:
            return obj[key]

    return default


# ============================================================
# GENERATE SHIMMERING STARS
# ============================================================

def create_stars(count=190):

    random.seed(42)

    stars = []

    for _ in range(count):

        left = random.uniform(0, 100)
        top = random.uniform(0, 100)

        size = random.uniform(1.0, 3.2)

        duration = random.uniform(2.5, 8.5)

        delay = random.uniform(-10, 0)

        opacity = random.uniform(0.25, 0.9)

        stars.append(
            f"""
            <span
                class="star"
                style="
                    left:{left:.2f}%;
                    top:{top:.2f}%;
                    width:{size:.2f}px;
                    height:{size:.2f}px;
                    animation-duration:{duration:.2f}s;
                    animation-delay:{delay:.2f}s;
                    opacity:{opacity:.2f};
                ">
            </span>
            """
        )

    return "".join(stars)


# ============================================================
# FLOATING PARTICLES
# ============================================================

def create_particles(count=50):

    random.seed(123)

    particles = []

    for _ in range(count):

        left = random.uniform(3, 97)
        top = random.uniform(3, 97)

        duration = random.uniform(8, 22)

        delay = random.uniform(-20, 0)

        size = random.uniform(1.5, 4.5)

        particles.append(
            f"""
            <span
                class="particle"
                style="
                    left:{left:.2f}%;
                    top:{top:.2f}%;
                    width:{size:.2f}px;
                    height:{size:.2f}px;
                    animation-duration:{duration:.2f}s;
                    animation-delay:{delay:.2f}s;
                ">
            </span>
            """
        )

    return "".join(particles)


stars_html = create_stars()
particles_html = create_particles()


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   FONTS
   ============================================================ */

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap'
);


/* ============================================================
   GLOBAL
   ============================================================ */

html,
body,
[class*="css"] {

    font-family: 'Inter', sans-serif;

}


.stApp {

    background: #050B1A;

    color: #f5efff;

    overflow-x: hidden;

}


/* ============================================================
   REMOVE STREAMLIT DEFAULTS
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}

[data-testid="stToolbar"] {
    visibility: hidden;
}

[data-testid="stDecoration"] {
    display: none;
}


/* ============================================================
   MAIN CONTENT
   ============================================================ */

.block-container {

    max-width: 1450px;

    padding-top: 1.5rem;
    padding-bottom: 5rem;

    position: relative;

    z-index: 20;

}


/* ============================================================
   CINEMATIC BACKGROUND
   ============================================================ */

.vista-background {

    position: fixed;

    inset: 0;

    width: 100vw;

    height: 100vh;

    overflow: hidden;

    pointer-events: none;

    z-index: 0;

    background:

        radial-gradient(
            ellipse at 50% 40%,
            rgba(37, 137, 255, 0.14),
            transparent 38%
        ),

        radial-gradient(
            ellipse at 15% 75%,
            rgba(31, 134, 255, 0.09),
            transparent 34%
        ),

        radial-gradient(
            ellipse at 85% 20%,
            rgba(66.0, 80.0, 255.0, 0.09),
            transparent 32%
        ),

        #050B1A;

}


/* ============================================================
   TOP BLUE GLOW
   ============================================================ */

.top-glow {

    position: absolute;

    width: 1000px;

    height: 300px;

    top: -170px;

    left: 50%;

    transform: translateX(-50%);

    background:

        radial-gradient(
            ellipse,
            rgba(51, 145, 255, 0.32),
            transparent 70%
        );

    filter: blur(30px);

}


/* ============================================================
   AURORA
   ============================================================ */

.aurora {

    position: absolute;

    width: 155%;

    height: 55%;

    left: -28%;

    top: 3%;

    opacity: 0.42;

    filter: blur(45px);

    background:

        linear-gradient(
            115deg,

            transparent 15%,

            rgba(39, 138, 255, 0.0) 25%,

            rgba(39, 138, 255, 0.30) 38%,

            rgba(44, 141, 255, 0.22) 48%,

            rgba(86.0, 76.0, 255.0, 0.28) 58%,

            rgba(39, 138, 255, 0.0) 76%
        );

    transform: rotate(-8deg);

    animation:
        auroraFlow 18s ease-in-out infinite alternate;

}


@keyframes auroraFlow {

    0% {

        transform:
            translateX(-8%)
            translateY(-3%)
            rotate(-9deg)
            scale(1);

    }

    50% {

        transform:
            translateX(5%)
            translateY(5%)
            rotate(-4deg)
            scale(1.08);

    }

    100% {

        transform:
            translateX(-3%)
            translateY(9%)
            rotate(-11deg)
            scale(1.15);

    }

}


/* ============================================================
   SECOND AURORA
   ============================================================ */

.aurora-two {

    position: absolute;

    width: 145%;

    height: 45%;

    left: -22%;

    bottom: 3%;

    filter: blur(55px);

    opacity: 0.28;

    background:

        linear-gradient(
            70deg,

            transparent 15%,

            rgba(35, 136, 255, 0.22) 32%,

            rgba(42, 140, 255, 0.35) 48%,

            rgba(43.0, 92.0, 255.0, 0.20) 63%,

            transparent 82%
        );

    transform: rotate(5deg);

    animation:
        auroraBottom 22s ease-in-out infinite alternate;

}


@keyframes auroraBottom {

    from {

        transform:
            translateX(-8%)
            rotate(5deg)
            scale(1);

    }

    to {

        transform:
            translateX(8%)
            rotate(-3deg)
            scale(1.12);

    }

}


/* ============================================================
   NEBULA CORE
   ============================================================ */

.nebula-core {

    position: absolute;

    width: 650px;

    height: 650px;

    left: 50%;

    top: 42%;

    transform:
        translate(-50%, -50%);

    border-radius: 50%;

    background:

        radial-gradient(
            circle,

            rgba(66, 153, 255, 0.17) 0%,

            rgba(35, 136, 255, 0.09) 25%,

            rgba(30, 133, 255, 0.035) 46%,

            transparent 70%
        );

    animation:
        corePulse 7s ease-in-out infinite;

}


@keyframes corePulse {

    0%,
    100% {

        transform:
            translate(-50%, -50%)
            scale(0.92);

        opacity: 0.60;

    }

    50% {

        transform:
            translate(-50%, -50%)
            scale(1.12);

        opacity: 1;

    }

}


/* ============================================================
   ENERGY RINGS
   ============================================================ */

.energy-ring {

    position: absolute;

    left: 50%;

    top: 42%;

    border-radius: 50%;

    border:
        1px solid rgba(81, 161, 255, 0.14);

    transform:
        translate(-50%, -50%)
        rotateX(65deg);

    box-shadow:

        0 0 35px rgba(60, 150, 255, 0.08),

        inset 0 0 30px rgba(60, 150, 255, 0.04);

}


.ring-one {

    width: 420px;

    height: 420px;

    animation:
        ringRotateOne 16s linear infinite;

}


.ring-two {

    width: 650px;

    height: 650px;

    border-color:
        rgba(70, 155, 255, 0.09);

    animation:
        ringRotateTwo 25s linear infinite reverse;

}


.ring-three {

    width: 900px;

    height: 900px;

    border-color:
        rgba(82.0, 99.0, 255.0, 0.06);

    animation:
        ringRotateThree 35s linear infinite;

}


@keyframes ringRotateOne {

    from {

        transform:
            translate(-50%, -50%)
            rotateX(65deg)
            rotateZ(0deg);

    }

    to {

        transform:
            translate(-50%, -50%)
            rotateX(65deg)
            rotateZ(360deg);

    }

}


@keyframes ringRotateTwo {

    from {

        transform:
            translate(-50%, -50%)
            rotateX(65deg)
            rotateZ(360deg);

    }

    to {

        transform:
            translate(-50%, -50%)
            rotateX(65deg)
            rotateZ(0deg);

    }

}


@keyframes ringRotateThree {

    from {

        transform:
            translate(-50%, -50%)
            rotateX(65deg)
            rotateZ(0deg);

    }

    to {

        transform:
            translate(-50%, -50%)
            rotateX(65deg)
            rotateZ(-360deg);

    }

}


/* ============================================================
   ENERGY WAVES
   ============================================================ */

.energy-wave {

    position: absolute;

    width: 165%;

    height: 1px;

    left: -32%;

    background:

        linear-gradient(
            90deg,

            transparent,

            rgba(57, 148, 255, 0.0),

            rgba(77, 159, 255, 0.45),

            rgba(95.0, 91.0, 255.0, 0.50),

            rgba(77, 159, 255, 0.0),

            transparent
        );

    filter: blur(1px);

    opacity: 0.35;

}


.energy-wave-one {

    top: 32%;

    animation:
        waveOne 11s ease-in-out infinite;

}


.energy-wave-two {

    top: 68%;

    animation:
        waveTwo 15s ease-in-out infinite;

}


@keyframes waveOne {

    0% {

        transform:
            translateX(-25%)
            rotate(-7deg);

        opacity: 0;

    }

    30% {
        opacity: 0.5;
    }

    70% {
        opacity: 0.25;
    }

    100% {

        transform:
            translateX(25%)
            rotate(-7deg);

        opacity: 0;

    }

}


@keyframes waveTwo {

    0% {

        transform:
            translateX(25%)
            rotate(6deg);

        opacity: 0;

    }

    35% {
        opacity: 0.35;
    }

    70% {
        opacity: 0.18;
    }

    100% {

        transform:
            translateX(-25%)
            rotate(6deg);

        opacity: 0;

    }

}


/* ============================================================
   SHIMMERING STARS
   ============================================================ */

.star {

    position: absolute;

    display: block;

    border-radius: 50%;

    background: #ffffff;

    box-shadow:

        0 0 4px rgba(255.0, 255.0, 255.0, 0.95),

        0 0 9px rgba(130, 187, 255, 0.90),

        0 0 18px rgba(70, 155, 255, 0.65);

    animation:
        starShimmer ease-in-out infinite;

    will-change:
        transform,
        opacity,
        filter;

}


@keyframes starShimmer {

    0% {

        transform:
            scale(0.35)
            rotate(0deg);

        opacity: 0.15;

        filter:
            brightness(0.7)
            blur(0px);

    }

    20% {

        transform:
            scale(0.75)
            rotate(45deg);

        opacity: 0.45;

        filter:
            brightness(1.2)
            blur(0px);

    }

    45% {

        transform:
            scale(1.8)
            rotate(90deg);

        opacity: 1;

        filter:
            brightness(2)
            blur(0.2px);

    }

    55% {

        transform:
            scale(1.15)
            rotate(135deg);

        opacity: 0.8;

        filter:
            brightness(1.5);

    }

    75% {

        transform:
            scale(0.55)
            rotate(180deg);

        opacity: 0.35;

        filter:
            brightness(0.9);

    }

    100% {

        transform:
            scale(0.35)
            rotate(360deg);

        opacity: 0.15;

        filter:
            brightness(0.7);

    }

}


/* ============================================================
   FLOATING PARTICLES
   ============================================================ */

.particle {

    position: absolute;

    border-radius: 50%;

    background:
        rgba(109, 176, 255, 0.80);

    box-shadow:
        0 0 12px rgba(68, 154, 255, 0.70);

    animation:
        particleFloat ease-in-out infinite;

}


@keyframes particleFloat {

    0% {

        transform:
            translate3d(0,0,0)
            scale(0.6);

        opacity: 0;

    }

    25% {

        opacity: 0.6;

    }

    50% {

        transform:
            translate3d(35px,-45px,0)
            scale(1);

        opacity: 0.85;

    }

    75% {

        opacity: 0.4;

    }

    100% {

        transform:
            translate3d(-20px,-90px,0)
            scale(0.4);

        opacity: 0;

    }

}


/* ============================================================
   CINEMATIC COMETS
   ============================================================ */

.comet {

    position: absolute;

    width: 10px;

    height: 10px;

    border-radius: 50%;

    background: #ffffff;

    box-shadow:

        0 0 8px #ffffff,

        0 0 18px #b8d9ff,

        0 0 35px #5ca7ff,

        0 0 65px rgba(65, 152, 255, 0.9);

    opacity: 0;

    z-index: 3;

}


/* Main comet tail */

.comet::before {

    content: "";

    position: absolute;

    width: 280px;

    height: 4px;

    right: 5px;

    top: 3px;

    border-radius: 999px;

    background:

        linear-gradient(
            90deg,

            transparent,

            rgba(67, 153, 255, 0.04),

            rgba(83, 162, 255, 0.18),

            rgba(137, 191, 255, 0.55),

            rgba(255.0, 255.0, 255.0, 0.95)
        );

    filter: blur(2px);

}


/* Soft extended comet tail */

.comet::after {

    content: "";

    position: absolute;

    width: 450px;

    height: 18px;

    right: 0;

    top: -3px;

    border-radius: 999px;

    background:

        linear-gradient(
            90deg,

            transparent,

            rgba(50, 144, 255, 0.02),

            rgba(65, 152, 255, 0.09),

            rgba(83, 162, 255, 0.20),

            transparent
        );

    filter: blur(8px);

}


/* Large comet */

.comet-one {

    left: -12%;

    top: 15%;

    transform:
        rotate(-28deg);

    animation:
        cometFlight 11s linear infinite;

}


/* Smaller comet */

.comet-two {

    left: -15%;

    top: 72%;

    transform:
        scale(0.65)
        rotate(-28deg);

    animation:
        cometFlightTwo 17s linear infinite;

    animation-delay: 5s;

}


@keyframes cometFlight {

    0% {

        left: -12%;

        top: 15%;

        opacity: 0;

    }

    4% {

        opacity: 1;

    }

    18% {

        opacity: 1;

    }

    30% {

        left: 108%;

        top: 55%;

        opacity: 0;

    }

    31% {

        left: -12%;

        top: 15%;

        opacity: 0;

    }

    100% {

        left: -12%;

        top: 15%;

        opacity: 0;

    }

}


@keyframes cometFlightTwo {

    0% {

        left: -15%;

        top: 72%;

        opacity: 0;

    }

    5% {

        opacity: 0.8;

    }

    22% {

        opacity: 0.8;

    }

    38% {

        left: 110%;

        top: 35%;

        opacity: 0;

    }

    39% {

        left: -15%;

        top: 72%;

        opacity: 0;

    }

    100% {

        left: -15%;

        top: 72%;

        opacity: 0;

    }

}


/* ============================================================
   PERSPECTIVE GRID
   ============================================================ */

.grid-floor {

    position: absolute;

    width: 150%;

    height: 70%;

    left: -25%;

    bottom: -38%;

    opacity: 0.075;

    background-image:

        linear-gradient(
            rgba(86, 164, 255, 0.45) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(86, 164, 255, 0.45) 1px,
            transparent 1px
        );

    background-size: 55px 55px;

    transform:
        perspective(600px)
        rotateX(62deg);

    animation:
        gridMove 12s linear infinite;

}


@keyframes gridMove {

    from {

        background-position:
            0 0,
            0 0;

    }

    to {

        background-position:
            0 55px,
            55px 0;

    }

}


/* ============================================================
   HERO
   ============================================================ */

.hero {

    position: relative;

    padding:
        35px
        40px
        32px
        40px;

    margin-bottom: 25px;

    border-radius: 24px;

    border:
        1px solid rgba(90, 166, 255, 0.22);

    background:

        linear-gradient(
            135deg,
            rgba(13, 24, 53, 0.88),
            rgba(7, 11, 22, 0.78)
        );

    box-shadow:

        0 25px 80px rgba(0.0, 0.0, 0.0, 0.55),

        0 0 60px rgba(44, 141, 255, 0.08),

        inset 0 1px 0 rgba(255.0, 255.0, 255.0, 0.06);

    backdrop-filter:
        blur(20px);

    overflow: hidden;

}


.hero::before {

    content: "";

    position: absolute;

    top: 0;

    left: -100%;

    width: 60%;

    height: 1px;

    background:

        linear-gradient(
            90deg,
            transparent,
            rgba(128, 186, 255, 0.8),
            transparent
        );

    animation:
        heroScan 7s linear infinite;

}


@keyframes heroScan {

    0% {
        left: -100%;
    }

    100% {
        left: 160%;
    }

}


.hero-title {

    font-family:
        'Space Grotesk',
        sans-serif;

    font-size:
        3.2rem;

    font-weight:
        700;

    letter-spacing:
        -2px;

    margin:
        0;

    background:

        linear-gradient(
            100deg,
            #ffffff 0%,
            #c8e1ff 30%,
            #5ca7ff 65%,
            #7bb8ff 100%
        );

    -webkit-background-clip:
        text;

    -webkit-text-fill-color:
        transparent;

}


.hero-subtitle {

    color:
        #9aa8b9;

    font-size:
        1rem;

    line-height:
        1.7;

    margin-top:
        8px;

}


.status-pill {

    display:
        inline-flex;

    align-items:
        center;

    gap:
        8px;

    margin-top:
        20px;

    padding:
        7px 14px;

    border-radius:
        999px;

    background:
        rgba(61, 150, 255, 0.10);

    border:
        1px solid rgba(83, 162, 255, 0.25);

    color:
        #b5d7ff;

    font-size:
        0.78rem;

    font-weight:
        600;

    letter-spacing:
        0.5px;

}


.status-dot {

    width:
        7px;

    height:
        7px;

    border-radius:
        50%;

    background:
        #6aafff;

    box-shadow:
        0 0 10px #55a3ff;

    animation:
        statusPulse 1.8s infinite;

}


@keyframes statusPulse {

    0%,
    100% {

        transform:
            scale(0.8);

        opacity:
            0.5;

    }

    50% {

        transform:
            scale(1.3);

        opacity:
            1;

    }

}


/* ============================================================
   SECTION TITLES
   ============================================================ */

.section-title {

    font-family:
        'Space Grotesk',
        sans-serif;

    font-size:
        1.25rem;

    font-weight:
        600;

    color:
        #eee5f7;

    margin:
        30px 0 14px 2px;

}


.section-title::before {

    content:
        "";

    display:
        inline-block;

    width:
        4px;

    height:
        18px;

    margin-right:
        10px;

    vertical-align:
        -2px;

    border-radius:
        5px;

    background:

        linear-gradient(
            180deg,
            #6bafff,
            #3592ff
        );

    box-shadow:
        0 0 12px rgba(73, 157, 255, 0.6);

}


/* ============================================================
   METRIC GRID
   ============================================================ */

.metric-grid {

    display:
        grid;

    grid-template-columns:
        repeat(4,1fr);

    gap:
        16px;

}


/* ============================================================
   METRIC CARDS
   ============================================================ */

.metric-card {

    position:
        relative;

    padding:
        22px;

    min-height:
        120px;

    border-radius:
        18px;

    border:
        1px solid rgba(86, 164, 255, 0.17);

    background:

        linear-gradient(
            145deg,
            rgba(14, 22, 42, 0.88),
            rgba(7, 10, 18, 0.85)
        );

    box-shadow:

        0 18px 45px rgba(0.0, 0.0, 0.0, 0.3),

        inset 0 1px 0 rgba(255.0, 255.0, 255.0, 0.04);

    transition:
        transform 0.35s ease,
        border-color 0.35s ease,
        box-shadow 0.35s ease;

    overflow:
        hidden;

}


.metric-card::after {

    content:
        "";

    position:
        absolute;

    width:
        130px;

    height:
        130px;

    right:
        -70px;

    top:
        -70px;

    border-radius:
        50%;

    background:

        radial-gradient(
            circle,
            rgba(67, 153, 255, 0.16),
            transparent 70%
        );

}


.metric-card:hover {

    transform:
        translateY(-7px);

    border-color:
        rgba(101, 172, 255, 0.42);

    box-shadow:

        0 25px 60px rgba(0.0, 0.0, 0.0, 0.45),

        0 0 30px rgba(52, 145, 255, 0.12);

}


.metric-label {

    color:
        #919eae;

    font-size:
        0.78rem;

    text-transform:
        uppercase;

    letter-spacing:
        1.2px;

}


.metric-value {

    font-family:
        'Space Grotesk',
        sans-serif;

    font-size:
        2.15rem;

    font-weight:
        700;

    margin-top:
        7px;

    color:
        #f7efff;

}


.metric-accent {

    color:
        #6cb0ff;

}


/* ============================================================
   TABLES
   ============================================================ */

[data-testid="stDataFrame"] {

    border-radius:
        14px;

    overflow:
        hidden;

}


thead tr th {

    background:
        rgba(42, 101, 170, 0.20) !important;

    color:
        #c8d7e9 !important;

}


tbody tr {

    background:
        rgba(9, 13, 25, 0.8) !important;

}


tbody tr:hover {

    background:
        rgba(45, 112, 190, 0.12) !important;

}


/* ============================================================
   TABS
   ============================================================ */

.stTabs [data-baseweb="tab-list"] {

    gap:
        8px;

    background:
        rgba(6, 9, 18, 0.65);

    border-radius:
        14px;

    padding:
        6px;

}


.stTabs [data-baseweb="tab"] {

    border-radius:
        10px;

    padding:
        8px 16px;

    color:
        #919caa;

}


.stTabs [aria-selected="true"] {

    background:
        rgba(55, 126, 210, 0.20);

    color:
        #cae2ff;

}


/* ============================================================
   BUTTON
   ============================================================ */

.stButton > button {

    border:
        1px solid rgba(81, 161, 255, 0.3);

    background:
        rgba(36, 86, 145, 0.22);

    color:
        #d5e8ff;

    border-radius:
        10px;

    transition:
        all 0.3s ease;

}


.stButton > button:hover {

    border-color:
        rgba(119, 182, 255, 0.65);

    background:
        rgba(51, 118, 196, 0.35);

    box-shadow:
        0 0 25px rgba(63, 151, 255, 0.18);

}


/* ============================================================
   PROGRESS
   ============================================================ */

.stProgress > div > div > div {

    background:

        linear-gradient(
            90deg,
            #357fd6,
            #4d9fff,
            #78afef
        );

}


/* ============================================================
   FOOTER
   ============================================================ */

.vista-footer {

    margin-top:
        55px;

    padding-top:
        20px;

    border-top:
        1px solid rgba(82, 162, 255, 0.12);

    text-align:
        center;

    color:
        #69737f;

    font-size:
        0.75rem;

    letter-spacing:
        0.5px;

}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 900px) {

    .metric-grid {

        grid-template-columns:
            repeat(2,1fr);

    }

    .hero-title {

        font-size:
            2.4rem;

    }

}


@media (max-width: 600px) {

    .metric-grid {

        grid-template-columns:
            1fr;

    }

    .hero {

        padding:
            25px;

    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# CINEMATIC BACKGROUND
# ============================================================

st.html(
    f"""
    <div class="vista-background">

        <!-- Blue atmospheric glow -->
        <div class="top-glow"></div>

        <!-- Moving aurora -->
        <div class="aurora"></div>
        <div class="aurora-two"></div>

        <!-- Central nebula -->
        <div class="nebula-core"></div>

        <!-- Rotating energy rings -->
        <div class="energy-ring ring-one"></div>
        <div class="energy-ring ring-two"></div>
        <div class="energy-ring ring-three"></div>

        <!-- Energy waves -->
        <div class="energy-wave energy-wave-one"></div>
        <div class="energy-wave energy-wave-two"></div>

        <!-- Shimmering stars -->
        {stars_html}

        <!-- Floating particles -->
        {particles_html}

        <!-- Flying comets -->
        <div class="comet comet-one"></div>
        <div class="comet comet-two"></div>

        <!-- Perspective grid -->
        <div class="grid-floor"></div>

    </div>
    """
)


# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div class="hero">

        <div class="hero-title">
            VISTA
        </div>

        <div class="hero-subtitle">

            Verification Intelligence & Silicon Test Analyzer

            <br>

            Automated fault analysis, diagnosis,
            test optimization and machine-learning
            assisted test intelligence.

        </div>

        <div class="status-pill">

            <span class="status-dot"></span>

            VISTA ENGINE ONLINE

        </div>

    </div>
    """
)


# ============================================================
# BENCHMARK DATA
# ============================================================

c17 = get_benchmark_data("C17")
c432 = get_benchmark_data("C432")
c499 = get_benchmark_data("C499")


# ============================================================
# FALLBACK DATA
# ============================================================

if not c17:

    c17 = {
        "total_faults": 22,
        "detected_faults": 22,
        "coverage": 100.0,
        "patterns": 32,
        "compacted_patterns": 4,
    }


if not c432:

    c432 = {
        "total_faults": 414,
        "detected_faults": 411,
        "coverage": 99.28,
        "patterns": 1024,
        "compacted_patterns": 18,
    }


if not c499:

    c499 = {
        "total_faults": 430,
        "detected_faults": 429,
        "coverage": 99.77,
        "patterns": 1024,
        "compacted_patterns": 0,
    }


# ============================================================
# EXTRACT C17
# ============================================================

c17_total = find_value(
    c17,
    ["total_faults", "faults", "total"],
    22
)

c17_detected = find_value(
    c17,
    ["detected_faults", "detected"],
    22
)

c17_coverage = find_value(
    c17,
    ["coverage", "fault_coverage"],
    100.0
)


# ============================================================
# EXTRACT C432
# ============================================================

c432_total = find_value(
    c432,
    ["total_faults", "faults", "total"],
    414
)

c432_detected = find_value(
    c432,
    ["detected_faults", "detected"],
    411
)

c432_coverage = find_value(
    c432,
    ["coverage", "fault_coverage"],
    99.28
)


# ============================================================
# EXTRACT C499 — PREFER THE VERIFIED MEMBER 1 MATRIX
# ============================================================

# Folder layout expected on the user's machine:
# Desktop/VISTA/member2/dashboard.py
# Desktop/VISTA_member1/c499_detection_matrix_recheck.json
C499_MATRIX_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / "VISTA_member1"
    / "c499_detection_matrix_recheck.json"
)

# Start with the master-data values as a fallback. If the verified
# Member 1 matrix is available, use it as the source of truth.
c499_total = find_value(
    c499,
    ["total_faults", "faults", "total"],
    430,
)
c499_detected = find_value(
    c499,
    ["detected_faults", "detected"],
    429,
)
c499_coverage = find_value(
    c499,
    ["coverage", "fault_coverage"],
    99.77,
)

if C499_MATRIX_FILE.exists():
    try:
        with C499_MATRIX_FILE.open("r", encoding="utf-8") as f:
            c499_matrix = json.load(f)

        if (
            c499_matrix.get("schema_version") == "1.1"
            and c499_matrix.get("document") == "fault_sim_report"
            and isinstance(c499_matrix.get("faults"), list)
            and c499_matrix["faults"]
        ):
            c499_faults = c499_matrix["faults"]
            c499_total = len(c499_faults)
            c499_detected = sum(
                1 for fault in c499_faults
                if fault.get("detected", False)
            )
            c499_coverage = (
                100.0 * c499_detected / c499_total
                if c499_total else 0.0
            )
        else:
            st.warning(
                "The C499 reference matrix was found but did not match "
                "the expected VISTA schema 1.1 format. Using master data."
            )
    except (OSError, json.JSONDecodeError, TypeError, KeyError) as exc:
        st.warning(
            f"Could not load the verified C499 matrix ({exc}). "
            "Using master data instead."
        )


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

st.html(
    """
    <div class="section-title">
        Executive Overview
    </div>
    """
)


st.html(
    f"""
    <div class="metric-grid">

        <div class="metric-card">

            <div class="metric-label">
                C499 Faults
            </div>

            <div class="metric-value">
                {int(c499_total)}
            </div>

            <div class="metric-label">
                total stuck-at faults
            </div>

        </div>


        <div class="metric-card">

            <div class="metric-label">
                C499 Coverage
            </div>

            <div class="metric-value metric-accent">
                {float(c499_coverage):.2f}%
            </div>

            <div class="metric-label">
                {int(c499_detected)} / {int(c499_total)} detected
            </div>

        </div>


        <div class="metric-card">

            <div class="metric-label">
                C432 Coverage
            </div>

            <div class="metric-value metric-accent">
                {float(c432_coverage):.2f}%
            </div>

            <div class="metric-label">
                {int(c432_detected)} / {int(c432_total)} detected
            </div>

        </div>


        <div class="metric-card">

            <div class="metric-label">
                C17 Coverage
            </div>

            <div class="metric-value metric-accent">
                {float(c17_coverage):.2f}%
            </div>

            <div class="metric-label">
                {int(c17_detected)} / {int(c17_total)} detected
            </div>

        </div>

    </div>
    """
)


# ============================================================
# COVERAGE
# ============================================================

st.html(
    """
    <div class="section-title">
        Fault Coverage Across Benchmarks
    </div>
    """
)


coverage_df = pd.DataFrame(
    {
        "Benchmark": [
            "C17",
            "C432",
            "C499",
        ],

        "Total Faults": [
            int(c17_total),
            int(c432_total),
            int(c499_total),
        ],

        "Detected Faults": [
            int(c17_detected),
            int(c432_detected),
            int(c499_detected),
        ],

        "Coverage (%)": [
            float(c17_coverage),
            float(c432_coverage),
            float(c499_coverage),
        ],
    }
)


st.dataframe(
    coverage_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# COVERAGE CHART
# ============================================================

st.html(
    """
    <div class="section-title">
        Coverage Visualization
    </div>
    """
)


chart_df = coverage_df.set_index(
    "Benchmark"
)[
    ["Coverage (%)"]
]


st.bar_chart(
    chart_df,

    use_container_width=True,
)


# ============================================================
# Fault Diagnosis — C432
# ============================================================

st.html(
    """
    <div class="section-title">
    Fault Diagnosis — C432
</div>
    """
)

diagnosis = (
    data.get("benchmarks", {})
    .get("c432", {})
    .get("diagnosis", {})
)

if not diagnosis:
    diagnosis = {
        "hard": 0,
        "medium": 0,
        "easy": 0,
    }





diagnosis_df = pd.DataFrame(
    {
        "Difficulty":
            list(diagnosis.keys()),

        "Fault Count":
            list(diagnosis.values()),
    }
)


st.dataframe(
    diagnosis_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# PATTERN COMPACTION
# ============================================================

st.html(
    """
    <div class="section-title">
        Test Pattern Compaction
    </div>
    """
)


compaction = data.get(
    "compaction",
    {}
)


if not compaction:

    compaction = {

        "C17": {

            "original": 32,

            "selected": 4,

            "reduction": 87.5,

        },

        "C432": {

            "original": 1024,

            "selected": 18,

            "reduction": 98.24,

        },

    }

# Add the latest independently verified C499 compaction result.
C499_COMPACTION_FILE = DATA_DIR / "c499_compaction_results.json"

if C499_COMPACTION_FILE.exists():
    try:
        with C499_COMPACTION_FILE.open("r", encoding="utf-8") as f:
            c499_compaction_result = json.load(f)

        if (
            c499_compaction_result.get("circuit") == "c499"
            and c499_compaction_result.get("coverage_preserved") is True
        ):
            compaction["C499 (verified)"] = {
                "original": c499_compaction_result["original_patterns"],
                "selected": c499_compaction_result["selected_pattern_count"],
                "reduction": c499_compaction_result["pattern_reduction_pct"],
            }

    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        st.warning("Could not load the latest C499 compaction result.")


compaction_rows = []


for benchmark, values in compaction.items():

    compaction_rows.append(
        {
            "Benchmark":
                benchmark,

            "Original Patterns":
                values.get(
                    "original",
                    0
                ),

            "Selected Patterns":
                values.get(
                    "selected",
                    0
                ),

            "Pattern Reduction (%)":
                values.get(
                    "reduction",
                    0
                ),
        }
    )


if compaction_rows:

    compaction_df = pd.DataFrame(
        compaction_rows
    )

    st.dataframe(
        compaction_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# UNDETECTED FAULTS
# ============================================================

st.html(
    """
    <div class="section-title">
        Undetected Faults
    </div>
    """
)


# Prefer the verified C499 reference matrix for its undetected faults.
undetected = data.get("undetected_faults", {})

if not isinstance(undetected, dict):
    undetected = {}
else:
    undetected = dict(undetected)

if C499_MATRIX_FILE.exists():
    try:
        with C499_MATRIX_FILE.open("r", encoding="utf-8") as f:
            undetected_matrix = json.load(f)
        if (
            undetected_matrix.get("schema_version") == "1.1"
            and undetected_matrix.get("document") == "fault_sim_report"
        ):
            undetected["C499"] = [
                fault.get("id", "Unknown fault")
                for fault in undetected_matrix.get("faults", [])
                if not fault.get("detected", False)
            ]
    except (OSError, json.JSONDecodeError, TypeError, KeyError):
        st.warning("Could not load C499 undetected faults from the reference matrix.")

if not isinstance(undetected.get("C432"), list):
    undetected["C432"] = []

if not undetected["C432"]:
    undetected["C432"] = [
        "F200 — N259 — SA1",
        "F292 — N347 — SA1",
        "F330 — N379 — SA1",
    ]

undetected_rows = []


for benchmark, faults in undetected.items():

    if isinstance(faults, list):

        for fault in faults:

            undetected_rows.append(
                {
                    "Benchmark":
                        benchmark,

                    "Fault":
                        fault,
                }
            )

    else:

        undetected_rows.append(
            {
                "Benchmark":
                    benchmark,

                "Fault":
                    str(fault),
            }
        )


if undetected_rows:

    undetected_df = pd.DataFrame(
        undetected_rows
    )

    st.dataframe(
        undetected_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# ML INTELLIGENCE
# ============================================================

st.html(
    """
    <div class="section-title">
        ML Fault Prioritization
    </div>
    """
)

# Load the saved C432 evaluation rather than showing placeholder zeros.
# Load reproducible leave-one-benchmark-out ML evaluation.
ML_RESULTS_FILE = DATA_DIR / "relative_cross_benchmark_ml_results.json"

ml_results = {}
c432_experiment = {}
ml = {}

if ML_RESULTS_FILE.exists():
    try:
        with ML_RESULTS_FILE.open("r", encoding="utf-8") as f:
            ml_results = json.load(f)

        experiments = ml_results.get("experiments", [])

        c432_experiment = next(
            (
                experiment
                for experiment in experiments
                if str(experiment.get("test_benchmark", "")).casefold() == "c432"
            ),
            {},
        )

        ml = {
            "model": "Random Forest",
            "features": ml_results.get("features", []),
            "accuracy": c432_experiment.get(
                "classification_report", {}
            ).get("accuracy", 0.0),
            "balanced_accuracy": c432_experiment.get(
                "balanced_accuracy", 0.0
            ),
            "macro_f1": c432_experiment.get("macro_f1", 0.0),
            "samples": c432_experiment.get("test_samples", 0),
        }

    except (OSError, json.JSONDecodeError, TypeError):
        st.warning("Could not load cross-benchmark ML evaluation results.")
else:
    st.warning("Cross-benchmark ML results file was not found.")

average_metrics = ml_results.get("average_metrics", {})

# Convert fractions to percentages for display.
def as_percent(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return number * 100 if 0 <= number <= 1 else number

c432_accuracy = as_percent(ml.get("accuracy", 0.0))
c432_balanced_accuracy = as_percent(ml.get("balanced_accuracy", 0.0))
c432_macro_f1 = as_percent(ml.get("macro_f1", 0.0))

average_balanced_accuracy = as_percent(
    average_metrics.get("balanced_accuracy", 0.0)
)
average_macro_f1 = as_percent(average_metrics.get("macro_f1", 0.0))
average_weighted_f1 = as_percent(average_metrics.get("weighted_f1", 0.0))

st.html(
    f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Evaluation</div>
            <div class="metric-value">LOBO</div>
            <div class="metric-label">Leave-one-benchmark-out</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">C432 Accuracy</div>
            <div class="metric-value metric-accent">{c432_accuracy:.1f}%</div>
            <div class="metric-label">{ml.get("samples", 0)} held-out samples</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">C432 Balanced Accuracy</div>
            <div class="metric-value metric-accent">{c432_balanced_accuracy:.1f}%</div>
            <div class="metric-label">Held-out C432 benchmark</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">C432 Macro F1</div>
            <div class="metric-value metric-accent">{c432_macro_f1:.1f}%</div>
            <div class="metric-label">Held-out C432 benchmark</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Average Balanced Accuracy</div>
            <div class="metric-value metric-accent">{average_balanced_accuracy:.1f}%</div>
            <div class="metric-label">Across 3 benchmarks</div>
        </div>
    </div>
    <p class="metric-label" style="margin-top: 10px;">
        Cross-benchmark evaluation: train on two benchmarks and test on the
        third. C432 generalization is currently weak; these results should not
        be interpreted as strong fault-difficulty prediction performance.
    </p>
    <p class="metric-label">
        Cross-benchmark averages — Macro F1: {average_macro_f1:.1f}% |
        Weighted F1: {average_weighted_f1:.1f}%.
    </p>
    """
)
# ============================================================
# ML FEATURES
# ============================================================

features = ml.get(
    "features",
    [
        "logic_depth",
        "distance_to_output",
        "gate_type",
        "is_sa0",
        "is_sa1",
        "fanout",
        "fanin",
    ],
)


feature_df = pd.DataFrame(
    {
        "Structural Feature":
            features
    }
)


st.dataframe(
    feature_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# DEVELOPMENT STATUS
# ============================================================

st.html(
    """
    <div class="section-title">
        VISTA Development Status
    </div>
    """
)


status_rows = [

    {
        "Module":
            "RTL Analysis",

        "Status":
            "COMPLETE",
    },

    {
        "Module":
            "Fault Generation",

        "Status":
            "COMPLETE",
    },

    {
        "Module":
            "Fault Injection",

        "Status":
            "COMPLETE",
    },

    {
        "Module":
            "Fault Simulation",

        "Status":
            "COMPLETE",
    },

    {
        "Module":
            "Fault Coverage",

        "Status":
            "COMPLETE",
    },

    {
        "Module":
            "Fault Diagnosis",

        "Status":
            "COMPLETE",
    },

    {
        "Module":
            "Pattern Compaction",

        "Status":
            "COMPLETE",
    },

    {
        "Module":
            "Structural ML",

        "Status":
            "PROTOTYPE",
    },

    {
        "Module":
            "Advanced ATPG",

        "Status":
            "IN PROGRESS",
    },

]


status_df = pd.DataFrame(
    status_rows
)


st.dataframe(
    status_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="vista-footer">

        VISTA — Verification Intelligence & Silicon Test Analyzer

        <br>

        RTL → Faults → Simulation → Diagnosis
        → Optimization → Intelligence

        <br><br>

        Research & Engineering Prototype

    </div>
    """
)
