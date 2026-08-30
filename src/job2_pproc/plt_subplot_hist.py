import plotly.graph_objects as go


def plt(
    plot_bgcolor: str = "white", paper_bgcolor: str = "ghostwhite"
) -> go.layout.Template:
    """Plotly template for subplot of histograms."""
    # x = 1 / 0
    plt = go.layout.Template()
    plt.layout = dict(
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        title_font=dict(family="Arial, sans-serif", size=18, color="RoyalBlue"),
        plot_bgcolor=plot_bgcolor,
        paper_bgcolor=paper_bgcolor,
    )
    return plt
