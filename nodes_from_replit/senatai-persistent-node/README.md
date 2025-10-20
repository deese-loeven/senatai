# Senatai Persistent Node

## Purpose
The **Persistent Node** is a multi-user web server version of Senatai designed for persistent online deployment. It serves as the central P2P hub for the Senatai network, enabling multiple users to access Canadian legislation data, participate in civic engagement, and synchronize with mobile apps and Sovereign Nodes.

## Key Features
- 🌐 **Always Online**: 24/7 web-accessible server
- 🐘 **PostgreSQL Database**: Scalable, production-grade database
- 👥 **Multi-User**: Supports thousands of concurrent users
- 🔗 **Network Hub**: Central node for P2P data synchronization
- 📡 **API Endpoints**: RESTful APIs for mobile apps and Sovereign Nodes
- 📊 **Real-Time Data**: Live connection to openparliament database

## Deployment Strategy

### Requirements
- Python 3.8+
- PostgreSQL 12+ (local or hosted)
- Environment variables for database connection
- Production WSGI server (Gunicorn recommended)

### Environment Variables

**Required**:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
SESSION_SECRET=your-secure-random-secret-key
```

**Optional**:
```bash
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
```

### Local Development

1. **Set up PostgreSQL database**:
   ```bash
   createdb senatai_production
   ```

2. **Set environment variables**:
   ```bash
   export DATABASE_URL="postgresql://localhost/senatai_production"
   export SESSION_SECRET="your-secret-key"
   ```

3. **Install dependencies**:
   ```bash
   pip install flask flask-login werkzeug psycopg2-binary gunicorn
   ```

4. **Initialize database**:
   ```bash
   python app.py  # Creates tables automatically
   ```

5. **Run development server**:
   ```bash
   python app.py
   ```

### Production Deployment

#### Option 1: Replit Deployment
1. Fork this project in Replit
2. Add secrets in Replit dashboard:
   - `DATABASE_URL`
   - `SESSION_SECRET`
3. Click "Deploy" button
4. Your app is live!

#### Option 2: VPS/Dedicated Server
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables** (in `/etc/environment` or `.env` file)

3. **Run with Gunicorn**:
   ```bash
   gunicorn --bind=0.0.0.0:5000 --workers=4 --timeout=120 app:app
   ```

4. **Configure reverse proxy** (Nginx recommended):
   ```nginx
   server {
       listen 80;
       server_name senatai.ca;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Set up SSL with Let's Encrypt**:
   ```bash
   certbot --nginx -d senatai.ca
   ```

#### Option 3: Three-Laptop P2P Setup
For connecting to the openparliament database on your Ubuntu laptop:

1. **On Ubuntu laptop** (PostgreSQL server):
   ```bash
   # Edit PostgreSQL config to allow remote connections
   sudo nano /etc/postgresql/14/main/postgresql.conf
   # Set: listen_addresses = '*'
   
   sudo nano /etc/postgresql/14/main/pg_hba.conf
   # Add: host all all 0.0.0.0/0 md5
   
   sudo systemctl restart postgresql
   ```

2. **On serving laptops**:
   ```bash
   export DATABASE_URL="postgresql://dan:senatai2025@216.211.67.180:5432/openparliament"
   gunicorn --bind=0.0.0.0:5000 --workers=2 app:app
   ```

3. **Configure domain** (senatai.ca):
   - Point DNS to your public IP
   - Set up port forwarding on router (port 80 → 5000)

### API Endpoints

**Health Check**:
```
GET /health
Returns: {"status": "healthy", "database": "connected"}
```

**Network Statistics**:
```
GET /api/stats
Returns: {
  "total_bills": 1234,
  "total_users": 567,
  "total_votes": 8901,
  "total_policap": 12345.67
}
```

**Future P2P Sync Endpoints** (Coming Soon):
- `POST /api/sync/predictions` - Upload anonymized predictions
- `GET /api/sync/bills` - Download bill updates
- `POST /api/sync/demographics` - Share anonymized demographic data

## Technical Architecture

**Database**: PostgreSQL with network accessibility
- All credentials loaded from environment variables
- Never hardcoded in code
- Connection pooling for performance
- Prepared statements for security

**Network Features**:
- Health check endpoint for monitoring
- API endpoints for mobile apps
- Future: P2P sync with Sovereign Nodes
- Future: Real-time updates via WebSockets

**Security**:
- Environment-based configuration
- No credentials in code or git
- HTTPS required in production
- Session management with secure cookies
- SQL injection protection via parameterized queries

## File Structure
```
senatai-persistent-node/
├── app.py                    # Main application (PostgreSQL-only)
├── question_generator.py     # Sophisticated question system
├── topic_matcher.py          # Bill matching engine
├── icebreakers.py           # Rotating welcome messages
├── demographics.py          # Optional demographic collection
├── policap_rewards.py       # Reward calculation
├── badges.py                # Two-tier badge system
├── init_postgres_tables.sql # Database schema
├── templates/               # Jinja2 HTML templates
├── static/                  # CSS and assets
└── requirements.txt         # Python dependencies
```

## Monitoring

**Health Checks**:
```bash
curl https://senatai.ca/health
```

**Database Status**:
```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM legislation;"
```

**Logs**:
```bash
# Gunicorn logs
tail -f /var/log/gunicorn/senatai.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

## Scaling

**Horizontal Scaling**:
- Add more Gunicorn workers: `--workers=8`
- Deploy multiple instances behind load balancer
- PostgreSQL read replicas for analytics queries

**Vertical Scaling**:
- Increase server RAM/CPU
- Optimize PostgreSQL configuration
- Enable connection pooling (PgBouncer)

## Backup Strategy

**Database Backups**:
```bash
# Daily automated backup
pg_dump $DATABASE_URL > senatai_backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump $DATABASE_URL | gzip > senatai_backup_$(date +%Y%m%d).sql.gz
```

**Restore**:
```bash
psql $DATABASE_URL < senatai_backup_20251019.sql
```

---

**Production Ready**: Designed for 24/7 operation with thousands of users. Tested with PostgreSQL 12+ and Python 3.8+.
