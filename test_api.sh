#!/bin/bash

# API Testing Script - Sentiment Analysis API
BASE_URL="http://localhost"
API_BASE="${BASE_URL}/api"

echo "Sentiment Analysis API - Test Script"

# Test 1: Health Check
echo "Test 1: Health Check"
curl -s "${BASE_URL}/health" | jq
echo ""

# Test 2: Root Endpoint
echo "Test 2: Root Endpoint (Check Model Status)"
curl -s "${BASE_URL}/" | jq
echo ""

# Test 3: Register New User
echo "Test 3: Register New User"
curl -s -X POST "${API_BASE}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "username": "demo_user",
    "password": "demo123",
    "full_name": "Demo User"
  }' | jq
echo ""

# Test 4: Login and Get Token
echo "Test 4: Login (Get JWT Token)"
TOKEN_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }')

TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')
echo $TOKEN_RESPONSE | jq

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "Failed to get token. Please ensure the database is initialized."
  exit 1
fi
echo ""

# Test 5: Get Current User Profile
echo "Test 5: Get Current User Profile"
curl -s "${API_BASE}/users/me" -H "Authorization: Bearer $TOKEN" | jq
echo ""

# Test 6: Get Model Info
echo "Test 6: Get Model Information"
curl -s "${API_BASE}/model/info" -H "Authorization: Bearer $TOKEN" | jq
echo ""

# Test 7: Predict Sentiment - Positive
echo "Test 7: Predict Sentiment - Positive Text"
curl -s -X POST "${API_BASE}/predict" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}' | jq
echo ""

# Test 8: Predict Sentiment - Negative
echo "Test 8: Predict Sentiment - Negative Text"
curl -s -X POST "${API_BASE}/predict" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is terrible."}' | jq
echo ""

# Test 9: Predict Sentiment - Neutral
echo "Test 9: Predict Sentiment - Neutral Text"
curl -s -X POST "${API_BASE}/predict" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "It is okay."}' | jq
echo ""

# Test 10: Batch Prediction
echo "Test 10: Batch Sentiment Prediction"
curl -s -X POST "${API_BASE}/predict/batch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["I love this!", "This is terrible"]}' | jq
echo ""

# Test 11: Load Balancing Test
echo "Test 11: Load Balancing Test"
for i in {1..5}; do
  RESPONSE=$(curl -s -X POST "${API_BASE}/predict" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"Test message $i\"}")
  INSTANCE=$(echo $RESPONSE | jq -r '.predicted_by')
  echo "Request $i: Instance: $INSTANCE"
done
echo ""

# Test 12: Unauthorized Access (No Token)
echo "Test 12: Unauthorized Access (No Token)"
curl -s -X POST "${API_BASE}/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "No token"}' | jq
echo ""

# Test 13: Invalid Token (Deliberate Failure)
echo "Test 13: Invalid Token"
curl -s -X POST "${API_BASE}/predict" \
  -H "Authorization: Bearer invalid_token_here" \
  -H "Content-Type: application/json" \
  -d '{"text": "Bad token"}' | jq
echo ""

# Test 14: Final Validation with Original Valid Token
echo "Test 14: Final Validation with Valid Token"
curl -s -X POST "${API_BASE}/predict" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Final verification check"}' | jq
echo ""

echo "All tests completed!"