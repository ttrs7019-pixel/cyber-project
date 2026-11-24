"""Generate the figures used in the technical report.

Outputs PNG files into report/figures/ at 300 dpi.
"""
import json
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager as fm

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "figures")
os.makedirs(OUT, exist_ok=True)

for f in os.listdir(ASSETS):
    if f.endswith(".ttf"):
        fm.fontManager.addfont(os.path.join(ASSETS, f))

plt.rcParams["font.family"] = "IBM Plex Sans"
SANS = "IBM Plex Sans"
MONO = "IBM Plex Mono"

NAVY = "#1F3A5F"
SLATE = "#44546A"
GREY = "#8A94A6"
LIGHT = "#EDF1F6"
GREEN = "#2F6B4F"
RUST = "#9C3B2E"
INK = "#1A1A1A"


class Canvas:
    """Small helper: a 0..1 x 0..1 axes with point-accurate vertical offsets."""

    def __init__(self, w_in, h_in):
        self.fig, self.ax = plt.subplots(figsize=(w_in, h_in))
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis("off")
        self.upp = 1.0 / (h_in * 72.0)      # data units per point

    def box(self, x, y, w, h, title, sub=None, fc="white", ec=NAVY, lw=1.1,
            title_size=9.4, sub_size=7.5, tcolor=INK, mono=False, radius=0.008):
        self.ax.add_patch(FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0,rounding_size={radius}",
            linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2))
        sub_lines = sub.split("\n") if sub else []
        th = title_size * 1.32
        sh = len(sub_lines) * sub_size * 1.46
        gap = 3.2 if sub_lines else 0.0
        total = th + gap + sh
        top = y + h / 2 + total / 2 * self.upp
        self.ax.text(x + w / 2, top, title, ha="center", va="top",
                     fontsize=title_size, color=tcolor, fontweight="semibold",
                     family=MONO if mono else SANS, zorder=3)
        if sub_lines:
            self.ax.text(x + w / 2, top - (th + gap) * self.upp, sub,
                         ha="center", va="top", fontsize=sub_size, color=SLATE,
                         linespacing=1.46, zorder=3)

    def arrow(self, p1, p2, color=NAVY, style="-|>", lw=1.05, ls="-",
              rad=0.0, shrink=3):
        self.ax.add_patch(FancyArrowPatch(
            p1, p2, arrowstyle=style, mutation_scale=8.5, linewidth=lw,
            color=color, linestyle=ls, connectionstyle=f"arc3,rad={rad}",
            zorder=1, shrinkA=shrink, shrinkB=shrink))

    def text(self, x, y, s, size=7.4, color=SLATE, ha="center", va="center",
             mono=False, italic=False, weight="normal", spacing=1.42, bg=True):
        self.ax.text(x, y, s, ha=ha, va=va, fontsize=size, color=color,
                     family=MONO if mono else SANS, style="italic" if italic else "normal",
                     fontweight=weight, linespacing=spacing, zorder=4,
                     bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="none",
                               alpha=0.94) if bg else None)

    def save(self, name, pad=0):
        self.fig.subplots_adjust(pad, pad, 1 - pad, 1 - pad)
        self.fig.savefig(os.path.join(OUT, name), dpi=300, facecolor="white")
        plt.close(self.fig)


