from flask import Flask, render_template_string

app = Flask(__name__)

# ==== HTML Template ====
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Diisco Home</title>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">

  <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: "Montserrat", sans-serif;
    }

    body {
      background: #0a0a0f;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
      flex-wrap: wrap;
      min-height: 100vh;
      padding: 2rem;
      color: #fff;
      transition: filter 0.5s ease;
    }

    /* Internet status indicator */
    .connection-status {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: #000;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
      z-index: 1000;
      transition: opacity 0.5s ease, visibility 0.5s ease;
      opacity: 0;
      visibility: hidden;
    }

    .connection-status.active {
      opacity: 1;
      visibility: visible;
    }

    .connection-status i {
      font-size: 5rem;
      color: #ff3333;
      margin-bottom: 1.5rem;
    }

    .connection-status h2 {
      font-size: 2rem;
      color: #fff;
      margin-bottom: 1rem;
      text-align: center;
    }

    .connection-status p {
      font-size: 1.2rem;
      color: #ccc;
      text-align: center;
      max-width: 80%;
    }

    /* 🔥 Logo Section */
    header {
      text-align: center;
      margin-bottom: 2rem;
    }

    header h1 {
      font-size: 2.5rem;
      font-weight: 700;
      color: cyan;
      text-shadow: 0 0 15px cyan, 0 0 30px cyan;
    }

    .container {
      display: flex;
      flex-wrap: wrap;
      gap: 2rem;
      justify-content: center;
    }

    /* 🔥 Card */
    .card {
      position: relative;
      width: 300px;
      height: 420px;
      overflow: hidden;
      border-radius: 18px;
      box-shadow: 0 0 25px rgba(0, 255, 255, 0.2);
      transition: all 0.4s ease-in-out;
      cursor: pointer;
      background: #111;
    }

    /* ✅ Image Full Show (No Crop) */
    .card img {
      width: 100%;
      height: 100%;
      object-fit: contain;   /* image poori dikhayega */
      background-color: #000; /* black background if empty */
      transition: 0.6s ease;
      filter: brightness(0.9);
    }

    /* Hover Effect: Zoom + Glow */
    .card:hover img {
      transform: scale(1.03);  /* thoda hi zoom kare */
      filter: brightness(1);
    }

    /* Neon Border Glow */
    .card:hover {
      box-shadow: 0 0 12px cyan, 0 0 25px cyan; /* ab soft glow hai */
    }

    /* Overlay Content */
    .card .content {
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      padding: 20px;
      background: linear-gradient(to top, rgba(0,0,0,0.9), rgba(0,0,0,0));
      color: #fff;
      transition: 0.4s ease;
    }

    .card h3 {
      font-size: 20px;
      font-weight: 600;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }

    .card span {
      font-size: 13px;
      font-weight: 400;
      opacity: 0.85;
    }

    /* Hidden Icons + Links */
    .card .links {
      margin-top: 12px;
      display: flex;
      gap: 15px;
      opacity: 0;
      transform: translateY(20px);
      transition: 0.4s ease;
    }

    .card .links a {
      color: cyan;
      font-size: 20px;
      text-shadow: 0 0 10px cyan, 0 0 20px cyan;
      transition: 0.3s;
    }

    .card .links a:hover {
      color: #fff;
      text-shadow: 0 0 15px #0ff, 0 0 30px #0ff;
    }

    /* Hover = show links */
    .card:hover .links {
      opacity: 1;
      transform: translateY(0);
    }

    /* Neon Border Glow */
    .card:hover {
      box-shadow: 0 0 30px cyan, 0 0 60px cyan;
    }
  </style>
</head>
<body>
  
  <!-- Internet Connection Status Indicator -->
  <div class="connection-status" id="connectionStatus">
    <i class="fa fa-wifi"></i>
    <h2>Internet Connection Lost</h2>
    <p>Please check your internet connection and try again.</p>
  </div>

  <!-- 🔥 Logo -->
  <header>
    <h1>Diisco</h1>
  </header>

  <div class="container">

    <!-- Card 1 -->
    <div class="card">
      <img src="https://iili.io/KfAeRgR.md.jpg">
      <div class="content">
        <h3>Admin</h3>
        <span>Hi Gyz I'm Diisco The Creator Off This Apk "/3 Don't Depand On This apk Made By Bot Hosting '/3 But Nonstop [ Aura ].</span>
        <div class="links">
          <a href="https://fi6.bot-hosting.net:21384/" target="_blank"><i class="fa fa-database"></i></a>
          <a href="#"><i class="fa fa-code"></i></a>
        </div>
      </div>
    </div>
    
    <!-- Card 2 -->
    <div class="card">
      <img src="https://iili.io/KfAe7Jp.md.jpg">
      <div class="content">
        <h3>Convo 2.0</h3>
        <span>Offline Server</span>
        <div class="links">
          <a href="https://fi6.bot-hosting.net:21384/" target="_blank"><i class="fa fa-database"></i></a>
          <a href="#"><i class="fa fa-code"></i></a>
        </div>
      </div>
    </div>

    <!-- Card 3 -->
    <div class="card">
      <img src="https://iili.io/KfAeweS.md.jpg">
      <div class="content">
        <h3>Post Server</h3>
        <span>Run IDs + Pages + Profiles</span>
        <div class="links">
          <a href="https://fi6.bot-hosting.net:21384/" target="_blank"><i class="fa fa-database"></i></a>
          <a href="#"><i class="fa fa-code"></i></a>
        </div>
      </div>
    </div>

     <!-- Card 4 -->
    <div class="card">
      <img src="https://iili.io/KfAr8u4.md.jpg">
      <div class="content">
        <h3>Post Uid</h3>
        <span>Post Uid Finder By Link </span>
        <div class="links">
          <a href="https://fi6.bot-hosting.net:21384/" target="_blank"><i class="fa fa-database"></i></a>
          <a href="#"><i class="fa fa-code"></i></a>
        </div>
      </div>
    </div>

    <!-- Card 5 -->
    <div class="card">
      <img src="https://iili.io/KfAeEss.md.jpg">
      <div class="content">
        <h3>Data</h3>
        <span>Token to Group + UID Getter</span>
        <div class="links">
          <a href="https://fi6.bot-hosting.net:21384/" target="_blank"><i class="fa fa-database"></i></a>
          <a href="#"><i class="fa fa-code"></i></a>
        </div>
      </div>
    </div>

    <!-- Card 6 -->
    <div class="card">
      <img src="https://iili.io/KfAr6P9.md.jpg">
      <div class="content">
        <h3>Checker</h3>
        <span>Token Valid / Invalid</span>
        <div class="links">
          <a href="https://fi6.bot-hosting.net:21384/" target="_blank"><i class="fa fa-database"></i></a>
          <a href="#"><i class="fa fa-code"></i></a>
        </div>
      </div>
    </div>

  </div>

  <script>
    // Check internet connection status
    function checkConnection() {
      const statusElement = document.getElementById('connectionStatus');
      
      if (!navigator.onLine) {
        statusElement.classList.add('active');
      } else {
        statusElement.classList.remove('active');
      }
    }

    // Initial check
    checkConnection();

    // Listen for connection status changes
    window.addEventListener('online', function() {
      document.getElementById('connectionStatus').classList.remove('active');
    });

    window.addEventListener('offline', function() {
      document.getElementById('connectionStatus').classList.add('active');
    });

    // Additional check every 5 seconds to catch some edge cases
    setInterval(checkConnection, 5000);
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=5000)
