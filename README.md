# 🎯 Sentiment Analysis API with Load Balancing & JWT Authentication

A production-ready sentiment analysis API built with FastAPI, Nginx load balancing, JWT authentication, and PostgreSQL.

## 📋 Project Overview

This project demonstrates how to build a scalable sentiment analysis API that can handle hundreds of concurrent users by distributing traffic across multiple FastAPI instances using Nginx as a load balancer.

### **Key Features**

✅ **Sentiment Analysis** - Predict sentiment (positive/negative/neutral) from text  
✅ **JWT Authentication** - Secure API access with token-based auth  
✅ **Load Balancing** - Nginx distributes traffic across 2 FastAPI instances  
✅ **Auto Failover** - If one instance fails, traffic routes to healthy instances  
✅ **PostgreSQL Database** - Store authorized users  
✅ **Batch Predictions** - Analyze multiple texts in one request  
✅ **Instance Tracking** - See which server handled your request  

---

## 🏗️ Architecture

```
Client Request (with JWT Token)
         ↓
    Nginx Load Balancer
    (Round-robin distribution)
         ↓
   ┌─────────┴─────────┐
   ↓                   ↓
FastAPI-1          FastAPI-2
(Sentiment Model)  (Sentiment Model)
   ↓                   ↓
   └─────────┬─────────┘
         ↓
   PostgreSQL Database
   (User Authentication)
```

---

## 🚀 Quick Start

### **Prerequisites**

- Docker & Docker Compose
- Python 3.11+ (for training model)
- curl & jq (for testing)

### **Setup (5 steps)**

**1. Train the sentiment model**
```bash
python3 train_model.py
```
This creates `models/sentiment_model.pkl`

**2. Build and start services**
```bash
docker compose -f updated_docker-compose.yml up --build -d
```

**3. Wait for PostgreSQL**
```bash
sleep 10
```

**4. Initialize database with sample users**
```bash
docker exec sentiment_fastapi1 python init_db.py
```

**5. Test the API**
```bash
chmod +x updated_test_api.sh
./updated_test_api.sh
```

---

## 📡 API Endpoints

### **Public Endpoints (No Auth Required)**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |

### **Protected Endpoints (Requires JWT Token)**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict` | Predict sentiment (single) |
| POST | `/api/predict/batch` | Predict sentiment (batch) |
| GET | `/api/model/info` | Get model information |
| GET | `/api/users/me` | Get current user profile |

---

## 🔐 Authentication Flow

### **1. Login**
```bash
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### **2. Use Token for Predictions**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost/api/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I love this product!"
  }'
```

**Response:**
```json
{
  "text": "I love this product!",
  "sentiment": "positive",
  "confidence": 0.95,
  "predicted_by": "FastAPI-1",
  "user": "admin"
}
```

---

## 🎯 Usage Examples

### **Single Prediction**
```bash
curl -X POST http://localhost/api/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is amazing!"}'
```

### **Batch Prediction**
```bash
curl -X POST http://localhost/api/predict/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "I love this!",
      "This is terrible",
      "Not sure about this"
    ]
  }'
```

**Response:**
```json
{
  "predictions": [
    {"text": "I love this!", "sentiment": "positive", "confidence": 0.95},
    {"text": "This is terrible", "sentiment": "negative", "confidence": 0.89},
    {"text": "Not sure about this", "sentiment": "neutral", "confidence": 0.67}
  ],
  "predicted_by": "FastAPI-2",
  "user": "admin",
  "total_count": 3
}
```

---

## ⚖️ Load Balancing Demo

### **Test Round-Robin Distribution**
```bash
for i in {1..10}; do
  curl -s -X POST http://localhost/api/predict \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"Test $i\"}" | jq -r '.predicted_by'
done
```

**Expected Output:**
```
FastAPI-1
FastAPI-2
FastAPI-1
FastAPI-2
...
```

### **Test Failover**
```bash
# Stop instance 1
docker stop sentiment_fastapi1

# All requests now go to instance 2
for i in {1..5}; do
  curl -s http://localhost/api/predict \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"text": "Test"}' | jq -r '.predicted_by'
done

# Restart instance 1
docker start sentiment_fastapi1
```

