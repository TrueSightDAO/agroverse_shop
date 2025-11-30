# truesight.me GitHub Pages Setup

## Current Issue

`truesight.me` is currently pointing to `TrueSightDAO/truesight_me_beta` instead of the production repository.

## Repository Structure

Based on the pattern with `agroverse.shop`, you likely have:
- **Production**: `TrueSightDAO/truesight_me` (or `truesight_me_prod`) → `truesight.me` and `www.truesight.me`
- **Beta**: `TrueSightDAO/truesight_me_beta` → `beta.truesight.me` (if you want a beta subdomain)

## Current DNS Configuration

**Route53 Hosted Zone**: `Z0032474227N6EQ3Z4QU`

**Current Records**:
- `truesight.me` → A record → `185.199.108.153` ❌ (only 1 IP, should have 4)
- `www.truesight.me` → CNAME → `TrueSightDAO.github.io` ✅

## Issues to Fix

### 1. Missing A Records for Apex Domain

GitHub Pages requires **4 A records** for apex domains. Currently only 1 is configured.

**Fix**: Add the missing 3 A records:
- `185.199.108.153` ✅ (already exists)
- `185.199.109.153` ❌ (missing)
- `185.199.110.153` ❌ (missing)
- `185.199.111.153` ❌ (missing)

### 2. Repository Configuration

The `truesight_me_beta` repository likely has a CNAME file with `truesight.me`, which is why GitHub routes the production domain to the beta repo.

**Fix**: 
- Production repo should have CNAME: `truesight.me`
- Beta repo should have CNAME: `beta.truesight.me` (if you want a beta subdomain)

## Step-by-Step Fix

### Step 1: Update A Records

Add all 4 GitHub Pages IP addresses:

```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id Z0032474227N6EQ3Z4QU \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "truesight.me",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [
          {"Value": "185.199.108.153"},
          {"Value": "185.199.109.153"},
          {"Value": "185.199.110.153"},
          {"Value": "185.199.111.153"}
        ]
      }
    }]
  }'
```

### Step 2: Configure Production Repository

1. **Go to**: `https://github.com/TrueSightDAO/truesight_me/settings/pages` (or `truesight_me_prod` if that's the repo name)

2. **Enable GitHub Pages**:
   - Source: Deploy from branch
   - Branch: `main` (or your Pages branch)
   - Folder: `/ (root)`

3. **Add Custom Domain**:
   - Custom domain: `truesight.me`
   - Click "Save"
   - This will create/update the CNAME file automatically

4. **Verify Domain** (if prompted):
   - Add the verification TXT record to Route53
   - Wait 5-10 minutes
   - Click "Verify"

### Step 3: Configure Beta Repository (Optional)

If you want a beta subdomain:

1. **Go to**: `https://github.com/TrueSightDAO/truesight_me_beta/settings/pages`

2. **Update Custom Domain**:
   - Remove `truesight.me` if it's there
   - Add custom domain: `beta.truesight.me`
   - Click "Save"

3. **Add DNS CNAME Record** (if beta subdomain doesn't exist):
   ```bash
   aws route53 change-resource-record-sets \
     --hosted-zone-id Z0032474227N6EQ3Z4QU \
     --change-batch '{
       "Changes": [{
         "Action": "CREATE",
         "ResourceRecordSet": {
           "Name": "beta.truesight.me",
           "Type": "CNAME",
           "TTL": 300,
           "ResourceRecords": [{"Value": "TrueSightDAO.github.io"}]
         }
       }]
     }'
   ```

### Step 4: Remove CNAME from Beta Repo (If Needed)

If `truesight_me_beta` has `truesight.me` in its CNAME file:

1. Go to the beta repository
2. Remove the custom domain `truesight.me` from Settings → Pages
3. Or manually update the CNAME file to `beta.truesight.me` (if using beta subdomain)

## Verification

After making changes:

```bash
# Check A records (should return all 4 IPs)
dig truesight.me +short

# Check www CNAME
dig www.truesight.me CNAME +short
# Should return: TrueSightDAO.github.io

# Check if site is accessible
curl -I https://truesight.me
# Should show: server: GitHub.com
```

## Expected Configuration

### DNS Records (Route53)
| Domain | Type | Value | Status |
|--------|------|-------|--------|
| `truesight.me` | A | 4 GitHub Pages IPs | ⚠️ Needs update (currently only 1) |
| `www.truesight.me` | CNAME | `TrueSightDAO.github.io` | ✅ Correct |
| `beta.truesight.me` | CNAME | `TrueSightDAO.github.io` | ⚠️ Optional, create if needed |

### Repository CNAME Files
| Repository | CNAME File Content | Status |
|------------|-------------------|--------|
| `truesight_me` (prod) | `truesight.me` | ⚠️ Needs to be set |
| `truesight_me_beta` | `beta.truesight.me` | ⚠️ Needs to be updated (currently has `truesight.me`) |

## Quick Fix Commands

**Update A records to include all 4 IPs**:
```bash
cat > /tmp/truesight_me_a_records.json << 'EOF'
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "truesight.me",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [
        {"Value": "185.199.108.153"},
        {"Value": "185.199.109.153"},
        {"Value": "185.199.110.153"},
        {"Value": "185.199.111.153"}
      ]
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id Z0032474227N6EQ3Z4QU \
  --change-batch file:///tmp/truesight_me_a_records.json
```

## Next Steps

1. ✅ Update A records (add missing 3 IPs)
2. ⚠️ Configure production repo in GitHub Pages settings
3. ⚠️ Update beta repo to use `beta.truesight.me` (if desired)
4. ⚠️ Wait 10-30 minutes for GitHub verification

