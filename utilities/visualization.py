"""Module to visualize cached search results using pandas and matplotlib
"""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
from utilities import dbhandler

def visualize():
    """Creates a pyplot for search queries visualization
    """
    search_data = dbhandler.fetch_searches()
    if len(search_data) == 0:
        print("Nothing to visualize yet")
        return
    df = pd.DataFrame(search_data)
    df.columns = ['time','personid','query','has_world']
    colors = {'True':'red', 'False':'blue'}
    annotations = {}
    size = []
    for _,row in df.iterrows():
        size.append(len(df[(df['query'] == row['query']) & (
            df['has_world'] == row['has_world'])]['query']))
        if not row['time'] in annotations.keys():
            annotations_list = df[(df['query'] == row['query']) & (
                df['has_world'] == row['has_world'])]['personid'].to_list()
            annotation = "\n".join(
                list(map(dbhandler.name_from_id, annotations_list)))
            annotations[row['time']] = {"label": annotation, "x" : row["time"] , "y" : row["query"]}
    df['size'] = size
    _, ax = plt.subplots()
    ax.scatter(x=df['time'],y=df['query'], c=df['has_world'].map(colors), s=df['size']*30)
    for key in annotations:
        ax.annotate(annotations[key]["label"], (annotations[key]["x"],annotations[key]["y"]))
    legend_elements = [Line2D([0],
                            [0],
                            marker='o',
                            color='w',
                            label='Homeworld cached',
                            markerfacecolor='red',
                            markersize=15),
                        Line2D([0],
                                [0],
                                marker='o',
                                color='w',
                                label='Homeworld NOT cached',
                                markerfacecolor='blue',
                                markersize=15)]
    plt.legend(handles=legend_elements)
    plt.title("Search Queries Visualization")
    plt.show()
