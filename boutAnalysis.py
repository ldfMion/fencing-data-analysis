import matplotlib.pyplot as plt
import pandas as pd

from typing import Literal

ActionClassification = Literal["OFFENSIVE", "DEFENSIVE"]


def get_score(df, perspective):
    return len(df[(df["Perspective"] == perspective) & (df["Outcome"] == "Hit")])



def plot_pie_chart(ax: plt.Axes, y_vals, labels, title: str, text_color: str, total_count: float):
    ax.pie(y_vals, labels=labels, autopct=lambda x: '{:.0f}'.format(x*total_count/100), textprops={"color": text_color})
    ax.set_title(title, color=text_color)
    return

def plot_pie_chart_from_column(ax: plt.Axes, filtered_df_column: pd.Series, title: str, text_color: str):
    counts = filtered_df_column.value_counts()
    plot_pie_chart(ax, counts, counts.index, title, text_color, counts.sum())
    return

def plot_pie_chart_from_dict(ax: plt.Axes, counts: dict, title: str, text_color: str):
    plot_pie_chart(ax, counts.values(), counts.keys(), title, text_color, sum(counts.values()))
    return


def to_percentage_str(number):
    return '{:.2f}%'.format(number * 100)

def classify_action(action_name: str) -> ActionClassification:
    OFFENSIVE_ACTIONS = ["Attack", "Remise", "Counter-time"]
    DEFENSIVE_ACTIONS = [
        "Parry",
        "Counter-attack",
        "Riposte",
        "Attack on prep",
        "Avoid with distance",
        "Counter-riposte",
    ]
    if action_name in OFFENSIVE_ACTIONS:
        return "OFFENSIVE"
    if action_name in DEFENSIVE_ACTIONS:
        return "DEFENSIVE"
    else:
        raise Exception(f"{action_name} not classfiable")

def get_classification_outcomes(actions: pd.DataFrame,
    perspective: str, classification: ActionClassification
) -> dict:
    
    outcome_counts =dict(
        actions.query(
            "`Action classification` == @classification and Perspective == @perspective"
        )["Outcome"].value_counts()
    )

    num_failed = len(actions.query(
        "Perspective != @perspective and `Counter action classification` == @classification and Outcome == 'Hit'"
    ))
    if(num_failed > 0):
        outcome_counts["Failed"] = num_failed

    return outcome_counts

def get_num_failed(outcome_counts: dict) -> int:
    return outcome_counts.get("Off-target", 0) + (outcome_counts.get("No hit", 0)) + outcome_counts.get("Failed", 0)

def get_num_hits(outcome_counts: dict) -> int:
    return outcome_counts.get("Hit", 0)

def calc_effectiveness(outcome_counts: dict) -> float:
    num_failed = get_num_failed(outcome_counts)
    num_hits = get_num_hits(outcome_counts)
    total = num_hits + num_failed
    if(total == 0):
        return 0
    return num_hits / (total)

def get_effectiveness_info_str(outcome_counts: dict) -> str:
    total = get_num_hits(outcome_counts) + get_num_failed(outcome_counts)
    return f'{get_num_hits(outcome_counts)}/{total} ({to_percentage_str(calc_effectiveness(outcome_counts))})'


def get_action_outcomes(actions: pd.DataFrame, perspective: str, action: str) -> dict:
    outcome_counts =dict(
        actions.query(
            "Action == @action and Perspective == @perspective"
        )["Outcome"].value_counts()
    )

    num_failed = len(actions.query(
        "Perspective != @perspective and `Counter action` == @action and Outcome == 'Hit'"
    ))
    if(num_failed > 0):
        outcome_counts["Failed"] = num_failed

    return outcome_counts


def get_unique_column_names(df: pd.DataFrame, column: str, filter_column: str = None, filter_values: list = None) -> set:
    if filter_column == None and filter_values == None:
        names =  set(df[column])
    else:
        names =  set(df[df[filter_column].isin(filter_values)][column])
    names = [name for name in names if str(name) != "nan"]
    return names