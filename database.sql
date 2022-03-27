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
	B_Age_Bucket VARCHAR,
	B_Height_Bucket VARCHAR,
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
	R_Name VARCHAR,
	R_Stance VARCHAR,
	R_Age_Bucket VARCHAR,
	R_Height_Bucket VARCHAR,
	R_Age INT,
	R_Height INT,
	R_Weight INT,
	R_Reach INT,
	R_Wins INT,
	R_Losses INT,
	R_Draws INT,
	R_No_Contest INT,
	R_Career_Significant_Strikes_Landed_PM INT,
	R_Career_Striking_Accuracy INT,
	R_Career_Significant_Strike_Defence INT,
	R_Career_Takedown_Average INT,
	R_Career_Takedown_Accuracy INT,
	R_Career_Takedown_Defence INT,
	R_Career_Submission_Average INT,
	R_Knockdowns INT,
	PRIMARY KEY (B_Name, R_Name)
);

-- Drop fighter_stats table
DROP TABLE fighter_stats;

-- Display fighter_stats table
SELECT * FROM fighter_stats;
