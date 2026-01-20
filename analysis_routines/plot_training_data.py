import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("R:/cla_psyc_grissom_labshare/Projects/Anika/Data/extincts/training_data.csv")
print(df.head())

mask = df['schedule'].isin(['Day0'])
df_training = df[~mask]

sns.lineplot(data=df_training, x="date", y="achieved", hue="mouseID", style="schedule")
plt.xticks(rotation=90)
plt.show()