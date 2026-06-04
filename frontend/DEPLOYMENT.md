# Deployment Guide

## Vercel (Recommended - Zero Config)

### Option 1: Git Push (Easiest)
1. Ensure your code is committed and pushed to GitHub
2. Go to https://vercel.com and sign in with your GitHub account
3. Click "Add New..." > "Project"
4. Select the `valorant-aim-analyzer` repository
5. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Environment Variables**: Add `NEXT_PUBLIC_API_URL`
6. Click "Deploy"

### Option 2: Vercel CLI
```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel

# For production deployment
vercel --prod
```

### Environment Variables
Set these in Vercel dashboard (Settings > Environment Variables):
```
NEXT_PUBLIC_API_URL=<your-backend-url>
NEXT_PUBLIC_AUTH_URL=<your-frontend-url>
```

## Docker Deployment

### Build Docker Image
```bash
docker build -f Dockerfile -t valorant-aim-analyzer-frontend:latest .
```

### Run Container
```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://api.example.com \
  valorant-aim-analyzer-frontend:latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://api:3001
      NEXT_PUBLIC_AUTH_URL: http://localhost:3000
    depends_on:
      - api
```

## Self-Hosted (VPS/Server)

### Prerequisites
- Node.js 18+
- npm or yarn
- PM2 (for process management)

### Deployment Steps

1. **Clone repository**
```bash
git clone <repo-url>
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Build application**
```bash
npm run build
```

4. **Configure environment**
```bash
cp .env.example .env.local
# Edit .env.local with production values
```

5. **Start with PM2**
```bash
npm install -g pm2
pm2 start npm --name "valorant-frontend" -- start
pm2 startup
pm2 save
```

6. **Nginx Reverse Proxy**
```nginx
server {
    listen 80;
    server_name analyzer.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

7. **SSL with Let's Encrypt**
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d analyzer.example.com
```

## AWS Deployment

### Using Amplify (Easiest)
1. Connect GitHub repository to AWS Amplify
2. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Start command**: `npm start`
3. Add environment variables
4. Deploy

### Using EC2 + Application Load Balancer
1. Launch EC2 instance (Ubuntu 22.04)
2. Install Node.js, npm, PM2
3. Clone and deploy using self-hosted steps above
4. Create Application Load Balancer
5. Configure target group pointing to EC2 instance

## Google Cloud Run

```bash
# Build and deploy
gcloud run deploy valorant-analyzer \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=<backend-url>
```

## Monitoring & Maintenance

### Health Checks
- Monitor `/api/health` endpoint
- Set up uptime monitoring (UptimeRobot, Pingdom)

### Logs
- Vercel: Built-in logging dashboard
- Self-hosted: Use PM2 logs or centralized logging (DataDog, Sentry)

### Performance
- Enable Vercel Analytics for real user monitoring
- Monitor Core Web Vitals in Vercel dashboard
- Use NextJS Image Optimization

### Updates
```bash
# Check for dependency updates
npm outdated

# Update packages
npm update

# Test before deploying
npm run build && npm run start
```

## Rollback Procedure

### Vercel
- Deployments > Select previous version > Redeploy

### Self-hosted with git
```bash
git log --oneline
git revert <commit-hash>
git push
npm run build
pm2 restart valorant-frontend
```

## Performance Optimization

1. **Enable compression** in Nginx/server
2. **Use CDN** for static assets
3. **Configure caching** headers
4. **Monitor Core Web Vitals** via PageSpeed Insights
5. **Optimize images** with Next.js Image component
6. **Lazy load components** with next/dynamic

## Troubleshooting

### Build fails
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
npm run build
```

### Port conflicts
```bash
# Change port
PORT=3001 npm start
```

### Environment variables not loading
- Verify `.env.local` is in root (`frontend/` directory)
- For Vercel: Check dashboard, not local file
- Restart application after changing

## Security Checklist

- [ ] Set up HTTPS/SSL
- [ ] Configure CORS for API
- [ ] Enable rate limiting
- [ ] Use environment variables for secrets
- [ ] Set security headers (CSP, X-Frame-Options, etc.)
- [ ] Regular dependency updates
- [ ] Enable authentication
- [ ] Use HTTPS only

## Support

For issues:
1. Check logs: `pm2 logs` or Vercel dashboard
2. Verify environment variables are set
3. Check backend API connectivity
4. Review recent commits and rollback if needed
