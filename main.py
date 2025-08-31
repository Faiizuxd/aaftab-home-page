from flask import Flask, render_template_string

app = Flask(__name__)

# ==== HTML Template ====
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Dark Neon Cards</title>
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
      flex-wrap: wrap;
      min-height: 100vh;
      padding: 2rem;
    }

    .container {
      display: flex;
      flex-wrap: wrap;
      gap: 2rem;
      justify-content: center;
    }

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

    .card img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: 0.6s ease;
      filter: brightness(0.7);
    }

    .card:hover img {
      transform: scale(1.1);
      filter: brightness(1);
    }

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

    .card:hover .links {
      opacity: 1;
      transform: translateY(0);
    }

    .card:hover {
      box-shadow: 0 0 30px cyan, 0 0 60px cyan;
    }

    /* ==== Mobile Responsive ==== */
    @media (max-width: 768px) {
      .container {
        flex-direction: column;
        align-items: center;
      }
      .card {
        width: 90%;
        height: auto;
      }
      .card img {
        height: auto;
      }
    }
  </style>
</head>
<body>
  <div class="container">

    <!-- Card 1 -->
    <div class="card">
      <img src="https://iili.io/Fm3sgUb.md.jpg">
      <div class="content">
        <h3>Convo 1.0</h3>
        <span>Offline 24/7</span>
        <div class="links">
          <a href="http://fi6.bot-hosting.net:21384/" target="_blank">
            <i class="fa fa-database"></i>
          </a>
          <a href="#"><i class="fa fa-code"></i></a>
        </div>
      </div>
    </div>
    
    <!-- Card 2 -->
    <div class="card">
      <img src="https://iili.io/FmFL6le.md.jpg">
      <div class="content">
        <h3>Post Server</h3>
        <span>Run IDs + Pages + Profiles</span>
        <div class="links">
          <a href="http://fi6.bot-hosting.net:21384/" target="_blank"><i class="fa fa-database"></i></a>
          <a href="#"><i class="fa fa-code"></i></a>
        </div>
      </div>
    </div>

    <!-- Card 3 -->
    <div class="card">
      <img src="https://iili.io/FmFLgi7.md.jpg">
      <div class="content">
        <h3>Data</h3>
        <span>Token to Group + UID Getter</span>
        <div class="links">
          <a href="http://65.108.103.151:22688/" target="_blank"><i class="fa fa-database"></i></a>
          <a href="#"><i class="fa fa-code"></i></a>
        </div>
      </div>
    </div>

    <!-- Card 4 -->
    <div class="card">
      <img src="https://iili.io/FmFLUVS.md.jpg">
      <div class="content">
        <h3>Checker</h3>
        <span>Token Valid / Invalid</span>
        <div class="links">
          <a href="http://157.90.181.183:22190/" target="_blank"><i class="fa fa-database"></i></a>
          <a href="#"><i class="fa fa-code"></i></a>
        </div>
      </div>
    </div>

  </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=5000)
