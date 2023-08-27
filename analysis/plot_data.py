import matplotlib.pyplot as plt
from default_constants import DELAY_SAMPLES, FIGSIZE


def plot_inv_frac(df, delay_samples=DELAY_SAMPLES, title="untitled"):
    df = df[df.delay_samples == delay_samples]

    fig, (ax1_1, ax2) = plt.subplots(1, 2)
    fig.suptitle(title)
    fig.set_figwidth(FIGSIZE[0])
    fig.set_figheight(FIGSIZE[1])

    # Initial plot

    ax1_1.set_title(f"delay_samples={delay_samples}")
    ax1_1.set_xlabel("inv_frac")
    color = "tab:green"
    ax1_1.set_ylabel("Hitrate", color=color)
    ax1_1.plot(df.inv_frac, df.hitrate, color=color)
    ax1_1.tick_params(axis='y', labelcolor=color)

    ax1_2 = ax1_1.twinx()  # instantiate a second axes that shares the same x-axis
    color = "tab:red"
    ax1_2.set_ylabel("Misfires", color=color)  # we already handled the x-label with ax1
    ax1_2.plot(df.inv_frac, df.misfires, color=color)
    ax1_2.tick_params(axis='y', labelcolor=color)

    # Get and plot hitrates and misfire rates

    ax2.set_title(f"delay_samples={delay_samples}")
    ax2.set_xlabel("inv_frac")
    ax2.set_ylim([0, 1.05])
    ax2.plot(df.inv_frac, df.hitrate, label="Hitrate", color="tab:green", linestyle="dotted")
    ax2.plot(df.inv_frac, df.misfire_rate, label="Misfire Rate", color="tab:red", linestyle="dotted")
    ax2.legend()

    fig.tight_layout()  # Otherwise the right y-label is slightly clipped (for axis1)
    plt.show()

    return fig


def plot_all_3d(df, title="untitled"):
    fig, (ax1, ax2) = plt.subplots(1, 2,
                                   subplot_kw={"projection": "3d"},
                                   figsize=FIGSIZE)
    x = df.inv_frac
    y = df.delay_samples

    fig.suptitle(title)
    fig.tight_layout()

    ax1.set_title("Hitrate")
    cmap = plt.get_cmap("plasma")
    ax1.set_xlabel("inv_frac")
    ax1.set_ylabel("delay_samples")
    ax1.set_zlabel("hitrate")
    ax1.plot_trisurf(x, y, df.hitrate, cmap=cmap, linewidth=0.2)

    ax2.set_title("Misfire rate")
    cmap = plt.get_cmap("plasma_r")
    ax2.set_xlabel("inv_frac")
    ax2.set_ylabel("delay_samples")
    ax2.set_zlabel("misfire_rate")
    ax2.set_zlim([0, 1])
    ax2.plot_trisurf(x, y, df.misfire_rate, cmap=cmap, linewidth=0.2)
    plt.show()

    return fig


def plot_misfires(df, title="untitled"):
    """3D plot of misfires, useful for looking at noise."""
    fig, axis = plt.subplots(1, 1,
                           subplot_kw={"projection": "3d"},
                           figsize=FIGSIZE)
    x = df.inv_frac
    y = df.delay_samples

    fig.suptitle(title)
    fig.tight_layout()

    axis.set_title("Misfires")
    cmap = plt.get_cmap("plasma")
    axis.set_xlabel("inv_frac")
    axis.set_ylabel("delay_samples")
    axis.set_zlabel("misfires")
    axis.plot_trisurf(x, y, df.misfires, cmap=cmap, linewidth=0.2)

    return fig
