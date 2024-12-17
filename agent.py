# Import necessary libraries
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Simulated data for the AI Agent
print("Step 1: Generating data for the AI agent...")
data_size = 100
np.random.seed(42)  # For reproducibility
X = np.random.rand(data_size, 1) * 10  # Random input values (feature)
y = 2 * X.squeeze() + np.random.randn(data_size) * 2  # Target = 2*X + noise

# Convert to DataFrame
data = pd.DataFrame({'Feature': X.squeeze(), 'Target': y})
print("Sample Data:")
print(data.head())

# Split data into training and testing sets
print("\nStep 2: Splitting the data into train and test sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the AI agent (Linear Regression Model)
print("\nStep 3: Training the Linear Regression model...")
model = LinearRegression()
model.fit(X_train, y_train)

# Test the AI agent
print("\nStep 4: Testing the AI agent...")
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)

# Display results
print(f"Mean Squared Error on Test Data: {mse:.2f}")
print("\nPredictions vs Actual Values:")
for i in range(5):  # Show first 5 predictions
    print(f"Input: {X_test[i][0]:.2f} | Prediction: {y_pred[i]:.2f} | Actual: {y_test[i]:.2f}")

# Simple decision-making function for the AI agent
def ai_decision(input_value):
    """AI Agent makes a simple decision based on the model's prediction."""
    prediction = model.predict(np.array([[input_value]]))
    if prediction > 10:
        return f"Prediction: {prediction[0]:.2f} -> Decision: HIGH VALUE"
    else:
        return f"Prediction: {prediction[0]:.2f} -> Decision: LOW VALUE"

# Let the AI agent make a decision
print("\nStep 5: Let the AI agent make a decision...")
test_input = float(input("Enter a value for the agent to evaluate: "))
result = ai_decision(test_input)
print(result)