---

## 👥 Default Users

After running `init_db.py`:

| Username | Password | Role | Use Case |
|----------|----------|------|----------|
| admin | admin123 | Superuser | Testing & admin tasks |
| testuser | test123 | Regular | Normal API usage |

---

## 📂 Project Structure

```
sentiment-api/
├── docker-compose.yml       # Services orchestration
├── Dockerfile              # FastAPI container
├── requirements.txt        # Python dependencies
├── train_model.py         # Train sentiment model
├── test_api.sh            # API testing script
├── init_db.py             # Database initialization
│
├── models/
│   └── sentiment_model.pkl  # Trained model
│
├── nginx/
│   └── nginx.conf          # Load balancer config
│
└── backend/
    └── app/
        ├── main.py                  # FastAPI app
        ├── core/
        │   ├── config.py           # Settings
        │   ├── security.py         # JWT functions
        │   └── logging.py          # Logging setup
        ├── db/
        │   ├── models.py           # User model
        │   └── session.py          # Database session
        ├── routers/
        │   ├── auth.py             # Login/register
        │   ├── sentiment.py        # Predictions ⭐
        │   ├── users.py            # User management
        │   └── health.py           # Health checks
        ├── services/
        │   └── auth_service.py     # Auth logic
        └── dependencies/
            └── auth_dependencies.py # JWT validation
```

---

## 🛠️ Commands

### **Start Services**
```bash
docker compose -f updated_docker-compose.yml up -d
```

### **View Logs**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f sentiment_fastapi1
docker compose logs -f sentiment_nginx
```

### **Stop Services**
```bash
docker compose down
```

### **Clean Everything**
```bash
docker compose down -v  # Removes volumes too
```

### **Rebuild After Code Changes**
```bash
docker compose up --build -d
```

---

## 🔍 Monitoring

### **Check Service Status**
```bash
docker compose ps
```

### **Health Check**
```bash
curl http://localhost/health
```

### **Nginx Status**
```bash
curl http://localhost/nginx-health
```

---

## 📊 Performance

### **Load Capacity**

- **Single Instance**: ~50-100 concurrent users
- **With Load Balancing**: ~100-200 concurrent users
- **Scalable**: Add more FastAPI instances in docker-compose.yml

### **Response Time**

- Health check: <10ms
- Single prediction: ~50-100ms
- Batch prediction (10 texts): ~200-300ms

---

## 🚧 Troubleshooting

### **Model not loading**
```bash
# Check if model file exists
ls -la models/sentiment_model.pkl

# Retrain if needed
python3 train_model.py
```

### **Database connection errors**
```bash
# Reinitialize database
docker exec sentiment_fastapi1 python init_db.py
```

### **503 Service Unavailable**
```bash
# Check if both instances are running
docker compose ps

# Check logs
docker compose logs sentiment_fastapi1
docker compose logs sentiment_fastapi2
```

---

## 🎓 Learning Points

This project demonstrates:

1. **Microservices Architecture** - Multiple independent services
2. **Load Balancing** - Distribute traffic for better performance
3. **API Security** - JWT-based authentication
4. **Database Integration** - PostgreSQL for user management
5. **Machine Learning Deployment** - Serving ML models via API
6. **Docker Orchestration** - Multi-container applications
7. **High Availability** - Automatic failover

---

## 📝 Next Steps

- [ ] Add rate limiting per user
- [ ] Implement caching (Redis)
- [ ] Add metrics (Prometheus)
- [ ] Set up monitoring dashboard (Grafana)
- [ ] Deploy to cloud (AWS/GCP/Azure)
- [ ] Add SSL/TLS certificates
- [ ] Implement API versioning
- [ ] Add comprehensive testing

---

## 📄 License

MIT License - Feel free to use for learning and production!

---

## 🤝 Contributing

Built for educational purposes. Feel free to extend and improve!

---

**Happy predicting! 🚀**