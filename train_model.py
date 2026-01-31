#!/usr/bin/env python3
"""
Simple script to train a sentiment analysis model
This creates a basic model for demonstration purposes
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

# Sample training data
train_texts = [
    # Positive examples
    "I love this product",
    "This is amazing",
    "Great quality",
    "Excellent service",
    "Best purchase ever",
    "Highly recommend",
    "Fantastic experience",
    "Love it so much",
    "Perfect product",
    "Outstanding quality",
    # Negative examples
    "I hate this",
    "Terrible product",
    "Waste of money",
    "Very disappointed",
    "Poor quality",
    "Awful experience",
    "Not recommended",
    "Horrible service",
    "Complete disaster",
    "Worst purchase",
    # Neutral examples
    "It's okay",
    "Average product",
    "Nothing special",
    "It works",
    "Decent quality",
    "Fair price",
    "Acceptable",
    "Normal product",
    "Standard quality",
    "Regular service"
]

train_labels = [
    "positive", "positive", "positive", "positive", "positive",
    "positive", "positive", "positive", "positive", "positive",
    "negative", "negative", "negative", "negative", "negative",
    "negative", "negative", "negative", "negative", "negative",
    "neutral", "neutral", "neutral", "neutral", "neutral",
    "neutral", "neutral", "neutral", "neutral", "neutral"
]

print("Training sentiment analysis model...")

# Create pipeline
model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=1000)),
    ('clf', MultinomialNB())
])

# Train model
model.fit(train_texts, train_labels)

print("Model trained successfully!")

# Test predictions
test_texts = [
    "This is great!",
    "This is terrible",
    "It's okay I guess"
]

print("\nTest predictions:")
for text in test_texts:
    prediction = model.predict([text])[0]
    probabilities = model.predict_proba([text])[0]
    confidence = max(probabilities)
    print(f"  '{text}' -> {prediction} (confidence: {confidence:.2f})")

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

# Save model
model_path = 'models/sentiment_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print(f"\nModel saved to: {model_path}")
print("You can now use this model with the FastAPI application!")