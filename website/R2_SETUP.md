# Cloudflare R2 Setup Guide for VideoGrid Component

This guide will walk you through setting up your Cloudflare R2 bucket to work with the VideoGrid component on your Cloudflare Pages site.

## Overview

The VideoGrid component displays videos from a Cloudflare R2 bucket in a responsive 2x6 grid with hover-to-play functionality. Since your website is already deployed on Cloudflare Pages, integration is straightforward.

## Prerequisites

- Active Cloudflare account
- Website deployed on Cloudflare Pages
- Videos you want to display (MP4 format recommended)

---

## Step 1: Create an R2 Bucket

1. **Navigate to R2 in Cloudflare Dashboard**

   - Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - Go to **R2** in the left sidebar
   - Click **Create bucket**

2. **Configure Your Bucket**

   - **Bucket name**: Choose a name (e.g., `my-thesis-videos`)
     - ⚠️ **Note this down** - you'll need it for configuration
   - **Location**: Choose the location closest to your users (Auto is fine)
   - Click **Create bucket**

3. **Note Your Account ID**
   - You can find your Account ID in the R2 overview page
   - Format: `1234567890abcdef1234567890abcdef`
   - ⚠️ **Note this down** - you'll need it for configuration

---

## Step 2: Make Your Bucket Public

The VideoGrid component uses direct URL access, so you need to make your bucket publicly accessible.

### Option A: Public Bucket (R2.dev subdomain)

1. **Enable Public Access**

   - In your bucket settings, go to **Settings** tab
   - Scroll to **Public access**
   - Click **Allow Access**
   - Confirm by clicking **Allow Access** again

2. **Get Your Public Bucket URL**
   - After enabling public access, you'll see a **Public R2.dev Bucket URL**
   - Format: `https://pub-[hash].r2.dev`
   - Example: `https://pub-abc123def456.r2.dev`
   - ⚠️ **[INSERT_YOUR_R2_BUCKET_URL_HERE]** - Copy this entire URL

### Option B: Custom Domain (Recommended for Production)

1. **Connect a Custom Domain**

   - In your bucket settings, go to **Settings** tab
   - Scroll to **Custom Domains**
   - Click **Connect Domain**
   - Enter your domain (e.g., `videos.yourdomain.com`)
   - Follow DNS configuration instructions
   - Wait for DNS propagation (usually 5-10 minutes)

2. **Get Your Custom Domain URL**
   - Format: `https://videos.yourdomain.com`
   - ⚠️ **[INSERT_YOUR_R2_BUCKET_URL_HERE]** - Use this URL

---

## Step 3: Upload Your Videos

1. **Create the Demos Folder**

   - In your R2 bucket, click **Upload**
   - Create a folder structure: `Demos/`
   - The VideoGrid component expects videos in this folder

2. **Upload Videos**

   - Click **Upload** in the `Demos` folder
   - Select your video files (MP4 recommended)
   - Wait for upload to complete

3. **Name Your Videos**

   - The component expects specific filenames (you can customize this)
   - Default expected files:
     - `demo1.mp4`
     - `demo2.mp4`
     - `demo3.mp4`
     - ... through `demo12.mp4`
   - **OR** customize the filenames in your component usage (see Usage section below)

4. **Verify Public Access**
   - After uploading, try accessing a video directly:
   - `https://[YOUR_R2_URL]/Demos/demo1.mp4`
   - You should be able to view the video in your browser

---

## Step 4: Configure Environment Variables

1. **Copy the Example Environment File**

   ```bash
   cd website
   cp .env.example .env
   ```

2. **Edit the .env File**
   Open `website/.env` and replace the placeholders:

   ```env
   # ⚠️ REPLACE THIS with your actual R2 public URL
   PUBLIC_R2_BUCKET_URL=https://pub-abc123def456.r2.dev
   # OR
   PUBLIC_R2_BUCKET_URL=https://videos.yourdomain.com

   # Optional: For reference
   PUBLIC_R2_ACCOUNT_ID=1234567890abcdef1234567890abcdef
   PUBLIC_R2_BUCKET_NAME=my-thesis-videos
   ```

3. **Verify Configuration**
   - Make sure there are no square brackets `[]` in your URL
   - The URL should start with `https://`
   - Don't include a trailing slash

---

## Step 5: Configure Cloudflare Pages Environment Variables

