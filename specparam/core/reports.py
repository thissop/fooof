"""Generate reports from model objects."""

from specparam.core.io import fname, fpath
from specparam.core.modutils import safe_import, check_dependency
from specparam.core.strings import (gen_settings_str, gen_model_results_str,
                                    gen_group_results_str, gen_time_results_str,
                                    gen_event_results_str)
from specparam.data.utils import get_periodic_labels
from specparam.plts.group import (plot_group_aperiodic, plot_group_goodness,
                                  plot_group_peak_frequencies)

plt = safe_import('.pyplot', 'matplotlib')
gridspec = safe_import('.gridspec', 'matplotlib')

###################################################################################################
###################################################################################################

## Settings & Globals
REPORT_FIGSIZE = (16, 20)
REPORT_FONT = {'family': 'monospace',
               'weight': 'normal',
               'size': 16}
SAVE_FORMAT = 'pdf'

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def save_model_report(model, file_name, file_path=None, add_settings=True, **plot_kwargs):
    """Generate and save out a PDF report for a power spectrum model fit.

    Parameters
    ----------
    model : SpectralModel
        Object with results from fitting a power spectrum.
    file_name : str
        Name to give the saved out file.
    file_path : str, optional
        Path to directory to save to. If None, saves to current directory.
    add_settings : bool, optional, default: True
        Whether to add a print out of the model settings to the end of the report.
    plot_kwargs : keyword arguments
        Keyword arguments to pass into the plot method.
    """

    # Define grid settings based on what is to be plotted
    n_rows = 3 if add_settings else 2
    height_ratios = [0.5, 1.0, 0.25] if add_settings else [0.45, 1.0]

    # Set up outline figure, using gridspec
    _ = plt.figure(figsize=REPORT_FIGSIZE)
    grid = gridspec.GridSpec(n_rows, 1, hspace=0.25, height_ratios=height_ratios)

    # First - text results
    ax0 = plt.subplot(grid[0])
    results_str = gen_model_results_str(model)
    ax0.text(0.5, 0.7, results_str, REPORT_FONT, ha='center', va='center')
    ax0.set_frame_on(False)
    ax0.set(xticks=[], yticks=[])

    # Second - data plot
    ax1 = plt.subplot(grid[1])
    model.plot(ax=ax1, **plot_kwargs)

    # Third - model settings
    if add_settings:
        ax2 = plt.subplot(grid[2])
        settings_str = gen_settings_str(model, False)
        ax2.text(0.5, 0.1, settings_str, REPORT_FONT, ha='center', va='center')
        ax2.set_frame_on(False)
        ax2.set(xticks=[], yticks=[])

    # Save out the report
    plt.savefig(fpath(file_path, fname(file_name, SAVE_FORMAT)))
    plt.close()


@check_dependency(plt, 'matplotlib')
def save_group_report(group, file_name, file_path=None, add_settings=True):
    """Generate and save out a PDF report for models of a group of power spectra.

    Parameters
    ----------
    group : SpectralGroupModel
        Object with results from fitting a group of power spectra.
    file_name : str
        Name to give the saved out file.
    file_path : str, optional
        Path to directory to save to. If None, saves to current directory.
    add_settings : bool, optional, default: True
        Whether to add a print out of the model settings to the end of the report.
    """

    # Define grid settings based on what is to be plotted
    n_rows = 4 if add_settings else 3
    height_ratios = [1.0, 1.0, 1.0, 0.5] if add_settings else [0.8, 1.0, 1.0]

    # Initialize figure
    _ = plt.figure(figsize=REPORT_FIGSIZE)
    grid = gridspec.GridSpec(n_rows, 2, wspace=0.4, hspace=0.25, height_ratios=height_ratios)

    # First / top: text results
    ax0 = plt.subplot(grid[0, :])
    results_str = gen_group_results_str(group)
    ax0.text(0.5, 0.7, results_str, REPORT_FONT, ha='center', va='center')
    ax0.set_frame_on(False)
    ax0.set(xticks=[], yticks=[])

    # Second - data plots

    # Aperiodic parameters plot
    ax1 = plt.subplot(grid[1, 0])
    plot_group_aperiodic(group, ax1)

    # Goodness of fit plot
    ax2 = plt.subplot(grid[1, 1])
    plot_group_goodness(group, ax2)

    # Peak center frequencies plot
    ax3 = plt.subplot(grid[2, :])
    plot_group_peak_frequencies(group, ax3)

    # Third - Model settings
    if add_settings:
        ax4 = plt.subplot(grid[3, :])
        settings_str = gen_settings_str(group, False)
        ax4.text(0.5, 0.1, settings_str, REPORT_FONT, ha='center', va='center')
        ax4.set_frame_on(False)
        ax4.set(xticks=[], yticks=[])

    # Save out the report
    plt.savefig(fpath(file_path, fname(file_name, SAVE_FORMAT)))
    plt.close()


