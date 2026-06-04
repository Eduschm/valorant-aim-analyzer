# API Contract

## Frontend-Backend Communication Specification

This document defines the contract between the frontend (Next.js) and backend services.

## Base URL

- Development: `http://localhost:3001`
- Production: Will be set via `NEXT_PUBLIC_API_URL` environment variable

## Content-Type

All requests and responses use `application/json`.

## Authentication

For Phase 1, authentication is placeholder. Phase 2 will implement:
- Bearer token in Authorization header
- Magic link email verification
- Session management

## Response Format

### Success Response
```json
{
  "success": true,
  "data": {...}
}
```

### Error Response
```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

## Error Codes

- `400` - Bad Request (validation error)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Server Error

---

## Authentication Endpoints

### POST /api/auth/signin
Send magic link email

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "message": "Magic link sent to email",
    "expiresIn": 3600
  }
}
```

---

### POST /api/auth/callback
Verify magic link token

**Request:**
```json
{
  "token": "abc123..."
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "sessionToken": "session_token_here",
    "user": {
      "id": "user_123",
      "email": "user@example.com"
    }
  }
}
```

---

### POST /api/auth/link-riot-id
Link Riot ID to account

**Request:**
```json
{
  "gameName": "PlayerName",
  "tagLine": "1234"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "linked": true,
    "riotId": "PlayerName#1234"
  }
}
```

---

### GET /api/auth/session
Get current session

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "riotId": "PlayerName#1234"
    },
    "isAuthenticated": true
  }
}
```

---

## Analysis Endpoints

### POST /api/analysis/tracker
Create tracker-only analysis

**Request:**
```json
{
  "riotId": "PlayerName#1234"
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "data": {
    "id": "analysis_123",
    "status": "processing",
    "riotId": "PlayerName#1234",
    "createdAt": "2024-06-04T12:00:00Z",
    "estimatedTime": 30
  }
}
```

---

### GET /api/analysis/:id
Get analysis details

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": "analysis_123",
    "riotId": "PlayerName#1234",
    "status": "completed",
    "createdAt": "2024-06-04T12:00:00Z",
    "stats": {
      "headshotPercent": 42.5,
      "adr": 156.8,
      "rankDelta": "+12 RR",
      "matchesAnalyzed": 20
    },
    "weaponStats": [
      {
        "weapon": "Vandal",
        "kills": 145,
        "accuracy": 22.4,
        "headshots": 35
      },
      {
        "weapon": "Phantom",
        "kills": 89,
        "accuracy": 19.8,
        "headshots": 18
      }
    ],
    "agentStats": [
      {
        "agent": "Jett",
        "matches": 8,
        "winRate": 62.5,
        "kills": 156
      }
    ],
    "coachingReport": "# Coaching Report\n\n## Strengths\n..."
  }
}
```

---

### GET /api/analysis/history
Get user's analysis history

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `pageSize` (optional): Items per page (default: 10)
- `sortBy` (optional): Field to sort by (default: createdAt)
- `sortOrder` (optional): 'asc' or 'desc' (default: 'desc')

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "analyses": [
      {
        "id": "analysis_123",
        "riotId": "PlayerName#1234",
        "status": "completed",
        "createdAt": "2024-06-04T12:00:00Z",
        "stats": {
          "headshotPercent": 42.5,
          "adr": 156.8
        }
      }
    ],
    "total": 45,
    "page": 1,
    "pageSize": 10
  }
}
```

---

## User Endpoints

### GET /api/user/profile
Get user profile

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "riotId": "PlayerName#1234",
    "gameName": "PlayerName",
    "tagLine": "1234",
    "tier": "Premium",
    "creditsUsed": 7,
    "creditsLimit": 10,
    "createdAt": "2024-05-01T10:00:00Z"
  }
}
```

---

### PUT /api/user/profile
Update user profile

**Request:**
```json
{
  "riotId": "NewName#5678"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "riotId": "NewName#5678",
    "updatedAt": "2024-06-04T15:00:00Z"
  }
}
```

---

## Phase 2: Clip Analysis Endpoints (Future)

### POST /api/upload/presigned-url
Get presigned S3/R2 URL for video upload

**Request:**
```json
{
  "fileName": "clip.mp4",
  "fileSize": 52428800,
  "fileType": "video/mp4"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "uploadUrl": "https://s3.example.com/...",
    "uploadId": "upload_456"
  }
}
```

---

### POST /api/analysis/clip
Submit clip for analysis

**Request:**
```json
{
  "uploadId": "upload_456",
  "fileName": "clip.mp4",
  "duration": 180,
  "context": {
    "map": "Ascent",
    "agent": "Jett",
    "round": 5
  }
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "data": {
    "id": "analysis_124",
    "status": "processing",
    "queuePosition": 3,
    "estimatedTime": 120
  }
}
```

---

### GET /api/analysis/:id/video-url
Get processed video URL

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "videoUrl": "https://cdn.example.com/analysis_124/video.mp4",
    "expiresIn": 3600
  }
}
```

---

### GET /api/analysis/:id/frames
Get annotated frames

**Query Parameters:**
- `engagementId` (optional): Get frames for specific engagement
- `format` (optional): 'jpg' or 'webp'

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "frames": [
      {
        "index": 0,
        "timestamp": 0.0,
        "url": "https://cdn.example.com/frame_0.jpg",
        "detections": [
          {
            "type": "enemy_head",
            "x": 512,
            "y": 384,
            "width": 32,
            "height": 48,
            "confidence": 0.95
          }
        ],
        "crosshair": {
          "x": 960,
          "y": 540
        }
      }
    ]
  }
}
```

---

### GET /api/analysis/:id/engagements
Get engagement timeline data

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "engagements": [
      {
        "id": "eng_1",
        "timestamp": 5.2,
        "duration": 0.8,
        "enemyCount": 1,
        "accuracy": "excellent",
        "offset": 12,
        "reactionTime": 250,
        "preAimAccuracy": 0.92
      }
    ]
  }
}
```

---

## Polling Strategy

For async operations (analysis processing):

1. Create analysis → receive `id` and `status`
2. Poll `GET /api/analysis/:id` every 2-5 seconds
3. Stop polling when `status` is 'completed' or 'failed'
4. Display `estimatedTime` to user if status is 'processing'

Example polling logic:
```javascript
const pollAnalysis = async (analysisId, maxAttempts = 120) => {
  for (let i = 0; i < maxAttempts; i++) {
    const response = await fetch(`/api/analysis/${analysisId}`)
    const { data } = await response.json()

    if (data.status === 'completed' || data.status === 'failed') {
      return data
    }

    await new Promise(resolve => setTimeout(resolve, 2000))
  }
}
```

---

## Rate Limiting

All endpoints will eventually have rate limiting:
- 100 requests per minute per user (Phase 2)
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## CORS Configuration

Backend should allow:
- Origin: `http://localhost:3000` (dev), production domain
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type, Authorization

---

## Caching Strategy

Frontend caching recommendations:
- Analysis history: Cache for 5 minutes
- User profile: Cache for 10 minutes
- Analysis details: Cache indefinitely (immutable)
- Use SWR/React Query for automatic cache invalidation

---

## Timeline for Implementation

- **Phase 1**: Auth + Tracker analysis endpoints (Weeks 1-2)
- **Phase 2**: Clip upload + video analysis endpoints (Weeks 3-6)
- **Phase 3**: Monetization + advanced metrics endpoints (Weeks 7-12)

---

## Questions?

- Frontend team lead: @eduardodev
- Backend team lead: @backenddev
- Slack: #valorant-analyzer-integration
