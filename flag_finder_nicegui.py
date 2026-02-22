from nicegui import ui 
import os, json
from PIL import Image

LOAD_BATCH = 60
current_results = []
shown_count = 0
loading_more = False

# -------------------------
# Load flags
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "flags.json"), "r", encoding="utf-8") as f:
    FLAGS = json.load(f)

def handle_scroll(e):
    global loading_more, shown_count

    if loading_more:
        return

    scroll_top = e.args.get('scrollTop', 0)
    client_height = e.args.get('clientHeight', 0)
    scroll_height = e.args.get('scrollHeight', 0)

    if scroll_top + client_height >= scroll_height - 50:
        if shown_count < len(current_results):
            loading_more = True
            display_flags(append=True)


# -------------------------
# Containers
# -------------------------
search_card = None
result_container = ui.column().style(
    'margin:20px; gap:10px; align-items:flex-start; '
    'height:89vh; overflow-y:auto;'
)

result_container.on('scroll', handle_scroll)

reset_button = ui.button('Reset', on_click=lambda: reset_view()).style(
    'position:fixed; top:20px; right:20px; font-size:16px; '
    'background:#f44336; color:white; padding:10px 20px; display:none'
)

details_dialog = ui.dialog().style(
    'min-width:400px; background:white; padding:20px; border-radius:8px'
)

with details_dialog:
    with ui.column().style('gap:10px'):

        details_title = ui.label().style(
            'font-weight:bold; font-size:18px'
        )

        details_image = ui.image().style(
            'width:100%; height:100%'
        )

        details_colours = ui.label()
        details_patterns = ui.label()
        details_text = ui.label()

# -------------------------
# Functions
# -------------------------
def search(colours, patterns):
    results = []
    for flag in FLAGS:
        if colours and not all(c in flag["colours"] for c in colours):
            continue
        if patterns and not all(p in flag["patterns"] for p in patterns):
            continue
        results.append(flag)
    return results

def display_flags(results=None, append=False):
    global shown_count, current_results, loading_more

    if results is not None:
        current_results = results

    if not append:
        result_container.clear()
        shown_count = 0

    with result_container:
        with ui.row().style('flex-wrap: wrap; gap:20px; justify-content:flex-start;'):
            for flag in current_results[shown_count:shown_count + LOAD_BATCH]:
                with ui.column().style('width:100px; align-items:center;'):
                    img_path = os.path.join(BASE_DIR, flag["file"])
                    ui.image(img_path).style('width:80px; height:50px').props('loading="lazy"')
                    ui.label(flag["country"]).style('text-align:center; font-size:14px')

                    ui.button(
                        'Details',
                        on_click=lambda f=flag: show_flag_details(f)
                    ).style('font-size:12px; margin-top:5px')

    shown_count += LOAD_BATCH
    loading_more = False

def show_flag_details(flag):
    details_title.set_text(flag["country"])
    details_image.set_source(os.path.join(BASE_DIR, flag["file"]))
    details_colours.set_text(f"Colours: {', '.join(flag['colours'])}")
    details_patterns.set_text(f"Patterns: {', '.join(flag['patterns'])}")
    details_text.set_text(flag.get("details") or flag.get("fun_fact") or "Every flag has a story!")
    details_dialog.open()

def apply_filter(colours=None, pattern=None, dialog=None):
    global current_results, shown_count

    reset_button.style('display:block')
    search_card.style('display:none')

    cols = colours or [c.strip().lower() for c in search_colours.value.split(',') if c.strip()]
    pats = [pattern] if pattern else [p.strip().lower() for p in search_patterns.value.split(',') if p.strip()]

    current_results = search(cols, pats)
    shown_count = 0  # IMPORTANT RESET

    display_flags(current_results)

    if dialog:
        dialog.close()

def reset_view():
    # Hide reset button
    reset_button.style('display:none')

    # Show search card again
    search_card.style('display:flex')

    # Clear previous results
    result_container.clear()

# -------------------------
# Help dialog
# -------------------------
def show_help():
    dialog = ui.dialog().style('min-width:600px; min-height:400px')
    with dialog:
        ui.label().style('font-weight:bold; font-size:18px; margin-bottom:10px')
        with ui.row().style('gap:50px;'):
            # Colours column
            with ui.column():
                ui.label("Available Colours:").style('font-weight:bold; font-size:16px')
                for colour in sorted({c for flag in FLAGS for c in flag["colours"]}):
                    with ui.row().style('align-items:center; gap:10px'):
                        ui.label(' ').style(f'background:{colour}; width:80px; height:50px; display:inline-block; border:none;')
                        ui.button(colour.capitalize(), on_click=lambda c=colour: apply_filter(colours=[c], dialog=dialog)).style(
                            'background:none; border:none; color:black; cursor:pointer; font-size:14px'
                        )
            # Patterns column
            with ui.column():
                ui.label("Available Patterns:").style('font-weight:bold; font-size:16px')
                for pattern in sorted({p for flag in FLAGS for p in flag["patterns"]}):
                    example_flag = next((f for f in FLAGS if pattern in f["patterns"]), None)
                    if example_flag:
                        img_path = os.path.join(BASE_DIR, example_flag["file"])
                        with ui.row().style('align-items:center; gap:10px'):
                            ui.image(img_path).style('width:80px; height:50px')
                            ui.button(pattern.capitalize(), on_click=lambda p=pattern: apply_filter(pattern=p, dialog=dialog))

    dialog.open()

# -------------------------
# Styling
# -------------------------
ui.add_head_html("""
<style>
body {
    margin: 0;
    padding: 0;
    height: 100%;
    box-sizing: border-box;
    background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 50%, #e0f7fa 100%);
    font-family: Arial, sans-serif;
}

/* Add subtle texture using semi-transparent overlay */
body::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: radial-gradient(rgba(255,255,255,0.1) 1px, transparent 1px);
    background-size: 20px 20px;
    pointer-events: none;
}

/* Card hover effect */
.ui-card:hover {
    box-shadow: 0 12px 25px rgba(0,0,0,0.18);
    transform: translateY(-3px);
    transition: all 0.2s ease;
}

/* Labels and inputs styling */
.ui-input, .ui-label {
    font-family: Arial, sans-serif;
}

/* Responsive design */
@media (max-width: 600px) {
    .ui-card {
        padding: 20px;
        min-width: 90%;
    }
    .ui-input, .ui-label {
        font-size: 14px;
        width: 80%;
    }
    .ui-button {
        font-size: 14px;
        width: 80%;
    }
}
</style>
""")

# -------------------------
# Main layout
# -------------------------
# Search card - fixed in viewport for perfect centering
with ui.card().style(
    'position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); '
    'padding:40px; min-width:400px; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.1)'
) as card:
    search_card = card

    ui.label("🌍 Flag Finder").style('font-size:36px; font-weight:bold; margin-bottom:25px')
    search_colours = ui.input(label='Colours (comma-separated)').style('font-size:16px; width:300px')
    search_patterns = ui.input(label='Patterns (comma-separated)').style('font-size:16px; width:300px')

    with ui.row().style('gap:20px; justify-content:center; margin-top:25px'):
        ui.button('Search', on_click=lambda: apply_filter()).style('font-size:16px; width:100px')
        ui.button('Help', on_click=show_help).style('font-size:16px; width:100px')

# -------------------------
# Place scrollable result container below
# -------------------------
result_container

ui.run(title="Flag Finder")