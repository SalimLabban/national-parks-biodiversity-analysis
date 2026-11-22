# national-parks-biodiversity-analysis
I analyzed species conservation records and wildlife observations across four national parks using Python, pandas, Matplotlib, Seaborn, and SciPy. The project includes eight charts, statistical comparisons of conservation status, and an analysis of weekly sheep observations.
Questions and findings
# Question	Finding
How are animal species distributed by conservation status?	86.47% had no listed status. Among recorded statuses, Species of Concern was the most common, with 103 animal species.
Which category had the highest percentage listed as endangered?	Mammals had the highest share at 3.41% (6 of 176), followed by fish at 2.40% (3 of 125).
Did the share with any listed conservation status differ across categories?	The pairwise chi-square tests found evidence of a difference between mammals and reptiles (p = 0.0384) and insufficient evidence for mammals and birds (p = 0.6876). The overall test had a small expected count, so its result warrants caution.
Which species had the most recorded observations in each park?	Columba livia in Bryce (339), Streptopelia decaocto in Great Smoky Mountains (256), Holcus lanatus in Yellowstone (805), and Hypochaeris radicata in Yosemite (505).


Sheep observations and sample planning
Yellowstone recorded 507 sheep observations in one week, compared with 250 in Bryce. If those weekly rates held, reaching a target of 870 observations per park would take 2 full weeks in Yellowstone and 4 in Bryce.
Comparing species across parks
The heatmap compares Yellowstone’s ten most recorded species across all four parks. The hexbin plot shows how species cluster by recorded counts in Yellowstone and Yosemite. The densest cluster is near 250 observations in Yellowstone and 150 in Yosemite. Darker hexagons contain more species with similar counts, and logarithmic shading makes smaller groups easier to see.
