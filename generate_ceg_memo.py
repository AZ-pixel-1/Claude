#!/usr/bin/env python3
"""
CEG US (Constellation Energy) - Investment Memo Generator
Generates a professional 1-page A4 investment memo PDF
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.ticker as mticker
import numpy as np
from datetime import datetime

# ── Color Palette ──────────────────────────────────────────────
BG          = '#0D1117'
CARD_BG     = '#161B22'
ACCENT      = '#58A6FF'
GREEN       = '#3FB950'
RED         = '#F85149'
YELLOW      = '#D29922'
WHITE       = '#E6EDF3'
GREY        = '#8B949E'
LIGHT_GREY  = '#C9D1D9'
DARK_BORDER = '#30363D'

def draw_rounded_rect(ax, x, y, w, h, color=CARD_BG, alpha=0.9, radius=0.02):
    rect = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad={radius}",
                          facecolor=color, edgecolor=DARK_BORDER, linewidth=0.5, alpha=alpha,
                          transform=ax.transAxes)
    ax.add_patch(rect)

fig = plt.figure(figsize=(8.27, 11.69), facecolor=BG, dpi=150)
ax_main = fig.add_axes([0, 0, 1, 1])
ax_main.set_xlim(0, 1)
ax_main.set_ylim(0, 1)
ax_main.set_facecolor(BG)
ax_main.axis('off')

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
draw_rounded_rect(ax_main, 0.02, 0.945, 0.96, 0.045, color='#1A2332')

ax_main.text(0.03, 0.975, 'CEG US', fontsize=18, fontweight='bold', color=ACCENT,
             va='center', fontfamily='monospace')
ax_main.text(0.03, 0.955, 'Constellation Energy Corp  |  NASDAQ  |  Utilities / Nuclear IPP',
             fontsize=7, color=GREY, va='center', fontfamily='monospace')

ax_main.text(0.62, 0.975, '$287.66', fontsize=16, fontweight='bold', color=WHITE,
             va='center', fontfamily='monospace')
ax_main.text(0.62, 0.955, 'Last Price (Feb 13, 2026)', fontsize=6, color=GREY,
             va='center', fontfamily='monospace')

ax_main.text(0.78, 0.975, 'BUY', fontsize=14, fontweight='bold', color=GREEN,
             va='center', fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a3a1a', edgecolor=GREEN, linewidth=1))

ax_main.text(0.88, 0.975, 'PT: $407', fontsize=10, fontweight='bold', color=GREEN,
             va='center', fontfamily='monospace')
ax_main.text(0.88, 0.955, '+42% upside', fontsize=7, color=GREEN,
             va='center', fontfamily='monospace')

# Thin accent line
ax_main.plot([0.02, 0.98], [0.943, 0.943], color=ACCENT, linewidth=1.5, alpha=0.6)

# ══════════════════════════════════════════════════════════════════
# ROW 1: KEY METRICS BAR + SNAPSHOT
# ══════════════════════════════════════════════════════════════════
metrics = [
    ('Mkt Cap', '$104B'),
    ('EV', '$129B'),
    ('Fwd P/E', '27.0x'),
    ('EV/EBITDA', '15.9x'),
    ('Div Yield', '0.56%'),
    ('D/E', '0.63x'),
    ('Beta', '1.14'),
    ('52w Range', '$161-$413'),
]

draw_rounded_rect(ax_main, 0.02, 0.905, 0.96, 0.032)
for i, (label, val) in enumerate(metrics):
    x_pos = 0.04 + i * 0.118
    ax_main.text(x_pos, 0.928, val, fontsize=7.5, fontweight='bold', color=WHITE,
                 va='center', fontfamily='monospace')
    ax_main.text(x_pos, 0.913, label, fontsize=5.5, color=GREY,
                 va='center', fontfamily='monospace')

# ══════════════════════════════════════════════════════════════════
# ROW 2 LEFT: INVESTMENT THESIS
# ══════════════════════════════════════════════════════════════════
draw_rounded_rect(ax_main, 0.02, 0.72, 0.47, 0.178)
ax_main.text(0.04, 0.885, 'INVESTMENT THESIS', fontsize=8, fontweight='bold',
             color=ACCENT, va='center', fontfamily='monospace')
ax_main.plot([0.04, 0.47], [0.878, 0.878], color=DARK_BORDER, linewidth=0.5)

thesis_points = [
    ('1.', 'Largest US nuclear fleet (21% PJM capacity) = irreplaceable'),
    ('   ', 'clean baseload monopoly in power-starved grid'),
    ('2.', 'AI/data center demand inflection: US DC load 33→120 GW'),
    ('   ', 'by 2030; CEG best positioned with 24/7 carbon-free power'),
    ('3.', 'Calpine deal (closed Jan 2026): 55 GW combined, >20%'),
    ('   ', 'EPS accretion, +$2B annual FCF, $300M cost synergies'),
    ('4.', 'PJM capacity prices 10x\'d ($29→$333/MW-day) with supply'),
    ('   ', 'deficit of 6.6 GW; nuclear clears every auction'),
    ('5.', 'Crane Clean Energy Center (TMI restart): 835 MW online'),
    ('   ', '2027, $1.6B invest, 20-yr Microsoft PPA + $1B DOE loan'),
]

y = 0.868
for prefix, text in thesis_points:
    color = GREEN if prefix.strip().endswith('.') else LIGHT_GREY
    ax_main.text(0.04, y, prefix, fontsize=5.8, fontweight='bold', color=GREEN,
                 va='center', fontfamily='monospace')
    ax_main.text(0.065, y, text, fontsize=5.8, color=LIGHT_GREY,
                 va='center', fontfamily='monospace')
    y -= 0.0145

# ══════════════════════════════════════════════════════════════════
# ROW 2 RIGHT: FINANCIAL SNAPSHOT TABLE
# ══════════════════════════════════════════════════════════════════
draw_rounded_rect(ax_main, 0.51, 0.72, 0.47, 0.178)
ax_main.text(0.53, 0.885, 'FINANCIAL SNAPSHOT', fontsize=8, fontweight='bold',
             color=ACCENT, va='center', fontfamily='monospace')
ax_main.plot([0.53, 0.96], [0.878, 0.878], color=DARK_BORDER, linewidth=0.5)

# Table headers
cols = ['Metric', 'FY2024', 'FY2025E', 'FY2026E']
col_x = [0.53, 0.69, 0.79, 0.89]
for i, col in enumerate(cols):
    ax_main.text(col_x[i], 0.867, col, fontsize=6, fontweight='bold',
                 color=GREY, va='center', fontfamily='monospace')
ax_main.plot([0.53, 0.96], [0.861, 0.861], color=DARK_BORDER, linewidth=0.5)

rows = [
    ('Revenue ($B)',    '$23.6', '$24.6', '$36.0*'),
    ('Adj. EBITDA ($B)', '$4.5', '$5.4',  '$8.5*'),
    ('Adj. EPS ($)',   '$11.91', '$9.25', '$11.0'),
    ('FCF ($B)',        '$1.8',  '$2.1',  '$4.0*'),
    ('Net Debt ($B)',   '$3.2', '$16.4†', '$15.0†'),
    ('EBITDA Margin',   '19%',  '22%',   '24%'),
    ('Net Debt/EBITDA', '0.7x', '3.0x†', '1.8x†'),
]
y = 0.851
for row in rows:
    for i, val in enumerate(row):
        color = WHITE if i > 0 else LIGHT_GREY
        ax_main.text(col_x[i], y, val, fontsize=5.8, color=color,
                     va='center', fontfamily='monospace')
    y -= 0.0145
    if y > 0.74:
        ax_main.plot([0.53, 0.96], [y + 0.005, y + 0.005], color=DARK_BORDER,
                     linewidth=0.3, alpha=0.5)

ax_main.text(0.53, 0.728, '*Incl. Calpine  †Pro forma w/ Calpine debt',
             fontsize=4.5, color=GREY, va='center', fontfamily='monospace', style='italic')

# ══════════════════════════════════════════════════════════════════
# ROW 3 LEFT: PEER VALUATION COMP
# ══════════════════════════════════════════════════════════════════
draw_rounded_rect(ax_main, 0.02, 0.545, 0.47, 0.168)
ax_main.text(0.04, 0.7, 'PEER VALUATION COMP', fontsize=8, fontweight='bold',
             color=ACCENT, va='center', fontfamily='monospace')
ax_main.plot([0.04, 0.47], [0.693, 0.693], color=DARK_BORDER, linewidth=0.5)

# Peer comp table
peer_cols = ['', 'CEG', 'VST', 'NRG', 'TLN']
peer_x = [0.04, 0.15, 0.24, 0.33, 0.42]
for i, col in enumerate(peer_cols):
    color = ACCENT if col == 'CEG' else GREY
    ax_main.text(peer_x[i], 0.683, col, fontsize=6, fontweight='bold',
                 color=color, va='center', fontfamily='monospace')
ax_main.plot([0.04, 0.47], [0.677, 0.677], color=DARK_BORDER, linewidth=0.5)

peer_data = [
    ('Mkt Cap ($B)',  ['$104', '$89', '$32', '$10']),
    ('Fwd P/E',       ['27.0x', '15.5x', '16.3x', '18.5x']),
    ('EV/EBITDA',     ['15.9x', '11.2x', '10.2x', '12.8x']),
    ('D/E Ratio',     ['0.63', '3.12', '6.15', '2.80']),
    ('ROE',           ['22%', '72%', '64%', '45%']),
    ('Div Yield',     ['0.6%', '0.8%', '1.1%', '0.0%']),
    ('1Y Return',     ['+78%', '+95%', '+42%', '+55%']),
]
y = 0.667
for label, vals in peer_data:
    ax_main.text(peer_x[0], y, label, fontsize=5.5, color=LIGHT_GREY,
                 va='center', fontfamily='monospace')
    for j, val in enumerate(vals):
        color = ACCENT if j == 0 else WHITE
        ax_main.text(peer_x[j + 1], y, val, fontsize=5.5, color=color,
                     va='center', fontfamily='monospace')
    y -= 0.0145
    if y > 0.56:
        ax_main.plot([0.04, 0.47], [y + 0.005, y + 0.005], color=DARK_BORDER,
                     linewidth=0.3, alpha=0.5)

ax_main.text(0.04, 0.555, 'CEG commands premium on nuclear scarcity + clean energy moat',
             fontsize=4.5, color=YELLOW, va='center', fontfamily='monospace', style='italic')

# ══════════════════════════════════════════════════════════════════
# ROW 3 RIGHT: PJM CAPACITY PRICE CHART
# ══════════════════════════════════════════════════════════════════
draw_rounded_rect(ax_main, 0.51, 0.545, 0.47, 0.168)
ax_main.text(0.53, 0.7, 'PJM CAPACITY PRICING ($/MW-day)', fontsize=8, fontweight='bold',
             color=ACCENT, va='center', fontfamily='monospace')

ax_chart1 = fig.add_axes([0.56, 0.56, 0.38, 0.12])
ax_chart1.set_facecolor(CARD_BG)
years = ['22/23', '23/24', '24/25', '25/26', '26/27', '27/28']
prices = [50.0, 34.1, 28.9, 269.9, 329.2, 333.4]
colors = [GREY, GREY, RED, GREEN, GREEN, GREEN]
bars = ax_chart1.bar(years, prices, color=colors, width=0.55, edgecolor=DARK_BORDER, linewidth=0.5)
for bar, price in zip(bars, prices):
    ax_chart1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
                   f'${price:.0f}', ha='center', va='bottom', fontsize=5,
                   color=WHITE, fontweight='bold', fontfamily='monospace')
ax_chart1.set_ylim(0, 420)
ax_chart1.tick_params(axis='both', colors=GREY, labelsize=5)
ax_chart1.spines['top'].set_visible(False)
ax_chart1.spines['right'].set_visible(False)
ax_chart1.spines['left'].set_color(DARK_BORDER)
ax_chart1.spines['bottom'].set_color(DARK_BORDER)
ax_chart1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

# ══════════════════════════════════════════════════════════════════
# ROW 4 LEFT: DATA CENTER POWER DEMAND CHART
# ══════════════════════════════════════════════════════════════════
draw_rounded_rect(ax_main, 0.02, 0.355, 0.47, 0.183)
ax_main.text(0.04, 0.525, 'US DATA CENTER POWER DEMAND (GW)', fontsize=8,
             fontweight='bold', color=ACCENT, va='center', fontfamily='monospace')

ax_chart2 = fig.add_axes([0.07, 0.375, 0.38, 0.13])
ax_chart2.set_facecolor(CARD_BG)
dc_years = ['2023', '2024', '2025E', '2026E', '2028E', '2030E', '2035E']
dc_gw = [15, 25, 41, 55, 80, 120, 176]
ax_chart2.fill_between(range(len(dc_years)), dc_gw, alpha=0.2, color=ACCENT)
ax_chart2.plot(range(len(dc_years)), dc_gw, color=ACCENT, linewidth=2, marker='o',
               markersize=4, markerfacecolor=WHITE, markeredgecolor=ACCENT)
for i, (yr, gw) in enumerate(zip(dc_years, dc_gw)):
    ax_chart2.annotate(f'{gw}', (i, gw), textcoords="offset points", xytext=(0, 8),
                       ha='center', fontsize=5.5, color=WHITE, fontweight='bold',
                       fontfamily='monospace')
ax_chart2.set_xticks(range(len(dc_years)))
ax_chart2.set_xticklabels(dc_years, fontsize=5, color=GREY, fontfamily='monospace')
ax_chart2.set_ylim(0, 200)
ax_chart2.tick_params(axis='y', colors=GREY, labelsize=5)
ax_chart2.spines['top'].set_visible(False)
ax_chart2.spines['right'].set_visible(False)
ax_chart2.spines['left'].set_color(DARK_BORDER)
ax_chart2.spines['bottom'].set_color(DARK_BORDER)
ax_chart2.text(0.5, 0.92, 'Source: Deloitte, Goldman Sachs, IEA estimates',
               transform=ax_chart2.transAxes, fontsize=4, color=GREY,
               ha='center', fontfamily='monospace', style='italic')

# ══════════════════════════════════════════════════════════════════
# ROW 4 RIGHT: CEG GENERATION MIX (POST-CALPINE) - DONUT CHART
# ══════════════════════════════════════════════════════════════════
draw_rounded_rect(ax_main, 0.51, 0.355, 0.47, 0.183)
ax_main.text(0.53, 0.525, 'CEG GENERATION MIX (55 GW POST-CALPINE)',
             fontsize=7, fontweight='bold', color=ACCENT, va='center', fontfamily='monospace')

ax_donut = fig.add_axes([0.54, 0.365, 0.18, 0.15])
ax_donut.set_facecolor(CARD_BG)
gen_labels = ['Nuclear', 'Nat Gas', 'Hydro/Wind\n/Solar', 'Geothermal']
gen_sizes = [32, 46, 16, 6]
gen_colors = [ACCENT, '#D29922', GREEN, '#A371F7']
wedges, _ = ax_donut.pie(gen_sizes, colors=gen_colors, startangle=90,
                          wedgeprops=dict(width=0.35, edgecolor=CARD_BG, linewidth=1.5))
ax_donut.text(0, 0, '55\nGW', ha='center', va='center', fontsize=10,
              fontweight='bold', color=WHITE, fontfamily='monospace')

# Legend for donut
legend_y = 0.49
for i, (label, size, color) in enumerate(zip(gen_labels, gen_sizes, gen_colors)):
    lbl = label.replace('\n', '')
    ax_main.plot([0.76], [legend_y - i * 0.028], 's', color=color, markersize=5,
                 transform=ax_main.transAxes)
    ax_main.text(0.78, legend_y - i * 0.028, f'{lbl}: {size}%',
                 fontsize=6, color=LIGHT_GREY, va='center', fontfamily='monospace')

# ══════════════════════════════════════════════════════════════════
# ROW 5: CATALYSTS + RISKS SIDE BY SIDE
# ══════════════════════════════════════════════════════════════════

# Catalysts
draw_rounded_rect(ax_main, 0.02, 0.195, 0.47, 0.153)
ax_main.text(0.04, 0.335, 'CATALYSTS & UPCOMING EVENTS', fontsize=8, fontweight='bold',
             color=GREEN, va='center', fontfamily='monospace')
ax_main.plot([0.04, 0.47], [0.328, 0.328], color=DARK_BORDER, linewidth=0.5)

catalysts = [
    ('Feb 24',  'Q4 2025 earnings + FY26 guidance (post-Calpine)'),
    ('Q1 26',   'First combined CEG+Calpine segment reporting'),
    ('H1 26',   'Potential new data center PPAs (CyrusOne +others)'),
    ('2027',    'Crane Clean Energy Center (TMI) restart: +835 MW'),
    ('2027+',   'Nuclear uprates: ~1.3 GW incremental capacity'),
    ('Ongoing', 'IRA Section 45Y PTC: ~$30/MWh nuclear tailwind'),
    ('Ongoing', 'PJM capacity repricing higher (supply deficit)'),
]
y = 0.318
for date, desc in catalysts:
    ax_main.text(0.04, y, f'▸ {date}', fontsize=5.5, fontweight='bold', color=GREEN,
                 va='center', fontfamily='monospace')
    ax_main.text(0.135, y, desc, fontsize=5.5, color=LIGHT_GREY,
                 va='center', fontfamily='monospace')
    y -= 0.0145

# Risks
draw_rounded_rect(ax_main, 0.51, 0.195, 0.47, 0.153)
ax_main.text(0.53, 0.335, 'KEY RISKS', fontsize=8, fontweight='bold',
             color=RED, va='center', fontfamily='monospace')
ax_main.plot([0.53, 0.96], [0.328, 0.328], color=DARK_BORDER, linewidth=0.5)

risks = [
    ('HIGH',  'Calpine integration execution; $300M synergy target'),
    ('HIGH',  'Elevated valuation (27x fwd P/E) vs peers (16x avg)'),
    ('MED',   'Pro forma leverage jump 0.7x→3.0x net debt/EBITDA'),
    ('MED',   'Nuclear regulatory/operational risk (NRC relicensing)'),
    ('MED',   'Power price/spark spread normalization risk'),
    ('LOW',   'Political risk to IRA nuclear credits (bipartisan)'),
    ('LOW',   'AI demand slowdown / hyperscaler capex pullback'),
]
y = 0.318
for severity, desc in risks:
    sev_color = RED if severity == 'HIGH' else (YELLOW if severity == 'MED' else GREEN)
    ax_main.text(0.53, y, f'[{severity}]', fontsize=5.5, fontweight='bold', color=sev_color,
                 va='center', fontfamily='monospace')
    ax_main.text(0.60, y, desc, fontsize=5.5, color=LIGHT_GREY,
                 va='center', fontfamily='monospace')
    y -= 0.0145

# ══════════════════════════════════════════════════════════════════
# ROW 6: TECHNICAL SETUP + BULL/BEAR
# ══════════════════════════════════════════════════════════════════
draw_rounded_rect(ax_main, 0.02, 0.06, 0.47, 0.128)
ax_main.text(0.04, 0.175, 'TECHNICAL SETUP', fontsize=8, fontweight='bold',
             color=ACCENT, va='center', fontfamily='monospace')
ax_main.plot([0.04, 0.47], [0.168, 0.168], color=DARK_BORDER, linewidth=0.5)

tech_items = [
    ('50-DMA: $238  |  200-DMA: $211  |  Both BELOW price', WHITE),
    ('RSI(14): ~31 (near oversold) - potential entry zone', GREEN),
    ('Support: $272  |  Resistance: $325  |  ATH: $413', WHITE),
    ('Golden cross intact; pullback from ATH = -30%', YELLOW),
    ('Consensus: 14 Buy / 0 Sell  |  Avg PT $407 (+42%)', GREEN),
]
y = 0.158
for text, color in tech_items:
    ax_main.text(0.045, y, '▸', fontsize=5.5, color=ACCENT, va='center', fontfamily='monospace')
    ax_main.text(0.06, y, text, fontsize=5.5, color=color, va='center', fontfamily='monospace')
    y -= 0.0145

# Bull / Bear
draw_rounded_rect(ax_main, 0.51, 0.06, 0.47, 0.128)

# Bull case
ax_main.text(0.53, 0.175, 'BULL $480+ (67%↑)', fontsize=7, fontweight='bold',
             color=GREEN, va='center', fontfamily='monospace')
ax_main.plot([0.53, 0.72], [0.168, 0.168], color=DARK_BORDER, linewidth=0.5)
bull_pts = [
    'Nuclear scarcity premium re-rates higher',
    'Calpine synergies beat >$300M target',
    'New mega data center PPAs announced',
]
y = 0.158
for pt in bull_pts:
    ax_main.text(0.535, y, f'▲ {pt}', fontsize=5.3, color=GREEN,
                 va='center', fontfamily='monospace')
    y -= 0.013

# Bear case
ax_main.text(0.53, y + 0.003, 'BEAR $180 (37%↓)', fontsize=7, fontweight='bold',
             color=RED, va='center', fontfamily='monospace')
ax_main.plot([0.53, 0.72], [y - 0.003, y - 0.003], color=DARK_BORDER, linewidth=0.5)
y -= 0.012
bear_pts = [
    'Multiple compression to peer avg (16x)',
    'Capacity price reversal / regulatory change',
    'Integration stumbles + leverage concerns',
]
for pt in bear_pts:
    ax_main.text(0.535, y, f'▼ {pt}', fontsize=5.3, color=RED,
                 va='center', fontfamily='monospace')
    y -= 0.013

# ══════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════
ax_main.plot([0.02, 0.98], [0.055, 0.055], color=DARK_BORDER, linewidth=0.5)
ax_main.text(0.02, 0.04, 'DISCLAIMER: For informational purposes only. Not investment advice. '
             'Data sources: Company filings, Bloomberg, FactSet, S&P Capital IQ, PJM.',
             fontsize=4, color=GREY, va='center', fontfamily='monospace', style='italic')
ax_main.text(0.02, 0.025, f'Credit: Moody\'s Baa1 / S&P BBB+ (Stable)  |  '
             f'Shares Out: 312M  |  Float: 99%  |  Inst. Ownership: ~85%  |  '
             f'Short Interest: ~2%  |  Generated: {datetime.now().strftime("%b %d, %Y")}',
             fontsize=4, color=GREY, va='center', fontfamily='monospace')
ax_main.text(0.98, 0.025, 'CONFIDENTIAL', fontsize=5, fontweight='bold', color=RED,
             va='center', ha='right', fontfamily='monospace', alpha=0.6)

plt.savefig('/home/user/Claude/CEG_Investment_Memo.pdf', format='pdf',
            facecolor=BG, edgecolor='none', bbox_inches='tight', pad_inches=0.1)
plt.savefig('/home/user/Claude/CEG_Investment_Memo.png', format='png',
            facecolor=BG, edgecolor='none', bbox_inches='tight', pad_inches=0.1, dpi=200)
print("✓ Memo saved: CEG_Investment_Memo.pdf + CEG_Investment_Memo.png")