# ---------------------------------------------------------------- figure 1
def architecture():
    c = Canvas(6.55, 3.30)
    ax = c.ax

    c.box(0.015, 0.330, 0.255, 0.430, "Client process",
          "client.py\nSSLContext (CERT_REQUIRED)\nSNI: localhost\nTLS 1.3 only")
    c.box(0.372, 0.330, 0.256, 0.430, "TCP transport",
          "127.0.0.1:8443\none request, one reply\nrecv() buffer 1024 B",
          fc=LIGHT, ec=SLATE)
    c.box(0.730, 0.330, 0.255, 0.430, "Server process",
          "server.py\nPROTOCOL_TLS_SERVER\ncertificate + private key\nlisten(1)")

    c.box(0.372, 0.070, 0.256, 0.195, "tls-keys.log",
          "NSS key-log format, 5 records", fc="white", ec=GREY, lw=0.9,
          title_size=8.6, sub_size=7.0)
    c.box(0.730, 0.070, 0.255, 0.195, "server.crt  /  server.key",
          "self-signed, CN = localhost\nRSA-2048, SHA-256", fc="white", ec=GREY,
          lw=0.9, title_size=8.6, sub_size=7.0, mono=False)

    y_up, y_dn = 0.615, 0.470
    c.arrow((0.272, y_up), (0.369, y_up))
    c.arrow((0.369, y_dn), (0.272, y_dn), color=GREY)
    c.arrow((0.630, y_up), (0.727, y_up))
    c.arrow((0.727, y_dn), (0.630, y_dn), color=GREY)

    c.text(0.3205, y_up + 0.052, "app data", size=6.8, mono=True, color=NAVY)
    c.text(0.3205, y_dn - 0.052, "app data", size=6.8, mono=True, color=GREY)
    c.text(0.6785, y_up + 0.052, "records", size=6.8, mono=True, color=NAVY)
    c.text(0.6785, y_dn - 0.052, "records", size=6.8, mono=True, color=GREY)

    c.arrow((0.142, 0.327), (0.470, 0.268), color=GREY, ls=(0, (2.2, 2.2)),
            lw=0.9, rad=-0.10)
    c.arrow((0.857, 0.327), (0.857, 0.268), color=GREY, ls=(0, (2.2, 2.2)), lw=0.9)

    c.text(0.015, 0.930,
           "The client trusts only the certificate handed to it at start-up (cafile=\"server.crt\"); "
           "no public CA is involved.",
           size=7.2, ha="left", italic=True)
    c.text(0.985, 0.930, "Fig. 1", size=7.2, ha="right", italic=True, color=GREY)

    c.save("fig1_architecture.png")


# ---------------------------------------------------------------- figure 2
def handshake():
    """Sequence diagram. Layout is computed in points so nothing collides."""
    H_IN = 4.10
    c = Canvas(6.55, H_IN)
    ax = c.ax
    pt = c.upp                      # axes units per point

    c.box(0.030, 0.940, 0.185, 0.052, "Client", fc=LIGHT, title_size=8.6)
    c.box(0.785, 0.940, 0.185, 0.052, "Server", fc=LIGHT, title_size=8.6)
    for x in (0.1225, 0.8775):
        ax.plot([x, x], [0.935, 0.045], color=GREY, linewidth=0.9,
                linestyle=(0, (3, 3)), zorder=1)

    steps = [
        ("ClientHello",
         "TLS 1.3 only, key_share = X25519, SNI = localhost", True),
        ("ServerHello",
         "version + TLS_AES_256_GCM_SHA384 + server key share", False),
        ("{EncryptedExtensions} {Certificate} {CertificateVerify} {Finished}",
         "certificate chain and RSA-PSS signature over the transcript", False),
        ("{Finished}",
         "client validates the chain and proves knowledge of the keys", True),
        ("[Application Data]",
         "\"Hello from secure client!\"  (AEAD protected)", True),
        ("[Application Data]",
         "\"Hello from secure server!\"  then FIN", False),
    ]

    lab_size, note_size = 6.85, 6.35
    pad = 5.0 * pt
    label_h = lab_size * 1.30 * pt
    note_h = note_size * 1.30 * pt
    block = label_h + note_h + 2 * pad
    top, bottom = 0.880, 0.105
    pitch = (top - bottom) / len(steps)

    for i, (label, note, c2s) in enumerate(steps):
        yc = top - i * pitch - pitch / 2 + (label_h + note_h) / 2 - note_h / 2 - pad * 0.4
        x1, x2 = (0.132, 0.868) if c2s else (0.868, 0.132)
        c.arrow((x1, yc), (x2, yc), color=NAVY if c2s else GREEN, lw=1.0, shrink=0)
        ha = "left" if c2s else "right"
        xt = 0.142 if c2s else 0.858
        c.text(xt, yc + pad * 0.55, label, size=lab_size, mono=True, color=INK,
               ha=ha, va="bottom")
        c.text(xt, yc - pad * 0.55, note, size=note_size, color=SLATE, ha=ha,
               va="top")

    c.text(0.5, 0.012,
           "Records are in clear until ServerHello; EncryptedExtensions onward is protected.  "
           "Resumption and 0-RTT are not enabled.",
           size=6.6, italic=True)

    c.save("fig2_handshake.png")


