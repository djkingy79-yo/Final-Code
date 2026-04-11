# Backup Strategy — Appeal Case Manager

## MongoDB Backup

### Automated Daily Backup (Recommended)

```bash
#!/bin/bash
# /etc/cron.daily/appeal-backup.sh
BACKUP_DIR="/backups/appeal-case-manager"
DATE=$(date +%Y-%m-%d_%H%M)
MONGO_URI="mongodb://localhost:27017"
DB_NAME="appeal_case_manager"

mkdir -p "$BACKUP_DIR"

# Dump database
mongodump --uri="$MONGO_URI" --db="$DB_NAME" --out="$BACKUP_DIR/$DATE"

# Compress
tar -czf "$BACKUP_DIR/$DATE.tar.gz" -C "$BACKUP_DIR" "$DATE"
rm -rf "$BACKUP_DIR/$DATE"

# Retain last 30 days
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/$DATE.tar.gz"
```

### MongoDB Atlas (Cloud)

If using MongoDB Atlas:
- Automated backups are enabled by default on M10+ clusters
- Point-in-time recovery available on M10+ with continuous backup
- Configure backup schedule in Atlas dashboard: **Project > Clusters > Backup**

### Manual Backup

```bash
# Full database dump
mongodump --uri="mongodb://localhost:27017" --db=appeal_case_manager --out=/backups/manual

# Restore from backup
mongorestore --uri="mongodb://localhost:27017" --db=appeal_case_manager /backups/manual/appeal_case_manager
```

## What to Back Up

| Data | Method | Frequency |
|------|--------|-----------|
| MongoDB (cases, users, reports) | mongodump | Daily |
| Uploaded documents | File system copy | Daily |
| Environment variables (.env) | Encrypted copy | On change |
| SSL certificates | Encrypted copy | On renewal |

## Restore Procedure

1. Stop the application
2. Restore MongoDB: `mongorestore --drop --db=appeal_case_manager /path/to/backup`
3. Restore uploaded files to the correct directory
4. Verify `.env` is correct
5. Start the application
6. Verify `GET /api/health` returns healthy
7. Test login and core functionality

## Disaster Recovery

- **RPO** (Recovery Point Objective): 24 hours (daily backups)
- **RTO** (Recovery Time Objective): 2 hours
- Store backups in a separate location (different server, S3 bucket, or external drive)
- Test restore procedure quarterly
