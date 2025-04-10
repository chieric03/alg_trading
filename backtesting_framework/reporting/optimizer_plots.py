import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import typing # Added import

def plot_optimization_heatmap(
    opt_result: typing.Any,
    all_param_names: list[str], # Added: List of all parameter names used in optimization
    param1_name: str,
    param2_name: str,
    metric_name: str = 'Objective Value',
    agg_func=np.max # Function to aggregate results if multiple runs have same params (max, min, mean)
):
    """
    Generates a heatmap visualizing the results of a backtesting optimization
    for two specified parameters against the optimization metric.

    Args:
        opt_result (typing.Any): The result object returned by Backtest.optimize().
                                 Must have `return_optimization=True`.
        all_param_names (list[str]): List of all parameter names used in the optimization
                                     (e.g., ['short_period', 'long_period', 'point_tp']).
        param1_name (str): The name of the first parameter for the heatmap (columns/x-axis).
        param2_name (str): The name of the second parameter for the heatmap (rows/y-axis).
        metric_name (str): The name of the metric being optimized (for the title).
                           Defaults to 'Objective Value'.
        agg_func (callable): Function to aggregate metric values if multiple optimization
                             runs share the same param1 and param2 values (e.g., when
                             other parameters were also varied). Defaults to np.max.
    """
    # Check if the necessary attributes exist.
    # Sambo results have 'space', 'xv', 'funv'. Older/other results might have '_vars'.
    has_sambo_attrs = hasattr(opt_result, 'space') and hasattr(opt_result, 'xv') and hasattr(opt_result, 'funv')
    has_legacy_attrs = hasattr(opt_result, '_vars') and hasattr(opt_result, 'xv') and hasattr(opt_result, 'funv')

    if not (has_sambo_attrs or has_legacy_attrs):
         print("Error: Invalid opt_result object. Missing expected attributes (e.g., 'space'/'_vars', 'xv', 'funv').")
         print("Did you run optimize with 'return_optimization=True'?")
         return

    try:
        # Validate input parameter names against the provided list
        if not all_param_names:
             print("Error: The provided list of all parameter names is empty.")
             return

        param_map = {name: name for name in all_param_names} # Use provided list for map

        if param1_name not in param_map or param2_name not in param_map:
            available_params = list(param_map.keys())
            raise ValueError(
                f"One or both parameters ('{param1_name}', '{param2_name}') not found "
                f"in optimization results. Available parameters: {available_params}"
            )

        # Create DataFrame from optimization results
        param_values = opt_result.xv # List of parameter combinations tried
        objective_values = opt_result.funv # Corresponding objective function values (often negative for maximization)

        # Assuming maximization, negate the objective values if needed
        if isinstance(objective_values, (list, np.ndarray)) and len(objective_values) > 0 and np.mean(objective_values) < 0:
             objective_values = [-v for v in objective_values]
             print("Note: Negating objective values, assuming maximization problem.")

        # Ensure all_param_names list (passed as argument) is not empty before creating DataFrame
        if not all_param_names: # Corrected variable name here
             print("Error: The provided list of all parameter names is empty.") # Adjusted error message
             return

        results_df = pd.DataFrame(param_values, columns=all_param_names) # Use provided all_param_names list
        results_df[metric_name] = objective_values

        # Filter out rows with NaN results if any
        results_df = results_df.dropna(subset=[metric_name])

        if results_df.empty:
            print("No valid optimization results found to plot.")
            return

        # Group by the two parameters of interest and aggregate the metric
        grouped = results_df.groupby([param1_name, param2_name])[metric_name].agg(agg_func).reset_index()

        # Pivot the table for the heatmap
        try:
            pivot_table = grouped.pivot(index=param2_name, columns=param1_name, values=metric_name)
        except Exception as e:
             print(f"Error creating pivot table: {e}")
             print("Maybe the combination of parameters is not unique enough for a heatmap?")
             print("Grouped data head:\n", grouped.head())
             return

        # Plot the heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_table, annot=True, fmt=".2f", cmap="viridis", linewidths=.5)
        plt.title(f'{metric_name} vs {param1_name} and {param2_name}')
        plt.xlabel(param1_name)
        plt.ylabel(param2_name)
        plt.tight_layout()
        plt.show()

    except AttributeError as e:
         # Catch potential issues if opt_result doesn't have expected attributes
         print(f"Error accessing attributes on opt_result: {e}")
         print("Did you run optimize with 'return_optimization=True'?")
    except Exception as e:
        print(f"An error occurred during heatmap generation: {e}")


# Example Usage (requires a dummy object similar to _OptimizeResult)
if __name__ == '__main__':
    # Create a dummy object for demonstration
    class DummyParam:
        def __init__(self, name):
            self.name = name

    class DummyOptimizeResult:
         def __init__(self, _vars, xv, funv):
              self._vars = _vars
              self.xv = xv
              self.funv = funv

    dummy_result = DummyOptimizeResult(
        _vars=[DummyParam('param_a'), DummyParam('param_b'), DummyParam('param_c')],
        xv=[ # Parameter combinations tried
            {'param_a': 10, 'param_b': 5, 'param_c': 100},
            {'param_a': 10, 'param_b': 10, 'param_c': 100},
            {'param_a': 20, 'param_b': 5, 'param_c': 100},
            {'param_a': 20, 'param_b': 10, 'param_c': 100},
            {'param_a': 10, 'param_b': 5, 'param_c': 200}, # Duplicate param_a/b
            {'param_a': 10, 'param_b': 10, 'param_c': 200},# Duplicate param_a/b
        ],
        funv=[ # Objective function values (negative for maximization)
            -1050, -1100, -1000, -1200, -1060, -1150
        ]
    )

    print("Generating example heatmap...")
    # Example requires providing the list of all parameter names used
    example_all_params = ['param_a', 'param_b', 'param_c']
    plot_optimization_heatmap(
        dummy_result,
        all_param_names=example_all_params,
        param1_name='param_a',
        param2_name='param_b',
        metric_name='Final Equity'
    )
    print("Example heatmap generation complete.")