# ---------------------------------------------------------------- figure 3
def latency():
    samples = json.load(open(os.path.join(DATA, "handshake_ms.json")))
    med = statistics.median(samples)
    mean = statistics.mean(samples)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.55, 2.35),
                                   gridspec_kw={"width_ratios": [2.25, 1]})

    bins = [1.35, 1.5, 1.6, 1.7, 1.8, 1.95, 2.15, 2.45, 3.0, 6.0]
    ax1.hist(samples, bins=bins, color=LIGHT, edgecolor=NAVY, linewidth=0.9,
             rwidth=0.9, zorder=2)
    ax1.axvline(med, color=RUST, linewidth=1.2, zorder=3)
    ax1.annotate(f"median {med:.2f} ms", xy=(med, 0.72), xycoords=("data", "axes fraction"),
                 xytext=(6, 0), textcoords="offset points", color=RUST, fontsize=7.4,
                 va="center")
    ax1.set_xlabel("handshake completion time, ms", fontsize=7.6, color=SLATE)
    ax1.set_ylabel("connections", fontsize=7.6, color=SLATE)
    ax1.set_title("(a) distribution of 30 handshakes", fontsize=8.4, color=INK,
                  loc="left", pad=6)
    for s in ("top", "right"):
        ax1.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax1.spines[s].set_color(GREY)
        ax1.spines[s].set_linewidth(0.8)
    ax1.tick_params(colors=SLATE, labelsize=7.2, width=0.8)
    ax1.grid(axis="y", color="#DCE2EA", linewidth=0.7)
    ax1.set_axisbelow(True)

    bp = ax2.boxplot(samples, widths=0.40, patch_artist=True, whis=(0, 100),
                     showfliers=False, orientation="vertical")
    for b in bp["boxes"]:
        b.set_facecolor(LIGHT)
        b.set_edgecolor(NAVY)
        b.set_linewidth(0.9)
    for b in bp["medians"]:
        b.set_color(RUST)
        b.set_linewidth(1.1)
    for k in ("whiskers", "caps"):
        for b in bp[k]:
            b.set_color(SLATE)
            b.set_linewidth(0.9)
    ax2.set_xticks([1])
    ax2.set_xticklabels(["n = 30"], fontsize=7.2)
    ax2.set_ylabel("ms", fontsize=7.6, color=SLATE)
    ax2.set_title("(b) spread", fontsize=8.4, color=INK, loc="left", pad=6)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax2.spines[s].set_color(GREY)
        ax2.spines[s].set_linewidth(0.8)
    ax2.tick_params(colors=SLATE, labelsize=7.2, width=0.8)
    ax2.grid(axis="y", color="#DCE2EA", linewidth=0.7)
    ax2.set_axisbelow(True)
    ax2.set_xlim(0.55, 1.55)
    ax2.annotate(f"max {max(samples):.2f}", xy=(1.18, max(samples)), xytext=(2, 0),
                 textcoords="offset points", ha="left", va="center", fontsize=6.8,
                 color=SLATE)
    ax2.annotate(f"min {min(samples):.2f}", xy=(1.18, min(samples)), xytext=(2, 0),
                 textcoords="offset points", ha="left", va="center", fontsize=6.8,
                 color=SLATE)
    ax2.set_xlim(0.62, 1.62)

    fig.tight_layout(pad=0.5)
    fig.savefig(os.path.join(OUT, "fig3_latency.png"), dpi=300, facecolor="white")
    plt.close(fig)
    print("latency: n=%d mean=%.2f median=%.2f min=%.2f max=%.2f"
          % (len(samples), mean, med, min(samples), max(samples)))


if __name__ == "__main__":
    architecture()
    handshake()
    latency()
    print("figures written to", OUT)
