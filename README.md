# table-tennis-analytics

**TT-analytics** proposes new metrics to further analyze **table tennis matches**.  Our approach involves adapting existing metrics by incorporating additional attributes provided by the **detailed data**, such as player zones and shot angles. Furthermore, we present a methodology for **visualizing all metrics simultaneously** during a single set, enabling a comprehensive assessment of their significance.

This repository is linked to a publication presented at the **MLSA 2023**.
You can reproduce the figures of the publication by executing :
```bash
# Clone the repository
$ git clone https://github.com/centralelyon/table-tennis-analytics.git
$ cd Metrics/Lebrun_Zhendong/
# Run the file MatchAnalysis.py
$ python3 MatchAnalysis.py
```
## Domination

We defined the **domination** as a situation in which a player (or a team) consistently outperforms their opponents and maintains a significant advantage. This function is close to 1 when the first player (or team) dominates, and it is close to -1 if it is the second.

> **Note :** we computed the domination as a function of three parameters : the **score** advantage, the **physical** domination and the **mental** domination.


## Expected Score

The **expected score** is a statistical metric to estimate the probability of winning a point based on various factors such as player skill, shot quality, and opponent performance.

> **Note :** To compute this metric, we used a **Playing Pattern Tree** in order to explore all the possible patterns of a point. We used **Simulated Data** to extend the database and to increase the precision.

## Creativity (or Shots Diversity)

The **creativity** is defined as the variety of shots and techniques employed by a player during a match, including variations in racket side, placement, and shot selection.
> **Note :** To compute the distance between two openings, we look at the depth of their common ancestor in the **Playing Pattern Tree**. 
