"""Widget construction and Tk variable helpers for the GUI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import tkinter as tk
from tkinter import ttk

from .config import DEFAULT_CANVAS_HEIGHT, DEFAULT_CANVAS_WIDTH, MODE_PATTERNS


@dataclass
class TkVars:
    """Container for the Tkinter variables shared across widgets."""

    mode: tk.StringVar
    pattern: tk.StringVar
    speed: tk.IntVar
    grid_size: tk.StringVar
    custom_width: tk.IntVar
    custom_height: tk.IntVar
    draw_mode: tk.StringVar
    symmetry: tk.StringVar


@dataclass
class Widgets:
    """References to widgets that the application interacts with later."""

    start_button: tk.Button
    pattern_combo: ttk.Combobox
    birth_entry: tk.Entry
    survival_entry: tk.Entry
    apply_rules_button: tk.Button
    gen_label: tk.Label
    population_label: tk.Label
    canvas: tk.Canvas


@dataclass
class Callbacks:
    """Callback definitions for UI events."""

    switch_mode: Callable[[str], None]
    step_once: Callable[[], None]
    clear_grid: Callable[[], None]
    reset_simulation: Callable[[], None]
    load_pattern: Callable[[], None]
    save_pattern: Callable[[], None]
    load_saved_pattern: Callable[[], None]
    export_png: Callable[[], None]
    apply_custom_rules: Callable[[], None]
    size_preset_changed: Callable[[tk.Event[tk.Misc]], None]
    apply_custom_size: Callable[[], None]
    toggle_grid: Callable[[], None]
    on_canvas_click: Callable[[tk.Event[tk.Misc]], None]
    on_canvas_drag: Callable[[tk.Event[tk.Misc]], None]


def build_ui(
    root: tk.Tk,
    variables: TkVars,
    callbacks: Callbacks,
    show_export: bool,
) -> Widgets:
    """Create the Tkinter widget layout and wire up callbacks."""

    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure("Card.TLabelframe", padding=8)
    style.configure("Card.TFrame", padding=8)

    shell = ttk.Frame(root, padding=10)
    shell.pack(fill=tk.BOTH, expand=True)

    shell.columnconfigure(1, weight=1)
    shell.rowconfigure(0, weight=1)

    sidebar = ttk.Frame(shell, style="Card.TFrame")
    sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 10))

    content = ttk.Frame(shell)
    content.grid(row=0, column=1, sticky="nsew")
    content.rowconfigure(0, weight=1)
    content.columnconfigure(0, weight=1)

    # Mode and pattern selection
    mode_frame = ttk.Labelframe(
        sidebar,
        text="Automaton",
        style="Card.TLabelframe",
    )
    mode_frame.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(mode_frame, text="Mode").pack(anchor=tk.W)
    mode_combo = ttk.Combobox(
        mode_frame,
        textvariable=variables.mode,
        state="readonly",
        values=list(MODE_PATTERNS.keys()),
    )
    mode_combo.pack(fill=tk.X, pady=(2, 6))
    mode_combo.bind(
        "<<ComboboxSelected>>",
        lambda _event: callbacks.switch_mode(variables.mode.get()),
    )

    ttk.Label(mode_frame, text="Pattern").pack(anchor=tk.W)
    pattern_combo = ttk.Combobox(
        mode_frame,
        textvariable=variables.pattern,
        state="readonly",
    )
    pattern_combo.pack(fill=tk.X, pady=(2, 6))
    pattern_combo.bind(
        "<<ComboboxSelected>>",
        lambda _event: callbacks.load_pattern(),
    )

    pattern_actions = ttk.Frame(mode_frame)
    pattern_actions.pack(fill=tk.X, pady=(4, 0))
    ttk.Button(
        pattern_actions,
        text="Save",
        command=callbacks.save_pattern,
    ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
    ttk.Button(
        pattern_actions,
        text="Load",
        command=callbacks.load_saved_pattern,
    ).pack(side=tk.LEFT, expand=True, fill=tk.X)
    if show_export:
        ttk.Button(
            mode_frame,
            text="Export PNG",
            command=callbacks.export_png,
        ).pack(fill=tk.X, pady=(6, 0))

    # Simulation controls
    sim_frame = ttk.Labelframe(
        sidebar,
        text="Simulation",
        style="Card.TLabelframe",
    )
    sim_frame.pack(fill=tk.X, pady=(0, 10))

    sim_toolbar = ttk.Frame(sim_frame)
    sim_toolbar.pack(fill=tk.X)

    start_button = tk.Button(
        sim_toolbar,
        text="Start",
        command=lambda: None,  # replaced by caller
        width=9,
        bg="#4caf50",
        fg="white",
        relief=tk.FLAT,
    )
    start_button.pack(side=tk.LEFT, padx=(0, 6))

    ttk.Button(
        sim_toolbar,
        text="Step",
        command=callbacks.step_once,
        width=7,
    ).pack(side=tk.LEFT)
    ttk.Button(
        sim_toolbar,
        text="Clear",
        command=callbacks.clear_grid,
        width=7,
    ).pack(side=tk.LEFT, padx=(6, 0))
    ttk.Button(
        sim_toolbar,
        text="Reset",
        command=callbacks.reset_simulation,
        width=7,
    ).pack(side=tk.LEFT, padx=(6, 0))

    ttk.Label(sim_frame, text="Speed").pack(anchor=tk.W, pady=(8, 2))
    tk.Scale(
        sim_frame,
        from_=1,
        to=100,
        orient=tk.HORIZONTAL,
        variable=variables.speed,
        length=200,
        showvalue=False,
    ).pack(fill=tk.X)

    ttk.Button(
        sim_frame,
        text="Toggle Grid",
        command=callbacks.toggle_grid,
    ).pack(fill=tk.X, pady=(8, 0))

    gen_label = ttk.Label(
        sim_frame,
        text="Generation: 0",
        font=("Arial", 10, "bold"),
    )
    gen_label.pack(anchor=tk.W, pady=(8, 0))

    stats_frame = ttk.Labelframe(
        sidebar,
        text="Population",
        style="Card.TLabelframe",
    )
    stats_frame.pack(fill=tk.X, pady=(0, 10))
    population_label = ttk.Label(
        stats_frame,
        text="Live: 0 | Δ: +0 | Peak: 0 | Density: 0.0%",
        wraplength=220,
        justify=tk.LEFT,
    )
    population_label.pack(anchor=tk.W)

    # Custom rules
    rules_frame = ttk.Labelframe(
        sidebar,
        text="Custom Rules",
        style="Card.TLabelframe",
    )
    rules_frame.pack(fill=tk.X, pady=(0, 10))

    rule_row = ttk.Frame(rules_frame)
    rule_row.pack(fill=tk.X)
    ttk.Label(rule_row, text="B").pack(side=tk.LEFT)
    birth_entry = ttk.Entry(rule_row, width=8)
    birth_entry.pack(side=tk.LEFT, padx=(4, 12))
    ttk.Label(rule_row, text="S").pack(side=tk.LEFT)
    survival_entry = ttk.Entry(rule_row, width=8)
    survival_entry.pack(side=tk.LEFT, padx=(4, 0))

    apply_rules_button = ttk.Button(
        rules_frame,
        text="Apply",
        command=callbacks.apply_custom_rules,
    )
    apply_rules_button.pack(fill=tk.X, pady=(6, 0))

    # Grid sizing
    grid_frame = ttk.Labelframe(
        sidebar,
        text="Grid",
        style="Card.TLabelframe",
    )
    grid_frame.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(grid_frame, text="Preset").pack(anchor=tk.W)
    size_combo = ttk.Combobox(
        grid_frame,
        textvariable=variables.grid_size,
        state="readonly",
        values=["50x50", "100x100", "150x150", "200x200", "Custom"],
    )
    size_combo.pack(fill=tk.X, pady=(2, 6))
    size_combo.bind("<<ComboboxSelected>>", callbacks.size_preset_changed)

    custom_row = ttk.Frame(grid_frame)
    custom_row.pack(fill=tk.X)
    ttk.Label(custom_row, text="W").pack(side=tk.LEFT)
    tk.Spinbox(
        custom_row,
        from_=10,
        to=500,
        textvariable=variables.custom_width,
        width=5,
    ).pack(side=tk.LEFT, padx=(4, 12))
    ttk.Label(custom_row, text="H").pack(side=tk.LEFT)
    tk.Spinbox(
        custom_row,
        from_=10,
        to=500,
        textvariable=variables.custom_height,
        width=5,
    ).pack(side=tk.LEFT, padx=(4, 0))

    ttk.Button(
        grid_frame,
        text="Apply",
        command=callbacks.apply_custom_size,
    ).pack(fill=tk.X, pady=(6, 0))

    # Drawing controls
    draw_frame = ttk.Labelframe(
        sidebar,
        text="Drawing",
        style="Card.TLabelframe",
    )
    draw_frame.pack(fill=tk.X)

    ttk.Label(draw_frame, text="Tool").pack(anchor=tk.W)
    tools_row = ttk.Frame(draw_frame)
    tools_row.pack(anchor=tk.W, pady=(2, 6))
    ttk.Radiobutton(
        tools_row,
        text="Toggle",
        variable=variables.draw_mode,
        value="toggle",
    ).pack(side=tk.LEFT)
    ttk.Radiobutton(
        tools_row,
        text="Pen",
        variable=variables.draw_mode,
        value="pen",
    ).pack(side=tk.LEFT, padx=(8, 0))
    ttk.Radiobutton(
        tools_row,
        text="Eraser",
        variable=variables.draw_mode,
        value="eraser",
    ).pack(side=tk.LEFT, padx=(8, 0))

    ttk.Label(draw_frame, text="Symmetry").pack(anchor=tk.W)
    ttk.Combobox(
        draw_frame,
        textvariable=variables.symmetry,
        state="readonly",
        values=["None", "Horizontal", "Vertical", "Both", "Radial"],
    ).pack(fill=tk.X, pady=(2, 0))

    # Canvas area
    canvas_frame = ttk.Frame(content)
    canvas_frame.grid(row=0, column=0, sticky="nsew")

    canvas = tk.Canvas(
        canvas_frame,
        bg="white",
        width=DEFAULT_CANVAS_WIDTH,
        height=DEFAULT_CANVAS_HEIGHT,
        highlightthickness=1,
        highlightbackground="#cccccc",
    )
    h_scroll = ttk.Scrollbar(
        canvas_frame,
        orient=tk.HORIZONTAL,
        command=canvas.xview,
    )
    v_scroll = ttk.Scrollbar(
        canvas_frame,
        orient=tk.VERTICAL,
        command=canvas.yview,
    )
    canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
    canvas.grid(row=0, column=0, sticky=tk.NSEW)
    h_scroll.grid(row=1, column=0, sticky=tk.EW, pady=(4, 0))
    v_scroll.grid(row=0, column=1, sticky=tk.NS, padx=(4, 0))

    canvas_frame.rowconfigure(0, weight=1)
    canvas_frame.columnconfigure(0, weight=1)

    canvas.bind("<Button-1>", callbacks.on_canvas_click)
    canvas.bind("<B1-Motion>", callbacks.on_canvas_drag)

    return Widgets(
        start_button=start_button,
        pattern_combo=pattern_combo,
        birth_entry=birth_entry,
        survival_entry=survival_entry,
        apply_rules_button=apply_rules_button,
        gen_label=gen_label,
        population_label=population_label,
        canvas=canvas,
    )
