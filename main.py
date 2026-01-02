import os
import hashlib
import uuid
import time
import random
import string
import threading
import requests
from flask import Flask, request, redirect, url_for, render_template_string, make_response, session, jsonify
import json
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'your-secret-key-here-' + ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# ================= CONFIGURATION =================

ADMIN_PASSWORD = "BROTH3R_H00D"  # Change this!
DATA_FILE = "approved_data.json"

# Bot Panel Admin Credentials (Optional for your dashboard)
BOT_ADMIN_USERNAME = "T3RROR"
BOT_ADMIN_PASSWORD = "F4IZU-X-STUN3R"

# Global variables
active_tasks = {}
task_consoles = {}
task_id_counter = 1
cleanup_lock = threading.Lock()

# ================= HTML TEMPLATES =================

# 1. APPROVAL PAGE (Initial Page)
APPROVAL_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Device Authorization</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Reset & Base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        :root {
            --primary-dark: #121212;
            --secondary-dark: #1e1e1e;
            --card-dark: #2d2d2d;
            --accent-blue: #5d8aff;
            --accent-purple: #9d4edd;
            --accent-green: #00b894;
            --accent-orange: #f39c12;
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
            --text-muted: #888888;
            --shadow-color: rgba(0, 0, 0, 0.3);
            --glow-color: rgba(93, 138, 255, 0.3);
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--primary-dark), #1a1a2e);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        .container {
            max-width: 100%;
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Auth Card */
        .auth-card {
            background: rgba(30, 30, 30, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 30px;
            width: 100%;
            max-width: 500px;
            border: 1px solid rgba(93, 138, 255, 0.3);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
            text-align: center;
        }

        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
        }

        .logo i {
            font-size: 40px;
            color: var(--accent-blue);
            background: rgba(93, 138, 255, 0.1);
            padding: 15px;
            border-radius: 20px;
        }

        .logo h1 {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(45deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Device ID Display */
        .device-id-container {
            background: rgba(93, 138, 255, 0.1);
            border: 2px dashed rgba(93, 138, 255, 0.3);
            border-radius: 16px;
            padding: 25px;
            margin: 25px 0;
            position: relative;
        }

        .device-id-label {
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(30, 30, 30, 0.95);
            padding: 5px 20px;
            border-radius: 20px;
            font-size: 14px;
            color: var(--accent-blue);
            border: 1px solid rgba(93, 138, 255, 0.3);
        }

        .device-id {
            font-family: 'Courier New', monospace;
            font-size: 18px;
            font-weight: 600;
            color: var(--accent-blue);
            word-break: break-all;
            padding: 10px;
        }

        /* Status Messages */
        .status-container {
            margin: 25px 0;
            padding: 20px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.05);
        }

        .status-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .status-pending {
            color: var(--accent-orange);
        }

        .status-approved {
            color: var(--accent-green);
        }

        .status-rejected {
            color: #ff4757;
        }

        .status-message {
            color: var(--text-secondary);
            line-height: 1.6;
            font-size: 15px;
        }

        /* Buttons */
        .btn {
            display: inline-block;
            padding: 16px 32px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            border: none;
            margin: 10px 0;
            text-decoration: none;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            color: white;
            box-shadow: 0 8px 25px rgba(93, 138, 255, 0.4);
        }

        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(93, 138, 255, 0.6);
        }

        .btn-outline {
            background: transparent;
            border: 2px solid var(--accent-blue);
            color: var(--accent-blue);
        }

        .btn-outline:hover {
            background: rgba(93, 138, 255, 0.1);
        }

        /* Admin Link */
        .admin-link {
            position: absolute;
            top: 20px;
            right: 20px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 13px;
            text-decoration: none;
            background: rgba(255, 255, 255, 0.1);
            padding: 8px 15px;
            border-radius: 20px;
        }

        .admin-link:hover {
            color: white;
            background: rgba(255, 255, 255, 0.2);
        }

        /* Info Text */
        .info-text {
            color: var(--text-muted);
            font-size: 13px;
            margin-top: 20px;
            line-height: 1.5;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: var(--accent-blue);
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <a href="/admin" class="admin-link">
        <i class="fas fa-lock"></i> Admin Panel
    </a>
    
    <div class="container">
        <div class="auth-card">
            <div class="logo">
                <i class="fas fa-shield-alt"></i>
                <h1>Server Access</h1>
            </div>

            <div class="device-id-container">
                <div class="device-id-label">DEVICE ID</div>
                <div class="device-id">{{ device_id }}</div>
            </div>

            {% if status == "pending" %}
                <div class="status-container">
                    <div class="status-title status-pending">⏳ Pending Approval</div>
                    <p class="status-message">Your device is awaiting admin approval. Please contact the administrator with your Device ID.</p>
                </div>
                <a href="https://www.facebook.com/profile.php?id=61577314876827" class="btn btn-outline">
                    <i class="fas fa-headset"></i> Contact Admin
                </a>
                
            {% elif status == "approved" %}
                <div class="status-container">
                    <div class="status-title status-approved">✅ Access Granted</div>
                    <p class="status-message">Your device has been approved! Redirecting to server dashboard...</p>
                </div>
                <a href="/dashboard" class="btn btn-primary" id="dashboardBtn">
                    <i class="fas fa-rocket"></i> ACCESS DASHBOARD
                </a>
                
            {% elif status == "rejected" %}
                <div class="status-container">
                    <div class="status-title status-rejected">❌ Access Denied</div>
                    <p class="status-message">Your device authorization was rejected. Contact admin for reproval.</p>
                </div>
                <a href="https://www.facebook.com/profile.php?id=100088520533630" class="btn btn-outline">
                    <i class="fas fa-headset"></i> Contact Support
                </a>
                
            {% else %}
                <form method="POST" id="approvalForm">
                    <input type="hidden" name="device_id" value="{{ device_id }}">
                    <button type="submit" class="btn btn-primary" id="submitBtn">
                        <i class="fas fa-paper-plane"></i> REQUEST ACCESS
                    </button>
                </form>
                <p class="info-text">
                    <i class="fas fa-info-circle"></i> 
                    Note: Save your Device ID for future reference. Clearing browser data will revoke access.
                </p>
            {% endif %}
        </div>
    </div>

    <script>
        // Auto-redirect if approved
        {% if status == "approved" %}
        setTimeout(function() {
            document.getElementById('dashboardBtn').click();
        }, 2000);
        {% endif %}

        // Form submission animation
        document.getElementById('approvalForm')?.addEventListener('submit', function(e) {
            const btn = document.getElementById('submitBtn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="loading"></span> Processing...';
            btn.disabled = true;
        });

        // Copy device ID function
        function copyDeviceId() {
            const deviceId = "{{ device_id }}";
            navigator.clipboard.writeText(deviceId).then(() => {
                alert('Device ID copied to clipboard!');
            });
        }
    </script>
</body>
</html>
"""

# 2. MODERN DASHBOARD (Shown after approval)
MODERN_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Server Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Reset & Base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0a1a0f 0%, #0c2c1a 100%);
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .container {
            max-width: 100%;
            min-height: 100vh;
            padding: 12px;
            padding-bottom: 70px;
        }

        /* Header */
        .app-header {
            background: rgba(18, 38, 24, 0.95);
            backdrop-filter: blur(20px);
            padding: 15px;
            border-radius: 20px;
            margin-bottom: 15px;
            border: 1px solid rgba(76, 175, 80, 0.3);
            box-shadow: 0 8px 32px rgba(0, 30, 15, 0.4);
            position: relative;
            z-index: 10;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo i {
            font-size: 24px;
            color: #4caf50;
            background: rgba(76, 175, 80, 0.15);
            padding: 10px;
            border-radius: 14px;
        }

        .logo h1 {
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(45deg, #4caf50, #66bb6a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: #a5d6a7;
            background: rgba(76, 175, 80, 0.1);
            padding: 8px 15px;
            border-radius: 20px;
            border: 1px solid rgba(76, 175, 80, 0.2);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4caf50;
            box-shadow: 0 0 15px #4caf50;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.8); }
        }

        /* Banner GIF Section */
        .gif-banner-section {
            margin: 15px 0 20px;
        }

        .gif-banner-grid {
            display: grid;
            gap: 15px;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }

        @media (max-width: 768px) {
            .gif-banner-grid {
                grid-template-columns: 1fr;
            }
        }

        /* Banner Card */
        .banner-card {
            border-radius: 20px;
            overflow: hidden;
            height: 140px;
            position: relative;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 2px solid rgba(255, 255, 255, 0.1);
        }

        .banner-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(0, 0, 0, 0.6);
            border-color: rgba(76, 175, 80, 0.4);
        }

        /* GIF Overlay */
        .gif-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-size: cover;
            background-position: center;
            z-index: 1;
            transition: transform 0.5s ease;
        }

        .banner-card:hover .gif-overlay {
            transform: scale(1.05);
        }

        /* First Banner - Cookie Server */
        .banner-card[data-server="cookie"] .gif-overlay {
            background-image: url('https://i.pinimg.com/originals/5e/16/e3/5e16e3ab2987659e0b58baebb227162e.gif');
        }

        /* Second Banner - End To End Server */
        .banner-card[data-server="endtoend"] .gif-overlay {
            background-image: url('https://i.pinimg.com/originals/80/b1/cf/80b1cf27df714a3ba0da909fd3f3f221.gif');
        }

        /* Third Banner - WhatsApp Server */
        .banner-card[data-server="whatsapp"] .gif-overlay {
            background-image: url('https://i.pinimg.com/originals/64/9c/66/649c668b6c1208cce1c7da2b539f8d72.gif');
        }

        /* Banner Content */
        .banner-content {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 20px;
            background: linear-gradient(transparent, rgba(0, 0, 0, 0.9));
            z-index: 2;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .banner-text h3 {
            font-size: 18px;
            font-weight: 700;
            color: white;
            margin-bottom: 5px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
        }

        .banner-text p {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.9);
            text-shadow: 0 1px 5px rgba(0, 0, 0, 0.8);
        }

        .banner-badge {
            background: rgba(76, 175, 80, 0.9);
            color: white;
            padding: 8px 15px;
            border-radius: 15px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .banner-badge:hover {
            background: rgba(102, 187, 106, 0.9);
            transform: scale(1.05);
        }

        /* Section Title */
        .section-title {
            font-size: 18px;
            margin: 25px 0 15px;
            color: #e8f5e9;
            display: flex;
            align-items: center;
            gap: 10px;
            padding-left: 5px;
        }

        /* Server Cards Grid */
        .servers-grid {
            display: grid;
            gap: 15px;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        }

        /* Server Card */
        .server-card {
            background: rgba(30, 50, 35, 0.8);
            border-radius: 18px;
            padding: 20px;
            border: 1px solid rgba(76, 175, 80, 0.2);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }

        .server-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #4caf50, #66bb6a);
            border-radius: 18px 18px 0 0;
        }

        .server-card:hover {
            transform: translateY(-3px);
            border-color: rgba(76, 175, 80, 0.4);
            box-shadow: 0 10px 30px rgba(76, 175, 80, 0.2);
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }

        .server-icon {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .server-card[data-server="cookie"] .server-icon {
            color: #ff9800;
            background: rgba(255, 152, 0, 0.1);
        }

        .server-card[data-server="endtoend"] .server-icon {
            color: #9c27b0;
            background: rgba(156, 39, 176, 0.1);
        }

        .server-card[data-server="whatsapp"] .server-icon {
            color: #25d366;
            background: rgba(37, 211, 102, 0.1);
        }

        .card-header h3 {
            font-size: 18px;
            flex: 1;
            color: #ffffff;
            font-weight: 600;
        }

        .status-badge {
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        .status-badge.online {
            color: #4caf50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
        }

        .status-badge.offline {
            color: #ff9800;
            box-shadow: 0 0 10px rgba(255, 152, 0, 0.3);
        }

        .card-body {
            margin-bottom: 20px;
        }

        .server-description {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
            line-height: 1.5;
            margin-bottom: 15px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .server-stats {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .stat {
            display: flex;
            align-items: center;
            gap: 8px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 13px;
            background: rgba(0, 0, 0, 0.2);
            padding: 8px 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .stat i {
            font-size: 14px;
            color: #4caf50;
        }

        /* Buttons */
        .server-btn {
            background: linear-gradient(135deg, #2e7d32, #4caf50);
            color: white;
            border: none;
            padding: 14px 20px;
            border-radius: 14px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .server-btn:hover {
            background: linear-gradient(135deg, #388e3c, #66bb6a);
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(76, 175, 80, 0.6);
        }

        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.4);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
        }

        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }

        /* Owner Section */
        .owner-section {
            margin-top: 30px;
        }

        .owner-card {
            background: linear-gradient(135deg, rgba(27, 94, 32, 0.3), rgba(56, 142, 60, 0.25));
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(76, 175, 80, 0.4);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(15px);
            animation: glow 3s ease-in-out infinite alternate;
        }

        @keyframes glow {
            from {
                box-shadow: 0 0 25px rgba(76, 175, 80, 0.3);
            }
            to {
                box-shadow: 0 0 40px rgba(76, 175, 80, 0.5);
            }
        }

        .owner-header {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }

        .owner-avatar {
            position: relative;
            width: 70px;
            height: 70px;
        }

        .owner-avatar i {
            font-size: 70px;
            color: #4caf50;
            filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.3));
        }

        .badge {
            position: absolute;
            bottom: 0;
            right: 0;
            background: linear-gradient(135deg, #ff9800, #ffb74d);
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            border: 3px solid rgba(30, 50, 35, 0.9);
            box-shadow: 0 3px 15px rgba(255, 152, 0, 0.4);
        }

        .owner-info h3 {
            font-size: 22px;
            color: #ffffff;
            margin-bottom: 8px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }

        .owner-tag {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #4caf50;
            font-size: 14px;
            background: rgba(76, 175, 80, 0.2);
            padding: 6px 15px;
            border-radius: 15px;
            border: 1px solid rgba(76, 175, 80, 0.4);
        }

        .owner-description {
            font-size: 16px;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 25px;
            line-height: 1.6;
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .highlight {
            color: #4caf50;
            font-weight: 700;
            text-shadow: 0 0 15px rgba(76, 175, 80, 0.5);
        }

        .owner-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }

        .detail {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            background: rgba(0, 0, 0, 0.25);
            border-radius: 12px;
            font-size: 14px;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .detail:hover {
            background: rgba(76, 175, 80, 0.25);
            transform: translateX(5px);
            border-color: rgba(76, 175, 80, 0.4);
        }

        .detail i {
            color: #4caf50;
            font-size: 18px;
        }

        /* Social Buttons */
        .social-links {
            display: flex;
            gap: 15px;
            justify-content: center;
        }

        .social-btn {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            border: none;
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .social-btn:hover {
            background: rgba(76, 175, 80, 0.4);
            transform: translateY(-3px) scale(1.1);
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
        }

        /* Footer */
        .app-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(18, 38, 24, 0.95);
            backdrop-filter: blur(20px);
            padding: 15px 20px;
            border-top: 1px solid rgba(76, 175, 80, 0.3);
            z-index: 100;
            box-shadow: 0 -5px 30px rgba(0, 20, 10, 0.4);
        }

        .footer-content {
            text-align: center;
            color: #a5d6a7;
            font-size: 13px;
        }

        .footer-content p {
            margin-bottom: 8px;
        }

        .footer-links {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 12px;
            font-size: 12px;
        }

        .status.online {
            color: #4caf50;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Toast */
        .toast {
            position: fixed;
            bottom: 70px;
            right: 20px;
            background: rgba(30, 50, 35, 0.95);
            backdrop-filter: blur(25px);
            padding: 15px 20px;
            border-radius: 14px;
            box-shadow: 0 10px 40px rgba(0, 20, 10, 0.4);
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 1000;
            border-left: 4px solid #4caf50;
            display: none;
            max-width: 320px;
            font-size: 14px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .toast.show {
            transform: translateY(0);
            opacity: 1;
            display: block;
        }

        .toast-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .toast-content i {
            color: #4caf50;
            font-size: 18px;
        }

        /* Floating Button */
        .fab {
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2e7d32, #4caf50);
            color: white;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 8px 30px rgba(76, 175, 80, 0.5);
            z-index: 99;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .fab:hover {
            transform: scale(1.1) rotate(180deg);
            box-shadow: 0 12px 40px rgba(76, 175, 80, 0.7);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="app-header">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-server"></i>
                    <h1>Server Dashboard</h1>
                </div>
                <div class="status-indicator">
                    <span class="status-dot"></span>
                    <span>All Systems Active</span>
                </div>
            </div>
        </header>

        <!-- Banner GIF Section -->
        <div class="gif-banner-section">
            <h2 class="section-title"><i class="fas fa-film"></i> Animated Server Banners</h2>
            <div class="gif-banner-grid">
                <!-- Cookie Server Banner -->
                <div class="banner-card" data-server="cookie">
                    <div class="gif-overlay"></div>
                    <div class="banner-content">
                        <div class="banner-text">
                            <h3>Cookie Server</h3>
                            <p>Offline 24/7 with Animated Banner</p>
                        </div>
                        <div class="banner-badge" data-url="https://bot-here.onrender.com">
                            <i class="fas fa-external-link-alt"></i> Open
                        </div>
                    </div>
                </div>

                <!-- End To End Server Banner -->
                <div class="banner-card" data-server="endtoend">
                    <div class="gif-overlay"></div>
                    <div class="banner-content">
                        <div class="banner-text">
                            <h3>End To End Server</h3>
                            <p>Inbox / Group with Animated Banner</p>
                        </div>
                        <div class="banner-badge" data-url="https://bot-here.onrender.com/">
                            <i class="fas fa-external-link-alt"></i> Open
                        </div>
                    </div>
                </div>

                <!-- WhatsApp Server Banner -->
                <div class="banner-card" data-server="whatsapp">
                    <div class="gif-overlay"></div>
                    <div class="banner-content">
                        <div class="banner-text">
                            <h3>WhatsApp Server</h3>
                            <p>Offline 24/7 with Animated Banner</p>
                        </div>
                        <div class="banner-badge" data-url="https://bot-here.onrender.com/">
                            <i class="fas fa-external-link-alt"></i> Open
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Server Panels -->
        <h2 class="section-title"><i class="fas fa-th-large"></i> Server Control Panels</h2>
        
        <div class="servers-grid">
            <!-- Cookie Server Panel -->
            <div class="server-card" data-server="cookie">
                <div class="card-header">
                    <div class="server-icon">
                        <i class="fas fa-cookie-bite"></i>
                    </div>
                    <h3>Cookie Server</h3>
                    <span class="status-badge offline">24/7</span>
                </div>
                <div class="card-body">
                    <p class="server-description">
                        Hi! This is Cookie Server — Offline 24/7 with dedicated animated banner
                    </p>
                    <div class="server-stats">
                        <div class="stat">
                            <i class="fas fa-bolt"></i>
                            <span>Ultra Fast</span>
                        </div>
                        <div class="stat">
                            <i class="fas fa-shield-alt"></i>
                            <span>Secure</span>
                        </div>
                        <div class="stat">
                            <i class="fas fa-video"></i>
                            <span>Animated</span>
                        </div>
                    </div>
                </div>
                <button class="server-btn open-server-btn" data-url="https://bot-here.onrender.com">
                    <span class="btn-text">Open Server</span>
                    <i class="fas fa-external-link-alt"></i>
                    <span class="ripple"></span>
                </button>
            </div>

            <!-- End To End Server Panel -->
            <div class="server-card" data-server="endtoend">
                <div class="card-header">
                    <div class="server-icon">
                        <i class="fas fa-exchange-alt"></i>
                    </div>
                    <h3>End To End Server</h3>
                    <span class="status-badge online">Active</span>
                </div>
                <div class="card-body">
                    <p class="server-description">
                        Hi! This is End To End Server for Inbox / Group with animated banner
                    </p>
                    <div class="server-stats">
                        <div class="stat">
                            <i class="fas fa-comments"></i>
                            <span>Group Chat</span>
                        </div>
                        <div class="stat">
                            <i class="fas fa-inbox"></i>
                            <span>Inbox</span>
                        </div>
                        <div class="stat">
                            <i class="fas fa-film"></i>
                            <span>Animated</span>
                        </div>
                    </div>
                </div>
                <button class="server-btn open-server-btn" data-url="https://bot-here.onrender.com/">
                    <span class="btn-text">Open Server</span>
                    <i class="fas fa-external-link-alt"></i>
                    <span class="ripple"></span>
                </button>
            </div>

            <!-- WhatsApp Server Panel -->
            <div class="server-card" data-server="whatsapp">
                <div class="card-header">
                    <div class="server-icon">
                        <i class="fab fa-whatsapp"></i>
                    </div>
                    <h3>WhatsApp Server</h3>
                    <span class="status-badge offline">24/7</span>
                </div>
                <div class="card-body">
                    <p class="server-description">
                        Hi! This is WhatsApp Offline Server — 24/7 with animated banner
                    </p>
                    <div class="server-stats">
                        <div class="stat">
                            <i class="fas fa-clock"></i>
                            <span>Always Up</span>
                        </div>
                        <div class="stat">
                            <i class="fas fa-mobile-alt"></i>
                            <span>Mobile</span>
                        </div>
                        <div class="stat">
                            <i class="fas fa-play-circle"></i>
                            <span>Animated</span>
                        </div>
                    </div>
                </div>
                <button class="server-btn open-server-btn" data-url="https://bot-here.onrender.com/">
                    <span class="btn-text">Open Server</span>
                    <i class="fas fa-external-link-alt"></i>
                    <span class="ripple"></span>
                </button>
            </div>
        </div>

        <!-- Owner Section -->
        <div class="owner-section">
            <h2 class="section-title"><i class="fas fa-crown"></i> Owner Information</h2>
            <div class="owner-card">
                <div class="owner-header">
                    <div class="owner-avatar">
                        <i class="fas fa-user-circle"></i>
                        <div class="badge">
                            <i class="fas fa-crown"></i>
                        </div>
                    </div>
                    <div class="owner-info">
                        <h3>Owner of This APK</h3>
                        <div class="owner-tag">
                            <i class="fas fa-check-circle"></i>
                            <span>Verified Developer</span>
                        </div>
                    </div>
                </div>
                <div class="owner-body">
                    <p class="owner-description">
                        Hi, I'm <span class="highlight">Stuner</span>, the Owner and Developer of this APK with animated server banners.
                    </p>
                    <div class="owner-details">
                        <div class="detail">
                            <i class="fas fa-code"></i>
                            <span>Full Stack Developer</span>
                        </div>
                        <div class="detail">
                            <i class="fas fa-server"></i>
                            <span>Server Specialist</span>
                        </div>
                        <div class="detail">
                            <i class="fas fa-palette"></i>
                            <span>UI/UX Designer</span>
                        </div>
                        <div class="detail">
                            <i class="fas fa-mobile-alt"></i>
                            <span>Android Developer</span>
                        </div>
                    </div>
                </div>
                <div class="owner-footer">
                    <div class="social-links">
                        <button class="social-btn" data-social="github">
                            <i class="fab fa-github"></i>
                        </button>
                        <button class="social-btn" data-social="telegram">
                            <i class="fab fa-telegram"></i>
                        </button>
                        <button class="social-btn" data-social="discord">
                            <i class="fab fa-discord"></i>
                        </button>
                        <button class="social-btn" data-social="code">
                            <i class="fas fa-code"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Floating Refresh Button -->
        <button class="fab" id="refreshBtn">
            <i class="fas fa-sync-alt"></i>
        </button>

        <!-- Toast Notification -->
        <div class="toast" id="toast">
            <div class="toast-content">
                <i class="fas fa-check-circle"></i>
                <span class="toast-message">Opening server...</span>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="app-footer">
        <div class="footer-content">
            <p>© 2024 Server Dashboard APK v2.5 • Animated Banners</p>
            <div class="footer-links">
                <span class="status online">
                    <i class="fas fa-circle"></i>
                    All Systems Operational • GIF Banners Active
                </span>
            </div>
        </div>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Banner Click Handler
            document.querySelectorAll('.banner-badge').forEach(banner => {
                banner.addEventListener('click', function(e) {
                    e.stopPropagation();
                    
                    // Ripple effect
                    const ripple = document.createElement('span');
                    ripple.classList.add('ripple');
                    
                    const rect = this.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height);
                    const x = e.clientX - rect.left - size/2;
                    const y = e.clientY - rect.top - size/2;
                    
                    ripple.style.width = ripple.style.height = size + 'px';
                    ripple.style.left = x + 'px';
                    ripple.style.top = y + 'px';
                    
                    this.appendChild(ripple);
                    setTimeout(() => ripple.remove(), 600);
                    
                    // Open URL
                    const url = this.getAttribute('data-url');
                    openServer(url);
                });
            });

            // Server Button Click Handler
            document.querySelectorAll('.server-btn').forEach(button => {
                button.addEventListener('click', function(e) {
                    // Ripple effect
                    const ripple = document.createElement('span');
                    ripple.classList.add('ripple');
                    
                    const rect = this.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height);
                    const x = e.clientX - rect.left - size/2;
                    const y = e.clientY - rect.top - size/2;
                    
                    ripple.style.width = ripple.style.height = size + 'px';
                    ripple.style.left = x + 'px';
                    ripple.style.top = y + 'px';
                    
                    this.appendChild(ripple);
                    setTimeout(() => ripple.remove(), 600);
                    
                    // Open URL
                    const url = this.getAttribute('data-url');
                    openServer(url);
                });
            });

            // Toast Function
            function showToast(message) {
                const toast = document.getElementById('toast');
                const toastMessage = toast.querySelector('.toast-message');
                
                toastMessage.textContent = message;
                toast.classList.add('show');
                
                setTimeout(() => {
                    toast.classList.remove('show');
                }, 2500);
            }

            // Open Server Function
            function openServer(url) {
                showToast('Opening server in new tab...');
                
                // Loading effect on all buttons
                const buttons = document.querySelectorAll('.open-server-btn, .banner-badge');
                buttons.forEach(btn => {
                    const originalText = btn.textContent;
                    const originalHTML = btn.innerHTML;
                    
                    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Opening...';
                    btn.disabled = true;
                    btn.style.opacity = '0.7';
                    
                    setTimeout(() => {
                        btn.innerHTML = originalHTML;
                        btn.disabled = false;
                        btn.style.opacity = '1';
                    }, 2000);
                });
                
                // Open URL
                setTimeout(() => {
                    window.open(url, '_blank', 'noopener,noreferrer');
                }, 800);
            }

            // Refresh Button
            const refreshBtn = document.getElementById('refreshBtn');
            refreshBtn.addEventListener('click', function() {
                this.classList.add('fa-spin');
                showToast('Refreshing server status...');
                
                setTimeout(() => {
                    this.classList.remove('fa-spin');
                    
                    // Animate status badges
                    document.querySelectorAll('.status-badge').forEach(badge => {
                        badge.style.transform = 'scale(1.2)';
                        badge.style.transition = 'transform 0.3s ease';
                        
                        setTimeout(() => {
                            badge.style.transform = 'scale(1)';
                            badge.classList.toggle('online');
                            badge.classList.toggle('offline');
                            badge.textContent = badge.classList.contains('online') ? 'Active' : '24/7';
                        }, 200);
                    });
                }, 1500);
            });

            // Banner Hover Effects
            const banners = document.querySelectorAll('.banner-card');
            banners.forEach(banner => {
                banner.addEventListener('mouseenter', () => {
                    banner.style.zIndex = '20';
                });
                
                banner.addEventListener('mouseleave', () => {
                    banner.style.zIndex = '1';
                });
                
                // Touch feedback
                banner.addEventListener('touchstart', () => {
                    banner.style.transform = 'scale(0.98)';
                });
                
                banner.addEventListener('touchend', () => {
                    banner.style.transform = '';
                });
            });

            // Animate elements on load
            setTimeout(() => {
                // Animate banners
                banners.forEach((banner, index) => {
                    banner.style.opacity = '0';
                    banner.style.transform = 'translateY(30px)';
                    
                    setTimeout(() => {
                        banner.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                        banner.style.opacity = '1';
                        banner.style.transform = 'translateY(0)';
                    }, index * 200);
                });
                
                // Animate server cards
                const cards = document.querySelectorAll('.server-card');
                cards.forEach((card, index) => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    
                    setTimeout(() => {
                        card.style.transition = 'all 0.5s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 600 + (index * 100));
                });
            }, 300);

            // Social button actions
            document.querySelectorAll('.social-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const social = this.getAttribute('data-social');
                    let url = '#';
                    
                    switch(social) {
                        case 'github': url = 'https://github.com/Stuner'; break;
                        case 'telegram': url = 'https://t.me/Stuner'; break;
                        case 'discord': url = 'https://discord.gg/stuner'; break;
                        case 'code': url = 'https://github.com/Stuner/server-dashboard'; break;
                    }
                    
                    showToast(`Opening ${social}...`);
                    
                    setTimeout(() => {
                        window.open(url, '_blank', 'noopener,noreferrer');
                    }, 500);
                });
            });

            // Auto GIF animation effect
            setInterval(() => {
                // Random banner glow effect
                const randomBanner = banners[Math.floor(Math.random() * banners.length)];
                randomBanner.style.boxShadow = '0 0 60px rgba(76, 175, 80, 0.6)';
                
                setTimeout(() => {
                    randomBanner.style.boxShadow = '';
                }, 1000);
                
                // Status dot pulse
                const dot = document.querySelector('.status-dot');
                dot.style.animation = 'none';
                setTimeout(() => dot.style.animation = 'pulse 2s infinite', 10);
            }, 4000);
        });
    </script>
</body>
</html>
"""

# 3. ADMIN PANEL (Remains same)
ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel</title>
    <style>
        :root {
            --primary: #8A2BE2;
            --secondary: #FF69B4;
            --dark: #1A1A2E;
            --light: #f8f9fa;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .back-link {
            color: white;
            text-decoration: none;
            margin-bottom: 20px;
            display: inline-block;
        }
        
        table {
            width: 100%;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 30px;
        }
        
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        th {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .btn {
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 5px;
        }
        
        .btn-approve {
            background: #00B894;
            color: white;
        }
        
        .btn-reject {
            background: #D63031;
            color: white;
        }
        
        .login-form {
            max-width: 400px;
            margin: 100px auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 10px;
            text-align: center;
        }
        
        .login-form input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: none;
            border-radius: 5px;
        }
        
        .login-form button {
            width: 100%;
            padding: 12px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    {% if not logged_in %}
    <div class="login-form">
        <h2>Admin Login</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Admin Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
    {% else %}
    <div class="container">
        <a href="/" class="back-link">← Back to Main</a>
        <div class="header">
            <h1>Admin Panel</h1>
            <p>Manage Device Approvals</p>
        </div>

        <h2>Pending Approvals</h2>
        <table>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for device in pending %}
                <tr>
                    <td>{{ device }}</td>
                    <td>
                        <form method="POST" action="/admin/approve" style="display: inline;">
                            <input type="hidden" name="device_id" value="{{ device }}">
                            <button type="submit" class="btn btn-approve">Approve</button>
                        </form>
                        <form method="POST" action="/admin/reject" style="display: inline;">
                            <input type="hidden" name="device_id" value="{{ device }}">
                            <button type="submit" class="btn btn-reject">Reject</button>
                        </form>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="2" style="text-align: center;">No pending devices</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h2>Approved Devices</h2>
        <table>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for device in approved %}
                <tr>
                    <td>{{ device }}</td>
                    <td>
                        <form method="POST" action="/admin/reject" style="display: inline;">
                            <input type="hidden" name="device_id" value="{{ device }}">
                            <button type="submit" class="btn btn-reject">Revoke</button>
                        </form>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="2" style="text-align: center;">No approved devices</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h2>Rejected Devices</h2>
        <table>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for device in rejected %}
                <tr>
                    <td>{{ device }}</td>
                    <td>
                        <form method="POST" action="/admin/approve" style="display: inline;">
                            <input type="hidden" name="device_id" value="{{ device }}">
                            <button type="submit" class="btn btn-approve">Approve</button>
                        </form>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="2" style="text-align: center;">No rejected devices</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}