For your deployed site to work, you need to set environment variables in Cloudflare Pages.

1. **Go to Your Pages Project**

   - Navigate to **Workers & Pages** in Cloudflare Dashboard
   - Select your Pages project

2. **Add Environment Variables**

   - Go to **Settings** → **Environment variables**
   - Click **Add variable**
   - Add the following:

   | Variable Name          | Value           | Environment          |
   | ---------------------- | --------------- | -------------------- |
   | `PUBLIC_R2_BUCKET_URL` | `[YOUR_R2_URL]` | Production & Preview |

   Example value: `https://pub-abc123def456.r2.dev`

3. **Redeploy Your Site**
   - After adding variables, trigger a new deployment
   - Go to **Deployments** tab
   - Click **Retry deployment** on the latest deployment
   - OR push a new commit to trigger automatic deployment

---

## Step 6: Use the VideoGrid Component

### Basic Usage (Default Videos)

In any `.mdx` or `.astro` file:

```astro
---
import VideoGrid from '@/components/VideoGrid.astro';
---

<VideoGrid title="My Research Demos" />
```

This will automatically look for `demo1.mp4` through `demo12.mp4` in the `Demos/` folder.

### Custom Video Files

If your videos have different names:

```astro
---
import VideoGrid from '@/components/VideoGrid.astro';
---

<VideoGrid
  title="Experiment Results"
  videoFiles={[
    "experiment-1-success.mp4",
    "experiment-2-failure.mp4",
    "experiment-3-success.mp4",
    "baseline-comparison.mp4",
    "ablation-study-1.mp4",
    "ablation-study-2.mp4",
    "real-world-test-1.mp4",
    "real-world-test-2.mp4",
    "sim-to-real-transfer.mp4",
    "final-demo.mp4",
    "failure-cases.mp4",
    "future-work-preview.mp4"
  ]}
/>
```

### Without Title

```astro
<VideoGrid videoFiles={["video1.mp4", "video2.mp4"]} />
```

---

## Testing Your Setup

### 1. Test R2 Public Access

Open your browser and navigate to:

```
https://[YOUR_R2_URL]/Demos/demo1.mp4
```

**Expected**: The video should load and play in your browser.

**If it doesn't work**:

- ✅ Check that public access is enabled
- ✅ Verify the file exists in the `Demos/` folder
- ✅ Check the filename matches exactly (case-sensitive)

### 2. Test Local Development

```bash
cd website
bun dev
```

Visit `http://localhost:4321` and navigate to the page with your VideoGrid.

**Expected**: You should see a 2x6 grid of videos that play on hover.

**If you see a yellow warning box**:

- ✅ Check that `.env` file exists in `website/` directory
- ✅ Verify `PUBLIC_R2_BUCKET_URL` is set correctly
- ✅ Make sure there are no `[INSERT_...]` placeholders remaining

### 3. Test Production Deployment

After deploying to Cloudflare Pages:

1. Visit your production site
2. Navigate to the page with VideoGrid
3. Open browser DevTools (F12) → Network tab
4. Hover over videos and check for:
   - Videos should load with 200 status codes
   - No CORS errors
   - No 403 (forbidden) errors

---

## Troubleshooting

### Videos Not Loading

**Problem**: Videos show loading spinner indefinitely

**Solutions**:

1. ✅ Verify public access is enabled on your R2 bucket
2. ✅ Check that files exist in the `Demos/` folder
3. ✅ Test direct URL access: `https://[YOUR_R2_URL]/Demos/demo1.mp4`
4. ✅ Check browser console for errors (F12)
5. ✅ Verify video files are valid MP4 format

### CORS Errors

**Problem**: Console shows "CORS policy" errors

**Solutions**:

1. ✅ In R2 bucket settings, go to **Settings** → **CORS Policy**
2. ✅ Add this CORS configuration:
   ```json
   [
     {
       "AllowedOrigins": ["*"],
       "AllowedMethods": ["GET", "HEAD"],
       "AllowedHeaders": ["*"],
       "MaxAgeSeconds": 3600
     }
   ]
   ```
3. ✅ Save and wait a few minutes for changes to propagate

### Configuration Warning Showing

**Problem**: Yellow warning box appears on the page

**Solutions**:

