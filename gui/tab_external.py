import webbrowser
import customtkinter as ctk

EXTERNAL_TOOLS = [
    {
        "category": "GPU Drivers & Optimization",
        "color": ("#c0392b", "#8b1a1a"),
        "tools": [
            {
                "name": "DDU — Display Driver Uninstaller",
                "description": "Completely removes GPU drivers before a clean reinstall. Essential before major driver updates.",
                "url": "https://www.wagnardsoft.com/",
            },
            {
                "name": "NVIDIA Inspector",
                "description": "Exposes advanced NVIDIA driver profile settings not available in the standard control panel.",
                "url": "https://github.com/Orbmu2k/nvidiaProfileInspector/releases",
            },
            {
                "name": "MSI Afterburner",
                "description": "GPU overclocking, fan curve control, and in-game frame time overlay (works on all GPU brands).",
                "url": "https://www.msi.com/Landing/afterburner/graphics-cards",
            },
        ],
    },
    {
        "category": "CPU & Memory",
        "color": ("#1a5fa8", "#144080"),
        "tools": [
            {
                "name": "Process Lasso",
                "description": "Fine-grained CPU priority and affinity management. ProBalance prevents CPU saturation during load spikes.",
                "url": "https://bitsum.com/",
            },
            {
                "name": "ISLC — Intelligent Standby List Cleaner",
                "description": "Monitors and purges Windows standby memory before it causes stutters from page faults in games.",
                "url": "https://www.wagnardsoft.com/",
            },
        ],
    },
    {
        "category": "Benchmarking & Diagnostics",
        "color": ("#6d3bbf", "#4a2880"),
        "tools": [
            {
                "name": "LatencyMon",
                "description": "Real-time DPC and ISR latency analysis. Use this to diagnose audio glitches and game stutter caused by drivers.",
                "url": "https://www.resplendence.com/latencymon",
            },
            {
                "name": "HWiNFO64",
                "description": "Detailed real-time hardware sensor monitoring — temperatures, clocks, voltages, and power draw.",
                "url": "https://www.hwinfo.com/download/",
            },
            {
                "name": "CrystalDiskMark",
                "description": "Storage read/write speed benchmark. Confirms NVMe speeds after driver or firmware changes.",
                "url": "https://crystalmark.info/en/software/crystaldiskmark/",
            },
            {
                "name": "CPU-Z",
                "description": "Detailed CPU, RAM timings, XMP/EXPO profile info, and motherboard specifications.",
                "url": "https://www.cpuid.com/softwares/cpu-z.html",
            },
        ],
    },
    {
        "category": "Network",
        "color": ("#b8660a", "#8a4c08"),
        "tools": [
            {
                "name": "NetLimiter",
                "description": "Per-process bandwidth throttling and monitoring. Prevents background updates from spiking game ping.",
                "url": "https://www.netlimiter.com/",
            },
        ],
    },
    {
        "category": "Game-Specific Tools",
        "color": ("#1a7a4a", "#145c38"),
        "tools": [
            {
                "name": "Special K",
                "description": "Per-game framerate limiter, HDR injection, texture modding, and latency reduction — no game modification needed.",
                "url": "https://wiki.special-k.info/",
            },
            {
                "name": "Lossless Scaling",
                "description": "Frame generation for older games using AI upscaling — adds FSR/DLSS-style frame interpolation to any title.",
                "url": "https://store.steampowered.com/app/993090/Lossless_Scaling/",
            },
            {
                "name": "Rivatuner Statistics Server (RTSS)",
                "description": "The gold-standard framerate limiter. Tighter than in-engine limiters — reduces latency and eliminates tearing.",
                "url": "https://www.guru3d.com/download/rtss-rivatuner-statistics-server-download/",
            },
        ],
    },
]


class ExternalToolsTab:
    def __init__(self, parent):
        self._build(parent)

    def _build(self, parent):
        # Header banner
        banner = ctk.CTkFrame(parent, fg_color=("#fff3cd", "#3d2e00"), corner_radius=8)
        banner.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkLabel(
            banner,
            text="🔗  These tools cannot be applied automatically. "
            "Click any button to open the tool's official website in your browser.",
            text_color=("#7d5a00", "#ffcc44"),
            font=ctk.CTkFont(size=12),
            wraplength=860,
            justify="left",
        ).pack(padx=10, pady=6, anchor="w")

        scroll = ctk.CTkScrollableFrame(parent, label_text="External Tools & Resources")
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        for section in EXTERNAL_TOOLS:
            self._add_section(scroll, section)

    def _add_section(self, parent, section: dict):
        # Section header
        hdr = ctk.CTkFrame(
            parent, fg_color=("gray80", "gray22"), corner_radius=6, height=32
        )
        hdr.pack(fill="x", padx=4, pady=(12, 6))
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr,
            text=section["category"],
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(side="left", padx=12)

        for tool in section["tools"]:
            self._add_tool_row(parent, tool, section["color"])

    def _add_tool_row(self, parent, tool: dict, color: tuple):
        row = ctk.CTkFrame(parent, fg_color=("gray93", "gray17"), corner_radius=6)
        row.pack(fill="x", padx=4, pady=3)

        # Left: name + description
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(12, 6), pady=8)

        ctk.CTkLabel(
            left,
            text=tool["name"],
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=tool["description"],
            font=ctk.CTkFont(size=11),
            text_color=("gray45", "gray60"),
            anchor="w",
            wraplength=620,
            justify="left",
        ).pack(anchor="w", pady=(1, 0))

        # Right: Open button
        url = tool["url"]
        ctk.CTkButton(
            row,
            text="Open ↗",
            width=86,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=color,
            hover_color=("gray40", "gray30"),
            command=lambda u=url: webbrowser.open(u),
        ).pack(side="right", padx=12, pady=8)
