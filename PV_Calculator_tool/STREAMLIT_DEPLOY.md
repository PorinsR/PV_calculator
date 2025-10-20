# Deploy PV Calculator to Streamlit Cloud (FREE)

## Quick Start (5 minutes)

### 1. Test Locally

```bash
# Install dependencies
pip install -r requirements_web.txt

# Run the app
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501` 🎉

### 2. Deploy to Streamlit Cloud (FREE)

#### Step 1: Push to GitHub

```bash
git add streamlit_app.py requirements_web.txt
git commit -m "Add Streamlit web app"
git push origin main
```

#### Step 2: Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"New app"**
3. Connect your GitHub account (if not already)
4. Select:
   - **Repository**: `yourusername/PV_calculator`
   - **Branch**: `main`
   - **Main file path**: `PV_Calculator_tool/streamlit_app.py`
5. Click **"Deploy!"**

**That's it!** Your app will be live at:

```
https://yourusername-pv-calculator.streamlit.app
```

### 3. Share Your App

- Get shareable link from Streamlit Cloud dashboard
- Can be accessed by anyone worldwide
- Updates automatically when you push to GitHub
- Free tier includes: unlimited public apps, 1 GB resources

---

## Advanced Configuration (Optional)

### Custom Domain

Create `.streamlit/config.toml`:

```toml
[server]
headless = true
port = 8501

[theme]
primaryColor = "#FF8C00"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Secrets Management

For API keys or sensitive data:

1. Go to Streamlit Cloud app settings
2. Click "Secrets"
3. Add key-value pairs:

```toml
[api]
key = "your-secret-key"
```

Access in code:

```python
api_key = st.secrets["api"]["key"]
```

---

## File Structure for Deployment

```
PV_calculator/
├── PV_Calculator_tool/
│   ├── streamlit_app.py          ← Main app file
│   ├── requirements_web.txt      ← Dependencies
│   ├── PV_calculator.py          ← Your existing modules
│   ├── PV_consumption_generator.py
│   ├── PV_solar_generator.py
│   ├── PV_battery_flow.py
│   └── ... (all other modules)
└── README.md
```

**Important**: Streamlit needs all imported modules in the same directory or as packages.

---

## Troubleshooting

### Issue: "Module not found"

**Solution**: Ensure `requirements_web.txt` includes all dependencies:

```bash
pip freeze > requirements_web.txt
```

### Issue: App crashes on startup

**Solution**: Check logs in Streamlit Cloud dashboard → View Logs

### Issue: Slow performance

**Solutions**:

- Add `@st.cache_data` decorator to expensive functions
- Use `st.session_state` to persist data between reruns
- Consider upgrading to Streamlit Cloud paid tier

Example caching:

```python
@st.cache_data
def calculate_scenarios(pv_size, battery_size):
    # Expensive calculation here
    return results
```

---

## Comparison: Streamlit Cloud vs Other Options

| Platform            | Cost      | Setup Time | Performance | Custom Domain |
| ------------------- | --------- | ---------- | ----------- | ------------- |
| **Streamlit Cloud** | Free      | 2 min      | Good        | Yes (paid)    |
| Heroku              | $7+/mo    | 15 min     | Good        | Yes           |
| AWS/Azure           | $5+/mo    | 30+ min    | Excellent   | Yes           |
| PythonAnywhere      | Free/Paid | 10 min     | Medium      | Yes (paid)    |
| Render              | Free      | 10 min     | Good        | Yes           |

**Winner for quick deployment**: Streamlit Cloud ✅

---

## Updating Your App

After making changes to your code:

```bash
git add .
git commit -m "Update calculations"
git push origin main
```

Streamlit Cloud automatically redeploys within 1-2 minutes! 🚀

---

## Monitoring & Analytics

### Built-in Analytics

Streamlit Cloud provides:

- Number of viewers
- App uptime
- Resource usage
- Error logs

### Add Google Analytics

Add to `streamlit_app.py`:

```python
import streamlit.components.v1 as components

# Google Analytics
ga_code = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
"""

components.html(ga_code, height=0)
```

---

## Next Steps

1. ✅ **Test locally**: `streamlit run streamlit_app.py`
2. ✅ **Deploy to Streamlit Cloud**: 2-minute setup
3. 📈 **Monitor usage**: Check analytics dashboard
4. 🎨 **Customize**: Adjust theme, add features
5. 📣 **Share**: Post link on social media, forums

**Your calculator will be live and accessible worldwide in minutes!** 🌍

Need help? Check:

- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Community Forum](https://discuss.streamlit.io)
- [Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud)
