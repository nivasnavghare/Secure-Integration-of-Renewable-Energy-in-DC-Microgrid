import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(18, 12))
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.axis('off')

# Define colors
color_input = '#FFE6CC'
color_renewable = '#FFFFCC'
color_storage = '#E6CCFF'
color_control = '#CCE6FF'
color_output = '#CCFFCC'
color_load = '#FFCCCC'

def create_block(ax, x, y, width, height, text, color, style='round'):
    """Create a block with text"""
    if style == 'round':
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle="round,pad=0.1", 
                            edgecolor='black', 
                            facecolor=color,
                            linewidth=2)
    else:
        box = patches.Rectangle((x, y), width, height,
                               edgecolor='black',
                               facecolor=color,
                               linewidth=2)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text,
           ha='center', va='center',
           fontsize=9, fontweight='bold',
           wrap=True)

def create_arrow(ax, x1, y1, x2, y2, label='', style='->'):
    """Create an arrow between blocks"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                          arrowstyle=style,
                          color='black',
                          linewidth=2,
                          mutation_scale=20)
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.2, label,
               fontsize=7, ha='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

def create_sum_block(ax, x, y, size=0.4):
    """Create summation block"""
    circle = patches.Circle((x, y), size, 
                          edgecolor='black', 
                          facecolor='white',
                          linewidth=2)
    ax.add_patch(circle)
    ax.text(x, y, '+', ha='center', va='center', fontsize=14, fontweight='bold')

# Title
ax.text(10, 13.5, 'DC MICROGRID SIMULINK BLOCK DIAGRAM', 
       ha='center', fontsize=16, fontweight='bold',
       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

# Subtitle
ax.text(10, 12.8, 'Secure Integration of Renewable Energy Sources', 
       ha='center', fontsize=11, style='italic')

# ========== ENVIRONMENTAL INPUTS ==========
ax.text(1.5, 11.5, 'ENVIRONMENTAL INPUTS', fontsize=10, fontweight='bold')

create_block(ax, 0.5, 10, 2, 0.8, 'Solar\nIrradiance\nG(t)', color_input)
create_block(ax, 0.5, 8.5, 2, 0.8, 'Ambient\nTemperature\nT(t)', color_input)
create_block(ax, 0.5, 7, 2, 0.8, 'Wind\nSpeed\nV(t)', color_input)

# ========== RENEWABLE GENERATION ==========
ax.text(5, 11.5, 'RENEWABLE GENERATION', fontsize=10, fontweight='bold')

# PV System
create_block(ax, 4, 9.5, 2.5, 1.2, 'PV SYSTEM\nMPPT Control\nη = 18%', color_renewable)
create_arrow(ax, 2.5, 10.4, 4, 10.1, 'G(t)')
create_arrow(ax, 2.5, 8.9, 4, 9.8, 'T(t)')

# Wind Turbine
create_block(ax, 4, 7, 2.5, 1.2, 'WIND TURBINE\nPower Curve\nPrated=50kW', color_renewable)
create_arrow(ax, 2.5, 7.4, 4, 7.6, 'V(t)')

# ========== POWER SUMMATION ==========
create_sum_block(ax, 8, 9)
create_arrow(ax, 6.5, 10.1, 7.6, 9.3, 'Ppv')
create_arrow(ax, 6.5, 7.6, 7.6, 8.7, 'Pwind')

# Total Generation block
create_block(ax, 8.5, 8.5, 2, 0.8, 'Pgen = Ppv + Pwind', color_control)
create_arrow(ax, 8.4, 9, 8.8, 9.3)

# ========== LOAD DEMAND ==========
ax.text(1.5, 5.5, 'LOAD DEMAND', fontsize=10, fontweight='bold')
create_block(ax, 0.5, 4.5, 2, 0.8, 'Load Profile\nPload(t)', color_load)

# ========== POWER BALANCE ==========
create_sum_block(ax, 8, 6)
ax.text(7.5, 6.3, '+', fontsize=12, fontweight='bold')
ax.text(8.3, 5.7, '−', fontsize=14, fontweight='bold')

create_arrow(ax, 9.5, 8.7, 9.5, 6.3, 'Pgen')
create_arrow(ax, 2.5, 4.9, 8, 5.7, 'Pload')

# Power deficit/surplus
create_block(ax, 8.5, 5.5, 2.2, 0.8, 'ΔP = Pgen − Pload', color_control)
create_arrow(ax, 8.4, 6, 9, 6.3)

# ========== BATTERY MANAGEMENT SYSTEM ==========
ax.text(13, 11.5, 'ENERGY STORAGE SYSTEM', fontsize=10, fontweight='bold')

create_block(ax, 11.5, 8.5, 3, 2, 'BATTERY MANAGEMENT\nSYSTEM (BMS)\n\nCapacity: 100 kWh\nSOC: 20-95%\nη = 90%', color_storage)

create_arrow(ax, 10.5, 5.9, 11.5, 9, 'ΔP')

# SOC Feedback
create_block(ax, 15, 9, 2, 0.8, 'Unit Delay\nSOC(t-1)', color_control)
create_arrow(ax, 14.5, 9.5, 15, 9.4, 'SOC(t)')
create_arrow(ax, 15, 8.8, 14.8, 8.8, '', style='<-')
ax.add_patch(FancyArrowPatch((15, 8.8), (13, 8.2),
                            connectionstyle="arc3,rad=.3",
                            arrowstyle='<-',
                            color='blue',
                            linewidth=2,
                            mutation_scale=20))
ax.text(14.5, 7.8, 'SOC\nFeedback', fontsize=7, ha='center',
       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

# Battery outputs
create_arrow(ax, 13, 10.5, 13, 11.5, 'Pbatt')
create_arrow(ax, 13.5, 10.5, 13.5, 11.5, 'SOC')

# ========== DC BUS ==========
create_block(ax, 11.5, 5, 3, 1.2, 'DC BUS\nVdc = 400V\nPower Flow Control', '#FFE6F0')

# Connection to DC bus
create_arrow(ax, 13, 8.5, 13, 6.2, 'Pbatt')

# ========== MONITORING & CONTROL ==========
ax.text(18, 11.5, 'MONITORING', fontsize=10, fontweight='bold')

# Scopes
create_block(ax, 17.5, 9.8, 2, 0.8, 'Power Scope\n(4 signals)', color_output)
create_block(ax, 17.5, 8.5, 2, 0.8, 'SOC Scope', color_output)
create_block(ax, 17.5, 7.2, 2, 0.8, 'Voltage Monitor', color_output)

create_arrow(ax, 14.5, 9.5, 17.5, 10.2)
create_arrow(ax, 14.5, 9.3, 17.5, 8.9)
create_arrow(ax, 14.5, 5.6, 17.5, 7.6)

# ========== PROTECTION SYSTEM ==========
ax.text(5, 3, 'PROTECTION & CONTROL LAYER', fontsize=10, fontweight='bold')

create_block(ax, 3.5, 1.5, 3, 1, 'AI-BASED FAULT\nDETECTION\n(LSTM/CNN)', '#FFCCCC')
create_block(ax, 7, 1.5, 3, 1, 'ANOMALY\nDETECTION\n(Isolation Forest)', '#FFCCCC')
create_block(ax, 10.5, 1.5, 3, 1, 'ADAPTIVE RELAY\nCOORDINATION\n(DQN)', '#FFCCCC')

# Monitoring connections
create_arrow(ax, 13, 5, 5, 2.5)
create_arrow(ax, 13, 5, 8.5, 2.5)
create_arrow(ax, 13, 5, 12, 2.5)

# ========== SYSTEM OUTPUTS ==========
ax.text(1.5, 0.5, 'SYSTEM OUTPUTS', fontsize=10, fontweight='bold')

create_block(ax, 14.5, 0.3, 2, 0.6, 'Display: Ppv', color_output)
create_block(ax, 16.7, 0.3, 2, 0.6, 'Display: Pwind', color_output)

# ========== ANNOTATIONS ==========
# Legend
legend_y = 0.5
ax.text(0.3, legend_y+0.8, 'LEGEND:', fontsize=9, fontweight='bold')
patches_list = [
    (color_input, 'Environmental Inputs'),
    (color_renewable, 'Renewable Generation'),
    (color_storage, 'Energy Storage'),
    (color_control, 'Control Blocks'),
    (color_load, 'Load'),
    (color_output, 'Monitoring/Display')
]

y_offset = legend_y
for color, label in patches_list[:3]:
    rect = patches.Rectangle((0.3, y_offset-0.15), 0.3, 0.15,
                            facecolor=color, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    ax.text(0.7, y_offset-0.075, label, fontsize=7, va='center')
    y_offset -= 0.2

# Information box
info_text = """SIMULATION PARAMETERS:
• Solver: ODE45 (Variable-step)
• Duration: 86400s (24 hours)
• Max Step: 1 second
• PV: 100kW, η=18%
• Wind: 50kW, Vin=3m/s
• BESS: 200kWh, 20-90% SOC"""

ax.text(0.3, 3.5, info_text, fontsize=7,
       bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
       family='monospace', verticalalignment='top')

# Add grid reference
ax.text(19.5, 0.1, 'COEP Technological University\nNivas D. Navghare | Dr. Arti V. Tare', 
       fontsize=7, ha='right', style='italic')

plt.tight_layout()
plt.savefig('results/matlab_style/simulink_block_diagram.png', 
           dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Simulink block diagram created: results/matlab_style/simulink_block_diagram.png")
plt.close()

print("\n" + "="*70)
print("SIMULINK BLOCK DIAGRAM GENERATED")
print("="*70)
print("\nThe diagram shows:")
print("  • Environmental input blocks (Solar, Temperature, Wind)")
print("  • PV System with MPPT control")
print("  • Wind Turbine with power curve model")
print("  • Power summation and balance calculation")
print("  • Battery Management System with SOC tracking")
print("  • DC Bus voltage control")
print("  • Real-time monitoring scopes")
print("  • AI-based protection layer")
print("  • Display blocks for outputs")
print("="*70)
