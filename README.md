# UFC Fight Analysis

## Project Overview

### Selected topic

The topic selected by the team was UFC Fight Analysis of all UFC fights from 2013.

### Reason topic was selected

The team selected to analyze UFC fights from 2013 because the team members had prior interest in UFC fighting, and were intrigued by the data contained in the dataset.

### Description of the source of data

The data on UFC fights from 2013 was obtained from [Kaggle](https://www.kaggle.com/calmdownkarm/ufcdataset?select=data.csv).

### Questions the team hopes to answer with the data

The questions we hope to answer with the data include:

-   Can our machine learning model predict the `winner` (target) based on the features?
-   Can our machine learning model predict the `winby` based on features?
-   Is there a relationship between fighter `age` and `winner` outcome?
-   Is there a relationship between fighter `height` and `winner` outcome?
-   Is there a relationship between fighter `hometown` and `winner` outcome?
-   Is there a relationship between fighter `weight` and `winner` outcome?

### Team Member Roles

For the First Segment of the project, each team member was assigned a specific role:

-   **Square:** The team member in the square role will be responsible for the repository.
    -   Tozer, Francesca, and Matin
-   **Triangle:** The member in the triangle role will create a mockup of a machine learning model. This can even be a diagram that explains how it will work concurrently with the rest of the project steps.
    -   Jack, Max, and Matin
-   **Circle:** The member in the circle role will create a mockup of a database with a set of sample data, or even fabricated data. This will ensure the database will work seamlessly with the rest of the project.
    -   Francesca and Tozer
-   **X:** The member in the X role will decide which technologies will be used for each step of the project.
    -   Jack and Max

### Communication Protocols

The team attends a standing meeting daily from 6-7pm EST on Discord to discuss progress made on the project, and other project-related matters. The team also maintains constant communication as-needed via Discord chat. The team maintains meeting notes, scheduling, and organization in [Notion](https://fobordo.notion.site/Module-20-Final-Project-d827016db1854b4f860cc8e221d9ccd7).

## Data Exploration

[Description of the data exploration (cleaning) phase of the project]

During the data exploration (cleaning) phase of the project, the team performed the following actions to clean and transform the data as a preprocessing step for the machine learning model.

### Converted data types

Using methods such as `convert_dtypes` and `astype`, the team converted the data types of various columns as necessary for the analysis

### Dropped non-beneficial columns

Using methods such as `drop` and `loc`, along with conditional operators, the team dropped all columns that were non-beneficial to the analysis, or columns that might create unnecessary "noise" for the machine learning model

### Created charts

-   [Red vs. Blue Win Rate]

### Created buckets

-   [Age]
-   [Weight]
-   [Height]

## Database Integration

[Description of the database integration?]

## Machine Learning Model

The team determined that the machine learning model for implementation was the Logistic Regression model. Logistic Regression was chosen because the dataset has been processed to have two possible outcomes (`blue` or `red` winner). In addition, Logistic Regression is widely used in machine learning due to its simplicity and speed. We are interested in evaluating the model's accuracy using Logistic Regression as a baseline to compare against other classifiers.

### Preliminary Data Preprocessing

1.  Import Data into Pandas DataFrame
2.  Convert columns to best inferred possible dtypes using dtypes supporting `pd.NA`
3.  Convert `winby` column into categorical type
4.  Drop the non-beneficial columns
5.  Keep only wins and losses (i.e., Red & Blue) in the `winner` column


### Feature Engineering

#### Weight Classes

The UFC have different weight classes for each fight and was used to introduce new categorical features to our dataset.

|    Weight Class   | Minimum Weight | Maximum Weight |
| :---------------: | :------------: | :------------: |
|    Heavyweight    |       93       |       120      |
| Light Heavyweight |      83.9      |       93       |
|    Middleweight   |      77.1      |      83.9      |
|    Welterweight   |      70.3      |      77.1      |
|    Lightweight    |      65.8      |      70.3      |
|   Featherweight   |      61.2      |      65.8      |
|    Bantamweight   |      56.7      |      61.2      |
|     Flyweight     |      52.2      |      56.7      |
|   Strawweight\*   |        0       |      52.2      |


#### Numerical & Categorical Transformations

![Pipeline](Resources/Images/pipeline.png)

##### Numerical value(s) transformation:

1.  Replace missing values using the null values along each column, and adding a indicator for replacement of null Values
  -   `SimpleImputer(strategy="constant", add_indicator=True)`
2.  Standardize features by removing the mean and scaling to unit variance
  -   `StandardScaler()`

##### Categorical value(s) transformation:

1.  Encode categorical features as a one-hot numeric array
  -   `OneHotEncoder(handle_unknown="ignore")`

### Feature Selection

#### Numerical

-   Last_round
-   Max_round
-   B_Age
-   R_Age
-   B_Height
-   R_Height

#### Categorical

-   winby
-   B_Weight_Class
-   R_Weight_Class

### Training and Testing Sets

Multiple arrays are created from splitting the train and test subsets randomly. The training dataset contains 80% of the data, whereas the testing dataset contains 20%. Additionally, `X` represents the features and `Y` as the target variable.

### Machine Learning Model Selection

[Explanation of model choice, including limitations and benefits]
<!-- TODO: Do we need this? This is a rehash of the Machine Learning Model paragraph. -->

## Analysis

### Results of the ML Model
|                | **precision** | **recall** | **f1-score** | **support** |
|---------------:|--------------:|-----------:|-------------:|------------:|
| **blue**       | 0.59          | 0.30       | 0.40         | 195         |
| **red**        | 0.62          | 0.85       | 0.71         | 261         |
|                |               |            |              |             |
| **accuracy**   |               |            | 0.61         | 456         |
| **macro avg**  | 0.60          | 0.57       | 0.55         | 456         |
| **weight avg** | 0.61          | 0.61       | 0.58         | 456         |

### Visualizations/Charts
![Pipeline](Resources/Images/confusion_matrix.png)

## Resources

-   Source Code: [`UFC_Final_Project.ipynb`](UFC_Final_Project.ipynb)
-   Data: [`data.csv`](Resources/data.csv)
    -   Header Breakdown
        -   `B` - Blue corner
        -   `R` - Red corner
        -   `B-Prev` - Previous wins of the fighter in the blue corner
        -   `R-Prev` - Previous wins of the fighter in the red corner
        -   `Last_round` - The round the fight ENDED
        -   `Max_round` - Total rounds the fight was scheduled for
        -   `Height` - Fighter height (cm)
        -   `Weight` - Fighter weight (kg)
        -   `winby`
            -   `DEC` - Decision: Fight went all rounds and the judges decided the winner.
            -   `KO/TKO`
                -   Knockout (KO): Opponent was flatlined, out cold.
                -   Technical Knockout (TKO): Opponent was not able to respond and the fight was stopped by the ref.
            -   `SUB` - Submission: Opponent was submitted.
        -   `winner`
            -   `Red` - Fighter in the red corner won the fight.
            -   `Blue` - Fighter in the blue corner won the fight.
            -   `No contest` - No contest decisions in MMA are usually declared when an accidental illegal strike (the rules on which differ from each organization and state) causes the recipient of the blow to be unable to continue, that decision being made by the referee, doctor, the fighter or his corner.
-   Libraries: [`Pandas`](https://pandas.pydata.org), [`Matplotlib`](https://matplotlib.org/), [`Scikit Learn`](https://scikit-learn.org/stable/index.html)