</body>
</html>
"""

# ================= DATA MANAGEMENT =================

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            # Convert to list format if it's in dict format
            if isinstance(data.get("approved"), dict):
                data["approved"] = list(data["approved"].keys())
            return data
    except:
        pass
    
    return {
        "approved": [],  # Now using list instead of dict
        "pending": [],
        "rejected": []
    }

def save_data():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(approved_data, f, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")

approved_data = load_data()

def get_permanent_device_id():
    try:
        fingerprint_parts = [
            request.headers.get('User-Agent', ''),
            request.headers.get('Accept-Language', ''),
            str(uuid.getnode())
        ]
        fingerprint = "|".join(filter(None, fingerprint_parts))
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:16]
    except:
        return str(uuid.uuid4())[:16]

# ================= ROUTES =================

@app.route("/", methods=["GET", "POST"])
def index():
    """Initial page - shows approval system"""
    device_id = request.cookies.get("device_id") or get_permanent_device_id()

    if request.method == "POST":
        if (device_id not in approved_data["approved"] and 
            device_id not in approved_data["pending"] and 
            device_id not in approved_data["rejected"]):
            approved_data["pending"].append(device_id)
            save_data()
        
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("device_id", device_id, max_age=60*60*24*365)
        return resp

    if device_id in approved_data["approved"]:
        status = "approved"
    elif device_id in approved_data["pending"]:
        status = "pending"
    elif device_id in approved_data["rejected"]:
        status = "rejected"
    else:
        status = "new"

    return render_template_string(APPROVAL_PAGE, 
                               device_id=device_id,
                               status=status)

@app.route("/dashboard")
def dashboard():
    """Modern Dashboard - shown after approval"""
    device_id = request.cookies.get("device_id")
    
    if not device_id:
        return redirect("/")
    
    if device_id not in approved_data["approved"]:
        # If not approved, show appropriate status
        if device_id in approved_data["pending"]:
            return redirect("/?status=pending")
        elif device_id in approved_data["rejected"]:
            return redirect("/?status=rejected")
        else:
            return redirect("/")
    
    # Show the modern dashboard
    return render_template_string(MODERN_DASHBOARD)

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if request.method == "POST" and "password" in request.form:
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            return render_template_string(ADMIN_PANEL_HTML,
                                          logged_in=True,
                                          pending=approved_data["pending"],
                                          approved=approved_data["approved"],
                                          rejected=approved_data["rejected"])
    
    return render_template_string(ADMIN_PANEL_HTML, logged_in=False)

@app.route("/admin/approve", methods=["POST"])
def admin_approve():
    device_id = request.form.get("device_id", "").strip()
    if device_id:
        # Remove from pending and rejected lists
        if device_id in approved_data["pending"]:
            approved_data["pending"].remove(device_id)
        if device_id in approved_data["rejected"]:
            approved_data["rejected"].remove(device_id)
        # Add to approved list
        if device_id not in approved_data["approved"]:
            approved_data["approved"].append(device_id)
        save_data()
    return redirect(url_for("admin_panel"))

@app.route("/admin/reject", methods=["POST"])
def admin_reject():
    device_id = request.form.get("device_id", "").strip()
    if device_id:
        # Remove from pending and approved lists
        if device_id in approved_data["pending"]:
            approved_data["pending"].remove(device_id)
        if device_id in approved_data["approved"]:
            approved_data["approved"].remove(device_id)
        # Add to rejected list
        if device_id not in approved_data["rejected"]:
            approved_data["rejected"].append(device_id)
        save_data()
    return redirect(url_for("admin_panel"))

if __name__ == '__main__':
    print("🚀 Starting Integrated System...")
    print("🌐 Main URL: http://127.0.0.1:5000")
    print("🔧 Admin Panel: http://127.0.0.1:5000/admin")
    print("📱 Dashboard: http://127.0.0.1:5000/dashboard (after approval)")
    print("\n📋 Flow: User → Approval System → Modern Dashboard")
    app.run(host='0.0.0.0', port=5000, debug=True)