@check_dependency(plt, 'matplotlib')
def save_time_report(time_model, file_name, file_path=None, add_settings=True):
    """Generate and save out a PDF report for models of a spectrogram.

    Parameters
    ----------
    time_model : SpectralTimeModel
        Object with results from fitting a spectrogram.
    file_name : str
        Name to give the saved out file.
    file_path : str, optional
        Path to directory to save to. If None, saves to current directory.
    add_settings : bool, optional, default: True
        Whether to add a print out of the model settings to the end of the report.
    """

    # Check model object for number of bands, to decide report size
    pe_labels = get_periodic_labels(time_model.time_results)
    n_bands = len(pe_labels['cf'])

    # Initialize figure, defining number of axes based on model + what is to be plotted
    n_rows = 1 + 2 + n_bands + (1 if add_settings else 0)
    height_ratios = [1.0] + [0.5] * (n_bands + 2) + ([0.4] if add_settings else [])
    _, axes = plt.subplots(n_rows, 1,
                           gridspec_kw={'hspace' : 0.35, 'height_ratios' : height_ratios},
                           figsize=REPORT_FIGSIZE)

    # First / top: text results
    results_str = gen_time_results_str(time_model)
    axes[0].text(0.5, 0.7, results_str, REPORT_FONT, ha='center', va='center')
    axes[0].set_frame_on(False)
    axes[0].set(xticks=[], yticks=[])

    # Second - data plots
    time_model.plot(axes=axes[1:2+n_bands+1])

    # Third - Model settings
    if add_settings:
        settings_str = gen_settings_str(time_model, False)
        axes[-1].text(0.5, 0.1, settings_str, REPORT_FONT, ha='center', va='center')
        axes[-1].set_frame_on(False)
        axes[-1].set(xticks=[], yticks=[])

    # Save out the report
    plt.savefig(fpath(file_path, fname(file_name, SAVE_FORMAT)))
    plt.close()


@check_dependency(plt, 'matplotlib')
def save_event_report(event_model, file_name, file_path=None, add_settings=True):
    """Generate and save out a PDF report for models of a set of events.

    Parameters
    ----------
    event_model : SpectralTimeEventModel
        Object with results from fitting a group of power spectra.
    file_name : str
        Name to give the saved out file.
    file_path : str, optional
        Path to directory to save to. If None, saves to current directory.
    add_settings : bool, optional, default: True
        Whether to add a print out of the model settings to the end of the report.
    """

    # Check model object for number of bands & aperiodic mode, to decide report size
    pe_labels = get_periodic_labels(event_model.event_time_results)
    n_bands = len(pe_labels['cf'])
    has_knee = 'knee' in event_model.event_time_results.keys()

    # Initialize figure, defining number of axes based on model + what is to be plotted
    n_rows = 1 + (4 if has_knee else 3) + (n_bands * 4) + 2 + (1 if add_settings else 0)
    height_ratios = [2.75] + [1] * (3 if has_knee else 2) + \
        [0.25, 1, 1, 1] * n_bands + [0.25] + [1, 1] + ([1.5] if add_settings else [])
    _, axes = plt.subplots(n_rows, 1,
                           gridspec_kw={'hspace' : 0.1, 'height_ratios' : height_ratios},
                           figsize=(REPORT_FIGSIZE[0], REPORT_FIGSIZE[1] + 6))

    # First / top: text results
    results_str = gen_event_results_str(event_model)
    axes[0].text(0.5, 0.7, results_str, REPORT_FONT, ha='center', va='center')
    axes[0].set_frame_on(False)
    axes[0].set(xticks=[], yticks=[])

    # Second - data plots
    event_model.plot(axes=axes[1:-1])

    # Third - Model settings
    if add_settings:
        settings_str = gen_settings_str(event_model, False)
        axes[-1].text(0.5, 0.1, settings_str, REPORT_FONT, ha='center', va='center')
        axes[-1].set_frame_on(False)
        axes[-1].set(xticks=[], yticks=[])

    # Save out the report
    plt.savefig(fpath(file_path, fname(file_name, SAVE_FORMAT)))
    plt.close()
