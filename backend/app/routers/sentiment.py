from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.db.models import User
from app.dependencies.auth_dependencies import get_current_active_user
from app.core.config import settings
from app.core.logging import logger
import socket

router = APIRouter(
    prefix="/api",
    tags=["Sentiment Analysis"]
)


class PredictRequest(BaseModel):
    """Request model for sentiment prediction"""
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "I love this product! It's amazing!"
            }
        }


class PredictResponse(BaseModel):
    """Response model for sentiment prediction"""
    text: str
    sentiment: str
    confidence: float
    predicted_by: str
    user: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "I love this product! It's amazing!",
                "sentiment": "positive",
                "confidence": 0.95,
                "predicted_by": "FastAPI-1",
                "user": "demo_user"
            }
        }


class BatchPredictRequest(BaseModel):
    """Request model for batch sentiment prediction"""
    texts: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "I love this!",
                    "This is terrible",
                    "Not sure about this"
                ]
            }
        }


class BatchPredictResponse(BaseModel):
    """Response model for batch predictions"""
    predictions: List[dict]
    predicted_by: str
    user: str
    total_count: int


@router.post("/predict", response_model=PredictResponse)
async def predict_sentiment(
    request: PredictRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Predict sentiment for a single text
    
    Requires: Valid JWT token
    
    **Example Request:**
    ```json
    {
        "text": "I love this product! It's amazing!"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "text": "I love this product! It's amazing!",
        "sentiment": "positive",
        "confidence": 0.95,
        "predicted_by": "FastAPI-1",
        "user": "demo_user"
    }
    ```
    """
    from app.main import sentiment_model
    
    if sentiment_model is None:
        logger.error("Sentiment model not loaded!")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not available"
        )
    
    logger.info(f"Prediction request from {current_user.username}: '{request.text[:50]}...'")
    
    try:
        # Predict sentiment
        prediction = sentiment_model.predict([request.text])[0]
        
        # Get confidence score
        probabilities = sentiment_model.predict_proba([request.text])[0]
        confidence = float(max(probabilities))
        
        logger.info(f"Prediction: {prediction} (confidence: {confidence:.2f}) by {settings.INSTANCE_ID}")
        
        return {
            "text": request.text,
            "sentiment": prediction,
            "confidence": confidence,
            "predicted_by": settings.INSTANCE_ID,
            "user": current_user.username
        }
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/batch", response_model=BatchPredictResponse)
async def predict_sentiment_batch(
    request: BatchPredictRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Predict sentiment for multiple texts at once
    
    Requires: Valid JWT token
    
    **Example Request:**
    ```json
    {
        "texts": [
            "I love this!",
            "This is terrible",
            "Not sure about this"
        ]
    }
    ```
    
    **Example Response:**
    ```json
    {
        "predictions": [
            {"text": "I love this!", "sentiment": "positive", "confidence": 0.95},
            {"text": "This is terrible", "sentiment": "negative", "confidence": 0.89},
            {"text": "Not sure about this", "sentiment": "neutral", "confidence": 0.67}
        ],
        "predicted_by": "FastAPI-1",
        "user": "demo_user",
        "total_count": 3
    }
    ```
    """
    from app.main import sentiment_model
    
    if sentiment_model is None:
        logger.error("Sentiment model not loaded!")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not available"
        )
    
    logger.info(f"Batch prediction request from {current_user.username}: {len(request.texts)} texts")
    
    try:
        # Predict all at once
        predictions = sentiment_model.predict(request.texts)
        probabilities = sentiment_model.predict_proba(request.texts)
        
        results = []
        for text, pred, prob in zip(request.texts, predictions, probabilities):
            results.append({
                "text": text,
                "sentiment": pred,
                "confidence": float(max(prob))
            })
        
        logger.info(f"Batch prediction completed: {len(results)} predictions by {settings.INSTANCE_ID}")
        
        return {
            "predictions": results,
            "predicted_by": settings.INSTANCE_ID,
            "user": current_user.username,
            "total_count": len(results)
        }
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@router.get("/model/info")
async def get_model_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get information about the loaded sentiment model
    
    Requires: Valid JWT token
    """
    from app.main import sentiment_model
    
    if sentiment_model is None:
        return {
            "status": "not_loaded",
            "instance_id": settings.INSTANCE_ID,
            "hostname": socket.gethostname()
        }
    
    return {
        "status": "loaded",
        "model_type": type(sentiment_model).__name__,
        "classes": list(sentiment_model.classes_) if hasattr(sentiment_model, 'classes_') else [],
        "instance_id": settings.INSTANCE_ID,
        "hostname": socket.gethostname(),
        "model_path": settings.MODEL_PATH
    }