---
name: deploy
description: Deployment workflow and best practices
---

# Deployment Skill

## Overview

Follow these guidelines for safe, reliable deployments.

## Pre-Deployment Checklist

### 1. Code Changes
- [ ] All code changes committed to git
- [ ] Pull request reviewed and approved
- [ ] Main branch up to date
- [ ] No uncommitted secrets

### 2. Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Smoke tests created/updated

### 3. Configuration
- [ ] Environment variables configured
- [ ] Feature flags set correctly
- [ ] Rollback plan prepared

## Deployment Process

### 1. Build
```bash
# Create production build
npm run build
# or
python setup.py build
```

### 2. Test in Staging
```bash
# Deploy to staging first
deploy --env=staging

# Run smoke tests
pytest tests/smoke.py -k deploy
```

### 3. Deploy to Production
```bash
# Monitor during deployment
deploy --env=production --monitor

# Check health endpoints
curl https://api.example.com/health
```

### 4. Verify
```bash
# Run post-deployment checks
./scripts/post-deploy-check.sh
```

## Rollback Procedure

If issues occur:

```bash
# Immediate rollback
rollback --env=production --to=previous

# Verify rollback
curl https://api.example.com/health
```

## Best Practices

1. **Blue-Green Deployments**: Keep two identical environments
2. **Canary Releases**: Gradually shift traffic
3. **Feature Flags**: Enable features incrementally
4. **Monitor Everything**: Metrics, logs, alerts
5. **Automate**: Manual steps fail under pressure
6. **Document**: Record what was deployed and when

## Environment-Specific Notes

### Development
- Auto-deploy on main branch push
- Minimal monitoring required
- Fast iteration

### Staging
- Mirror production configuration
- Full testing suite
- Performance tests

### Production
- Multi-region consideration
- Full monitoring and alerting
- Rollback plan required