1. ✅ Check `.env` file exists in `website/` directory
2. ✅ Verify no placeholders like `[INSERT_YOUR_R2_BUCKET_URL_HERE]` remain
3. ✅ For production, check Cloudflare Pages environment variables are set
4. ✅ Restart development server after changing `.env`

### Videos Play on Mobile but Not Desktop (or vice versa)

**Problem**: Videos work on one device type but not another

**Solutions**:

1. ✅ Check video codec compatibility (H.264 is most compatible)
2. ✅ Verify videos aren't too large (compress if needed)
3. ✅ Test in different browsers (Chrome, Firefox, Safari)

---

## Video Optimization Tips

### Recommended Video Specifications

- **Format**: MP4 (H.264 codec)
- **Resolution**: 1920x1080 or 1280x720
- **Bitrate**: 2-5 Mbps for 1080p, 1-2 Mbps for 720p
- **Frame rate**: 30 fps
- **Duration**: Keep under 30 seconds for demos

### Compressing Videos

Using FFmpeg to optimize videos:

```bash
# Compress video to web-friendly size
ffmpeg -i input.mp4 -vcodec h264 -acodec aac -vf scale=1280:720 -b:v 2M -preset slow output.mp4

# Remove audio (if not needed, saves bandwidth)
ffmpeg -i input.mp4 -c:v copy -an output.mp4
```

---

## Cost Considerations

### R2 Pricing (as of 2024)

- **Storage**: $0.015 per GB/month
- **Class A Operations** (writes): $4.50 per million requests
- **Class B Operations** (reads): $0.36 per million requests
- **Egress**: FREE (this is the big advantage of R2!)

### Example Cost Calculation

For a thesis website with 12 demo videos:

- **Videos**: 12 × 50 MB = 600 MB = 0.6 GB
- **Storage cost**: $0.015 × 0.6 = **$0.009/month**
- **Reads**: 1000 visitors × 12 videos = 12,000 requests
- **Read cost**: $0.36 × (12,000/1,000,000) = **$0.004/month**

**Total**: ~$0.01/month (essentially free for research websites!)

---

## Security Best Practices

1. **Public Access**: Only enable for videos you want to be publicly accessible
2. **Bucket Policy**: Configure bucket policies if you need more control
3. **Environment Variables**: Never commit `.env` file to Git
4. **Custom Domain**: Use a subdomain for better organization
5. **Rate Limiting**: Consider Cloudflare's rate limiting if you expect high traffic

---

## Quick Reference

### Configuration Checklist

- [ ] R2 bucket created
- [ ] Public access enabled
- [ ] Account ID noted
- [ ] Public R2.dev URL or custom domain obtained
- [ ] `Demos/` folder created in bucket
- [ ] Videos uploaded to `Demos/` folder
- [ ] Video filenames match component configuration
- [ ] `.env.example` copied to `.env`
- [ ] `.env` file populated with actual values (remove all `[INSERT_...]` placeholders)
- [ ] Environment variables added to Cloudflare Pages
- [ ] Site redeployed after adding environment variables
- [ ] Videos accessible via direct URL test
- [ ] VideoGrid component added to page
- [ ] Local development test passed
- [ ] Production deployment test passed

### Key Values to Configure

| Placeholder                        | Where to Find It                     | Example                           |
| ---------------------------------- | ------------------------------------ | --------------------------------- |
| `[INSERT_YOUR_R2_BUCKET_URL_HERE]` | R2 bucket → Settings → Public access | `https://pub-abc123def456.r2.dev` |
| `[INSERT_YOUR_ACCOUNT_ID_HERE]`    | Cloudflare → R2 → Overview           | `1234567890abcdef...`             |
| `[INSERT_YOUR_BUCKET_NAME_HERE]`   | R2 bucket name you created           | `my-thesis-videos`                |

---

## Support

If you encounter issues:

1. Check the [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
2. Verify the [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
3. Review the troubleshooting section above
4. Check browser console (F12) for error messages

---

## Next Steps

After setup is complete:

1. ✅ Add VideoGrid to your research sections
2. ✅ Customize video filenames and titles as needed
3. ✅ Optimize videos for web delivery
4. ✅ Test on multiple devices and browsers
5. ✅ Monitor R2 usage in Cloudflare Dashboard

Your VideoGrid should now be fully functional and displaying your research demos beautifully! 🎉
