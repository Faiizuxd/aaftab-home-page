from flask import Flask, render_template_string

app = Flask(__name__)

# ==== HTML Template ====
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
      width: 100%;
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
      object-fit: contain;
      background-color: #000;
      transition: 0.6s ease;
      filter: brightness(0.9);
    }

    /* Hover Effect: Zoom + Glow */
    .card:hover img {
      transform: scale(1.03);
      filter: brightness(1);
    }

    /* Neon Border Glow */
    .card:hover {
      box-shadow: 0 0 12px cyan, 0 0 25px cyan;
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
      text-decoration: none;
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

    /* Mobile Responsive Styles */
    @media (max-width: 768px) {
      body {
        padding: 1rem;
      }
      
      header h1 {
        font-size: 2rem;
      }
      
      .container {
        gap: 1.5rem;
      }
      
      .card {
        width: 100%;
        max-width: 320px;
        height: 380px;
      }
      
      .card .content {
        padding: 15px;
      }
      
      .card h3 {
        font-size: 18px;
      }
      
      .card span {
        font-size: 12px;
      }
      
      .connection-status i {
        font-size: 3.5rem;
      }
      
      .connection-status h2 {
        font-size: 1.5rem;
      }
      
      .connection-status p {
        font-size: 1rem;
      }
    }

    @media (max-width: 480px) {
      header {
        margin-bottom: 1.5rem;
      }
      
      header h1 {
        font-size: 1.8rem;
      }
      
      .card {
        height: 350px;
      }
      
      .card .content {
        padding: 12px;
      }
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

    <!-- Example Card -->
    <div class="card">
      <img src="https://iili.io/KfAeRgR.md.jpg">
      <div class="content">
        <h3>Admin</h3>
        <span>Hi Gyz I'm Diisco The Creator...</span>
        <div class="links">
          <a href="https://fi6.bot-hosting.net:21384/"><i class="fa fa-database"></i></a>
          <a href="#"><i class="fa fa-code"></i></a>
        </div>
      </div>
    </div>

    <!-- Aapke baaki cards yaha... -->
    
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

    // Additional check every 5 seconds
    setInterval(checkConnection, 5000);


    // === Custom Code for Links (Same tab + hide href) ===
    document.querySelectorAll(".card .links a").forEach(link => {
      link.addEventListener("click", function(e) {
        e.preventDefault(); // stop default href preview
        let url = this.getAttribute("href");
        if (url && url !== "#") {
          window.location.href = url; // open in same tab
        }
      });
    });
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
