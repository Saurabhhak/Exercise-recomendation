from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load your dataset
df = pd.read_csv('ExerciseDataset.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    # Get form data from the request
    exercise_type = request.form.get('exercise_type')
    body_part = request.form.get('body_part')
    equipment = request.form.get('equipment')
    level = request.form.get('level')
    
    # Filter dataset based on user input
    filtered_df = df.loc[
        (df['Type'] == exercise_type) & 
        (df['BodyPart'] == body_part) & 
        (df['Equipment'] == equipment) & 
        (df['Level'] == level)
    ]
    if not filtered_df.empty:
        # Convert filtered data to HTML for display
        recommendations = filtered_df.to_html(index=False)
    else:
        # Display a message if no results are found
        recommendations = "No matching exercises found. Please adjust your filters and try again."
    return render_template('index.html', recommendations=recommendations)
@app.route('/sign')
def sign():
    return render_template('sign.html')
if __name__ == '__main__':
    app.run(debug=True)
