-- Create ufc_table

-- Display ufc_table
SELECT * FROM ufc_table
ORDER BY field1 ASC;

-- Create fighter_stats table
CREATE TABLE fighter_stats (
	weight_class VARCHAR,
	Gender VARCHAR,
	B_Name VARCHAR,
	B_Stance VARCHAR,
	B_Age_Bucket,
	B_Height_Bucket,
	B_Age INT,
	B_Height INT,
	B_Weight INT,
	B_Reach VARCHAR,
	B_Wins INT,
	B_Losses INT,
	B_Draws INT,
	B_No_Contest INT,
	B_Career_Significant_Strikes_Landed_PM INT,
	B_Career_Striking_Accuracy INT,
	B_Career_Significant_Strike_Defence INT,
	B_Career_Takedown_Average INT,
	B_Career_Takedown_Accuracy INT,
	B_Career_Takedown_Defence INT,
	B_Career_Submission_Average INT,
	B_Knockdowns INT,
	R_Name,
	R_Stance,
	R_Age_Bucket,
	R_Height_Bucket,
	R_Age,
	R_Height,
	R_Weight,
	R_Reach,
	R_Wins,
	R_Losses,
	R_Draws,
	R_No_Contest,
	R_Career_Significant_Strikes_Landed_PM,
	R_Career_Striking_Accuracy,
	R_Career_Significant_Strike_Defence,
	R_Career_Takedown_Average,
	R_Career_Takedown_Accuracy,
	R_Career_Takedown_Defence,
	R_Career_Submission_Average,
	R_Knockdowns
	PRIMARY KEY B_Name, R_Name
);

-- Drop fighter_stats table
DROP TABLE fighter_stats;

-- Display fighter_stats table
SELECT * FROM fighter_stats;
