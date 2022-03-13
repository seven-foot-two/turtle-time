# UFC Fight Analysis

## Project Overview
### Selected topic
The topic selected by the team was UFC Fight Analysis of all UFC fights from 2013.

### Reason for topic selection
The team selected to analyze UFC fights from 2013 because the team members had prior interest in UFC fighting, and were intrigued by the data contained in the dataset.

### Description of the source of data
The data on UFC fights from 2013 was obtained from [Kaggle](https://www.kaggle.com/calmdownkarm/ufcdataset?select=data.csv).

### Questions we hope to answer with the data
The questions we hope to answer with the data include:
- Can our machine learning model predict the `winner` (target) based on the features?
- Can our machine learning model predict the `winby` based on features?
- Is there a relationship between fighter `age` and `winner` outcome?
- Is there a relationship between fighter `height` and `winner` outcome?
- Is there a relationship between fighter `hometown` and `winner` outcome?
- Is there a relationship between fighter `weight` and `winner` outcome?

### Team Member Roles
For the First Segment of the project, each team member was assigned a specific role:
- **Square:** The team member in the square role will be responsible for the repository.
    - Tozer, Francesca, and Matin
- **Triangle:** The member in the triangle role will create a mockup of a machine learning model. This can even be a diagram that explains how it will work concurrently with the rest of the project steps.
    - Jack, Max, and Matin
- **Circle:** The member in the circle role will create a mockup of a database with a set of sample data, or even fabricated data. This will ensure the database will work seamlessly with the rest of the project.
    - Francesca and Tozer
- **X:** The member in the X role will decide which technologies will be used for each step of the project.
    - Jack and Max

### Communication Protocols
The team attends a standing meeting daily from 6-7pm EST on Discord to discuss progress made on the project, and other project-related matters. The team also maintains constant communication as-needed via Discord chat. 

## Machine Learning Model
The team determined that the best machine learning model to implement for the First Segment was a Logistic Regression model. The team chose Logistic Regression because the dataset has two possible outcomes (`blue` or `red` winner). This model is also widely used in machine learning, and the team was interested to see the accuracy of the model for this initial phase.

## Resources
- Source Code: [`UFC_Final_Project.ipynb`](UFC_Final_Project.ipynb)
- Data: [`data.csv`](Resources/data.csv)
    - Header Breakdown
        - `B` - Blue corner
        - `R` - Red corner
        - `B-Prev` - Previous wins of the fighter in the blue corner
        - `R-Prev` - Previous wins of the fighter in the red corner
        - `Last_round` - The round the fight ENDED
        - `Max_round` - Total rounds the fight was scheduled for
        - `Height` - Fighter height (cm)
        - `Weight` - Fighter weight (kg)
        - `winby`
            - `DEC` - Decision: Fight went all rounds and the judges decided the winner.
            - `KO/TKO`
                - Knockout (KO): Opponent was flatlined, out cold.
                - Technical Knockout (TKO): Opponent was not able to respond and the fight was stopped by the ref.
            - `SUB` - Submission: Opponent was submitted.
        - `winner`
            - `Red` - Fighter in the red corner won the fight.
            - `Blue` - Fighter in the blue corner won the fight.
            - `No contest` - No contest decisions in MMA are usually declared when an accidental illegal strike (the rules on which differ from each organization and state) causes the recipient of the blow to be unable to continue, that decision being made by the referee, doctor, the fighter or his corner.
- Libraries: [`Pandas`](https://pandas.pydata.org), [`Matplotlib`](https://matplotlib.org/), [`Scikit Learn`](https://scikit-learn.org/stable/index.html)
