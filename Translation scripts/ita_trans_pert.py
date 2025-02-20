import matplotlib.pyplot as plt
import pandas as pd

# Data for the metrics
data = {
    "Metric": [
        "Execution Accuracy", 
        "Executable Execution Accuracy", 
        "Easy Execution Accuracy", 
        "Medium Execution Accuracy", 
        "Hard Execution Accuracy", 
        "Extra Execution Accuracy"
    ],
    "English Baseline": [30.0, 48.39, 34.4, 16.67, 42.11, 15.38],
    "Italian Original": [14.0, 22.05, 18.4, 6.67, 5.26, 7.69],
    "Eng Schema Ita Data": [18.0, 28.35, 24.8, 6.67, 5.26, 7.69],
    "Italian New Prompt": [20.5, 30.37, 24.0, 10.0, 10.53, 23.08],
    "Italian Schema with English Data": [12.0, 22.64, 13.6, 6.67, 10.53, 11.54],
    "Italian Schema and Data": [16.0, 30.19, 18.4, 6.67, 21.05, 11.54]
}

# Creating the dataframe
df = pd.DataFrame(data)

# Plot Execution Accuracy and Executable Execution Accuracy
fig, ax = plt.subplots(figsize=(14, 8))

# Plotting the lines for each scenario
ax.plot(df['Metric'], df['English Baseline'], marker='o', label='English Baseline', color='blue')
ax.plot(df['Metric'], df['Italian Original'], marker='o', label='Italian Original', color='green')
ax.plot(df['Metric'], df['Eng Schema Ita Data'], marker='o', label='Eng Schema Ita Data', color='orange')
ax.plot(df['Metric'], df['Italian New Prompt'], marker='o', label='Italian New Prompt', color='red')
ax.plot(df['Metric'], df['Italian Schema with English Data'], marker='o', label='Italian Schema w/ English Data', color='purple')
ax.plot(df['Metric'], df['Italian Schema and Data'], marker='o', label='Italian Schema and Data', color='brown')

# Setting labels and title
ax.set_xlabel('Metric')
ax.set_ylabel('Accuracy (%)')
ax.set_title('Execution and Executable Execution Accuracy across Scenarios')
ax.legend()
ax.grid(True)

# Adjust the y-axis limits for more space
ax.set_ylim(0, 60)

# Define different offset ranges for each metric to minimize overlap
offsets_dict = {
    "Execution Accuracy": [5, 10, -10, 15, -15, 20],
    "Executable Execution Accuracy": [10, -15, 15, -10, 10, -20],
    "Easy Execution Accuracy": [5, -5, 5, -5, 5, -5],
    "Medium Execution Accuracy": [5, 5, -5, -5, 5, 5],
    "Hard Execution Accuracy": [-5, 5, -5, 5, -5, 5],
    "Extra Execution Accuracy": [5, -5, 5, -5, 5, -5]
}

# Adding percentages on the graph with different offsets to avoid overlap
colors = ['blue', 'green', 'orange', 'red', 'purple', 'brown']
for idx, col in enumerate(df.columns[1:]):
    for i, val in enumerate(df[col]):
        metric = df['Metric'][i]
        offset = offsets_dict[metric][idx % len(offsets_dict[metric])]
        ax.annotate(f"{val:.2f}%", (df['Metric'][i], val), 
                    color=colors[idx], 
                    xytext=(0, offset), 
                    textcoords='offset points',
                    ha='center')

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
