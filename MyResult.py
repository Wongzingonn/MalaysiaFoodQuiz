import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Define text files path
base_path = os.path.dirname(__file__)
questions_path = os.path.join(base_path, "Questions.txt")
answers_path = os.path.join(base_path, "Answers.txt")

def load_data():
    # Load correct answers
    correct_answers = {}
    if os.path.exists(questions_path):
        with open(questions_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        correct_answers[parts[0]] = parts[1]
    
    # Load participant answers
    results_data = []
    if os.path.exists(answers_path):
        with open(answers_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    if len(parts) == 3:
                        name, qid, answer = parts
                        
                        # Determine if correct
                        is_correct = 0
                        if qid in correct_answers and correct_answers[qid] == answer:
                            is_correct = 1
                            
                        results_data.append({
                            "Name": name,
                            "Question_ID": qid,
                            "Correct": is_correct
                        })
                        
    return pd.DataFrame(results_data), len(correct_answers)

def main():
    print("--- Quiz Results Statistical Analysis ---\n")
    
    df, total_possible_score = load_data()
    
    if df.empty:
        print("No answers have been recorded yet. Please take the quiz first!")
        return

    # Group by 'Name' to calculate total score for each participant
    participant_scores = df.groupby('Name')['Correct'].sum().reset_index()
    participant_scores.columns = ['Participant', 'Total Marks']

    print("📋 Participant Scores:")
    print(participant_scores.to_string(index=False))
    print("\n" + "="*40 + "\n")

    print("📈 Statistical Analysis Overview:")
    
    # Calculate statistics using numpy and pandas
    scores_array = participant_scores['Total Marks'].to_numpy()

    if len(scores_array) > 0:
        highest_mark = np.max(scores_array)
        lowest_mark = np.min(scores_array)
        mean_mark = np.mean(scores_array)
        median_mark = np.median(scores_array)
        
        print(f"Total Participants: {len(participant_scores)}")
        print(f"Highest Mark:       {int(highest_mark)}")
        print(f"Lowest Mark:        {int(lowest_mark)}")
        print(f"Average / Mean:     {mean_mark:.2f}")
        print(f"Median:             {median_mark:.2f}")
        print("\n" + "="*40 + "\n")

        print("📊 Generating Visualizations... Close the plot windows to finish.")
        
        # Create a figure with a 2x2 grid for 4 separate graphs
        fig, axs = plt.subplots(2, 2, figsize=(14, 10))
        
        # Total Marks by Participant (Bar Chart)
        bars = axs[0, 0].bar(
            participant_scores['Participant'], 
            participant_scores['Total Marks'], 
            color='skyblue', 
            edgecolor='black'
        )
        
        axs[0, 0].bar_label(bars, fmt='%d', padding=3)
        axs[0, 0].set_ylabel('Total Marks')
        axs[0, 0].set_xlabel('Participant Name')
        axs[0, 0].set_title('Total Marks by Participant')
        axs[0, 0].set_ylim(0, total_possible_score + 1)
        axs[0, 0].tick_params(axis='x', labelrotation=45)
        
        # Use discrete bins for integer scores for the histograms
        bins = np.arange(0, total_possible_score + 2) - 0.5

        # Average Histogram
        axs[0, 1].hist(scores_array, bins=bins, color='lightgreen', edgecolor='black', rwidth=0.8)
        axs[0, 1].axvline(x=mean_mark, color='darkgreen', linestyle='dashed', linewidth=2, label=f'Average: {mean_mark:.2f}')
        axs[0, 1].set_ylabel('Number of Participants')
        axs[0, 1].set_xlabel('Marks Obtained')
        axs[0, 1].set_title('Average Mark Distribution')
        axs[0, 1].set_xticks(range(total_possible_score + 1))
        axs[0, 1].yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        axs[0, 1].legend()
        
        # Median Histogram
        axs[1, 0].hist(scores_array, bins=bins, color='plum', edgecolor='black', rwidth=0.8)
        axs[1, 0].axvline(x=median_mark, color='purple', linestyle='dashed', linewidth=2, label=f'Median: {median_mark:.2f}')
        axs[1, 0].set_ylabel('Number of Participants')
        axs[1, 0].set_xlabel('Marks Obtained')
        axs[1, 0].set_title('Median Mark Distribution')
        axs[1, 0].set_xticks(range(total_possible_score + 1))
        axs[1, 0].yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        axs[1, 0].legend()
        
        # Mean Histogram
        axs[1, 1].hist(scores_array, bins=bins, color='lightcoral', edgecolor='black', rwidth=0.8)
        axs[1, 1].axvline(x=mean_mark, color='darkred', linestyle='dashed', linewidth=2, label=f'Mean: {mean_mark:.2f}')
        axs[1, 1].set_ylabel('Number of Participants')
        axs[1, 1].set_xlabel('Marks Obtained')
        axs[1, 1].set_title('Mean Mark Distribution')
        axs[1, 1].set_xticks(range(total_possible_score + 1))
        axs[1, 1].yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        axs[1, 1].legend()
        
        plt.tight_layout()
        plt.show()

    else:
        print("Not enough data to compute statistics.")

if __name__ == "__main__":
    main()