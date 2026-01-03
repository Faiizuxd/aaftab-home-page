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

ADMIN_PASSWORD = "STUN3R_X_FAIZU"  # Change this!
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
    <title>Secure Access</title>
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
            --primary-green: #0a2f1d;
            --secondary-green: #14532d;
            --card-green: #1e3a2d;
            --accent-teal: #0d9488;
            --accent-lime: #84cc16;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --text-primary: #f0fdf4;
            --text-secondary: #bbf7d0;
            --text-muted: #86efac;
            --shadow-color: rgba(6, 78, 59, 0.2);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, var(--primary-green), #064e3b);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        .container {
            max-width: 100%;
            min-height: 100vh;
            padding: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Header Image */
        .header-image {
            width: 100%;
            height: 140px;
            object-fit: cover;
            border-radius: 12px;
            margin-bottom: 15px;
            border: 2px solid rgba(20, 83, 45, 0.5);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }

        /* Auth Card */
        .auth-card {
            background: rgba(30, 58, 45, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            width: 100%;
            max-width: 380px;
            border: 1px solid rgba(13, 148, 136, 0.3);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
        }

        .logo {
            text-align: center;
            margin-bottom: 15px;
        }

        .logo h1 {
            font-size: 20px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 4px;
        }

        .logo p {
            color: var(--text-muted);
            font-size: 12px;
            font-weight: 400;
        }

        /* Device ID Display */
        .device-id-container {
            background: rgba(13, 148, 136, 0.1);
            border: 1px solid rgba(13, 148, 136, 0.2);
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
        }

        .device-id-label {
            display: block;
            font-size: 12px;
            color: var(--accent-teal);
            margin-bottom: 6px;
            font-weight: 500;
        }

        .device-id {
            font-family: 'SF Mono', 'Courier New', monospace;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            word-break: break-all;
            padding: 8px 10px;
            background: rgba(0, 0, 0, 0.15);
            border-radius: 6px;
            border-left: 3px solid var(--accent-emerald);
        }

        /* Status Messages */
        .status-container {
            margin: 15px 0;
            padding: 12px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.03);
            text-align: center;
        }

        .status-icon {
            font-size: 24px;
            margin-bottom: 8px;
        }

        .status-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .status-pending {
            color: var(--accent-amber);
        }

        .status-approved {
            color: var(--accent-emerald);
        }

        .status-rejected {
            color: var(--accent-rose);
        }

        .status-message {
            color: var(--text-secondary);
            line-height: 1.4;
            font-size: 13px;
            opacity: 0.9;
        }

        /* Buttons */
        .btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 18px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            width: 100%;
            border: none;
            margin: 6px 0;
            text-decoration: none;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-emerald), var(--accent-teal));
            color: white;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
        }

        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(16, 185, 129, 0.3);
        }

        .btn-outline {
            background: transparent;
            border: 1px solid var(--accent-emerald);
            color: var(--accent-emerald);
        }

        .btn-outline:hover {
            background: rgba(16, 185, 129, 0.08);
        }

        /* Admin Link */
        .admin-link {
            position: absolute;
            top: 12px;
            right: 12px;
            color: var(--text-muted);
            font-size: 11px;
            text-decoration: none;
            background: rgba(255, 255, 255, 0.07);
            padding: 5px 10px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s;
        }

        .admin-link:hover {
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.1);
        }

        /* Info Text */
        .info-text {
            color: var(--text-muted);
            font-size: 11px;
            margin-top: 12px;
            line-height: 1.3;
            text-align: center;
            padding: 0 8px;
        }

        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: var(--accent-emerald);
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 20px;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            color: var(--text-muted);
            font-size: 10px;
        }

        /* Animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .auth-card {
            animation: fadeIn 0.4s ease-out;
        }

        /* Copy Indicator */
        .copy-indicator {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(30, 58, 45, 0.9);
            padding: 10px 20px;
            border-radius: 8px;
            border: 1px solid var(--accent-emerald);
            color: var(--accent-emerald);
            font-size: 13px;
            z-index: 1000;
            display: none;
            animation: fadeIn 0.3s;
        }
    </style>
</head>
<body>
    <a href="/admin" class="admin-link">
        <i class="fas fa-lock"></i> Admin
    </a>
    
    <div class="container">
        <div class="auth-card">
            <!-- Header Image - Full Width -->
            <img src="https://i.pinimg.com/originals/fe/7d/22/fe7d22e8088f2585aac9eb3c3bd6d62e.jpg" alt="Security Shield" class="header-image">
            
            <div class="logo">
                <h1>Secure Access</h1>
                <p>Device verification system</p>
            </div>

            <div class="device-id-container">
                <span class="device-id-label">DEVICE ID</span>
                <div class="device-id">{{ device_id }}</div>
            </div>

            {% if status == "pending" %}
                <div class="status-container">
                    <div class="status-icon status-pending">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="status-title status-pending">Pending</div>
                    <p class="status-message">Awaiting admin approval. Contact with Device ID.</p>
                </div>
                <a href="https://www.facebook.com/profile.php?id=61577314876827" class="btn btn-outline">
                    <i class="fas fa-headset"></i> Contact Admin
                </a>
                
            {% elif status == "approved" %}
                <div class="status-container">
                    <div class="status-icon status-approved">
                        <i class="fas fa-check"></i>
                    </div>
                    <div class="status-title status-approved">Approved</div>
                    <p class="status-message">Access granted. Redirecting...</p>
                </div>
                <a href="/dashboard" class="btn btn-primary" id="dashboardBtn">
                    <i class="fas fa-rocket"></i> Dashboard
                </a>
                
            {% elif status == "rejected" %}
                <div class="status-container">
                    <div class="status-icon status-rejected">
                        <i class="fas fa-times"></i>
                    </div>
                    <div class="status-title status-rejected">Denied</div>
                    <p class="status-message">Access rejected. Contact support.</p>
                </div>
                <a href="https://www.facebook.com/profile.php?id=100088520533630" class="btn btn-outline">
                    <i class="fas fa-headset"></i> Support
                </a>
                
            {% else %}
                <form method="POST" id="approvalForm">
                    <input type="hidden" name="device_id" value="{{ device_id }}">
                    <button type="submit" class="btn btn-primary" id="submitBtn">
                        <i class="fas fa-paper-plane"></i> Request Access
                    </button>
                </form>
                <p class="info-text">
                    <i class="fas fa-info-circle"></i> 
                    Save Device ID. Clearing data revokes access.
                </p>
            {% endif %}
            
            <div class="footer">
                Secure Access &copy; 2023
            </div>
        </div>
    </div>

    <!-- Copy Indicator -->
    <div class="copy-indicator" id="copyIndicator">Copied!</div>

    <script>
        // Auto-redirect if approved
        {% if status == "approved" %}
        setTimeout(function() {
            document.getElementById('dashboardBtn').click();
        }, 1200);
        {% endif %}

        // Form submission animation
        document.getElementById('approvalForm')?.addEventListener('submit', function(e) {
            const btn = document.getElementById('submitBtn');
            btn.innerHTML = '<span class="loading"></span> Processing';
            btn.disabled = true;
        });

        // Copy device ID on click
        document.querySelector('.device-id')?.addEventListener('click', function() {
            const deviceId = "{{ device_id }}";
            navigator.clipboard.writeText(deviceId).then(() => {
                // Show copy indicator
                const indicator = document.getElementById('copyIndicator');
                indicator.style.display = 'block';
                
                setTimeout(() => {
                    indicator.style.display = 'none';
                }, 1500);
            });
        });

        // Add subtle hover effect to card
        document.querySelector('.auth-card').addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.3)';
        });

        document.querySelector('.auth-card').addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 12px 30px rgba(0, 0, 0, 0.25)';
        });
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
    <linke.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Reset & Base - Compact */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0a1a0f 0%, #0c2c1a 100%);
            color: #ffffff;
            min-heighh;
            overflow-x: hidden;
            font-size: 14px;
            line-height: 1.4;
        }

        .container {
            max-width: 100%;
            min-height: 100vh;
            padding: 10px;
            padding-bottom: 60px;
        }

        /* Header - Compact */
        .app-header {
            background: rgba(18, 38, 24, 0.95);
            backdrop-filter: blur(10px);
            padding: 12px 15px;
            border-radius: 16px;
            margin-bottom: 12px;
            border: 1px solid rgba(76, 175, 80, 0.2);
            box-shadow: 0 4px 15px rgba(0, 20, 10, 0.2);
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .logo i {
            font-size: 20px;
            color: #4caf50;
            background: rgba(76, 175, 80, 0.1);
            padding: 8px;
            border-radius: 12px;
        }

        .logo h1 {
            font-size: 16px;
            font-weight: 600;
            color: #4caf50;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: #a5d6a7;
            background: rgba(76, 175, 80, 0.1);
            padding: 5px 10px;
            border-radius: 15px;
        }

        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #4caf50;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }

        /* Section Title - Small */
        .section-title {
            font-size: 14px;
            margin: 15px 0 10px;
            color: #e8f5e9;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Server Cards - Compact */
        .servers-grid {
            display: grid;
            gap: 12px;
        }

        /* Server Card Container */
        .server-card-container {
            background: rgba(30, 50, 35, 0.8);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(76, 175, 80, 0.15);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
            margin-bottom: 8px;
        }

        .server-card-container:hover {
            transform: translateY(-2px);
            border-color: rgba(76, 175, 80, 0.3);
            box-shadow: 0 8px 20px rgba(76, 175, 80, 0.2);
        }

        /* Banner - Small & Compact */
        .card-banner {
            height: 80px;
            position: relative;
            overflow: hidden;
        }

        .gif-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-size: cover;
            background-position: center;
        }

        /* Banner GIFs */
        .server-card-container[data-server="cookie"] .gif-overlay {
            background-image: url('https://i.pinimg.com/originals/5e/16/e3/5e16e3ab2987659e0b58baebb227162e.gif');
        }

        .server-card-container[data-server="endtoend"] .gif-overlay {
            background-image: url('https://i.pinimg.com/originals/80/b1/cf/80b1cf27df714a3ba0da909fd3f3f221.gif');
        }

        .server-card-container[data-server="whatsapp"] .gif-overlay {
            background-image: url('https://i.pinimg.com/originals/64/9c/66/649c668b6c1208cce1c7da2b539f8d72.gif');
        }

        /* Banner Overlay */
        .banner-overlay {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
            padding: 8px 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .banner-title h3 {
            font-size: 14px;
            color: white;
            font-weight: 600;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
        }

        .banner-badge {
            background: rgba(76, 175, 80, 0.9);
            color: white;
            padding: 5px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
            border: 1px solid rgba(255, 255, 255, 0.2);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .banner-badge:hover {
            background: rgba(102, 187, 106, 0.9);
        }

        /* Server Card Content - Compact */
        .server-card {
            padding: 12px;
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }

        .server-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .server-card-container[data-server="cookie"] .server-icon {
            color: #ff9800;
            background: rgba(255, 152, 0, 0.1);
        }

        .server-card-container[data-server="endtoend"] .server-icon {
            color: #9c27b0;
            background: rgba(156, 39, 176, 0.1);
        }

        .server-card-container[data-server="whatsapp"] .server-icon {
            color: #25d366;
            background: rgba(37, 211, 102, 0.1);
        }

        .card-header h3 {
            font-size: 15px;
            flex: 1;
            color: #ffffff;
            font-weight: 500;
        }

        .status-badge {
            padding: 4px 8px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: 500;
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .status-badge.online {
            color: #4caf50;
        }

        .status-badge.offline {
            color: #ff9800;
        }

        .card-body {
            margin-bottom: 12px;
        }

        .server-description {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.4;
            margin-bottom: 10px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.15);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .server-stats {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .stat {
            display: flex;
            align-items: center;
            gap: 5px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 11px;
            background: rgba(0, 0, 0, 0.15);
            padding: 5px 8px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .stat i {
            font-size: 11px;
            color: #4caf50;
        }

        /* Server Button - Compact */
        .server-btn {
            background: linear-gradient(135deg, #2e7d32, #4caf50);
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            width: 100%;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 3px 10px rgba(76, 175, 80, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .server-btn:hover {
            background: linear-gradient(135deg, #388e3c, #66bb6a);
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }

        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple-animation 0.4s linear;
        }

        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }

        /* Owner Section - Compact */
        .owner-section {
            margin-top: 20px;
        }

        .owner-card {
            background: linear-gradient(135deg, rgba(27, 94, 32, 0.2), rgba(56, 142, 60, 0.15));
            border-radius: 16px;
            padding: 15px;
            border: 1px solid rgba(76, 175, 80, 0.2);
            animation: soft-glow 3s ease-in-out infinite alternate;
        }

        @keyframes soft-glow {
            from {
                box-shadow: 0 0 10px rgba(76, 175, 80, 0.1);
            }
            to {
                box-shadow: 0 0 20px rgba(76, 175, 80, 0.2);
            }
        }

        .owner-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }

        .owner-avatar {
            position: relative;
            width: 50px;
            height: 50px;
        }

        .owner-avatar i {
            font-size: 50px;
            color: #4caf50;
        }

        .badge {
            position: absolute;
            bottom: -2px;
            right: -2px;
            background: linear-gradient(135deg, #ff9800, #ffb74d);
            color: white;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 9px;
            border: 2px solid rgba(30, 50, 35, 0.9);
        }

        .owner-info h3 {
            font-size: 16px;
            color: #ffffff;
            margin-bottom: 4px;
        }

        .owner-tag {
            display: flex;
            align-items: center;
            gap: 4px;
            color: #4caf50;
            font-size: 11px;
            background: rgba(76, 175, 80, 0.1);
            padding: 3px 8px;
            border-radius: 10px;
        }

        .owner-description {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 15px;
            line-height: 1.4;
            padding: 12px;
            background: rgba(0, 0, 0, 0.15);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .highlight {
            color: #4caf50;
            font-weight: 600;
        }

        .owner-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 8px;
            margin-bottom: 15px;
        }

        .detail {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px;
            background: rgba(0, 0, 0, 0.15);
            border-radius: 10px;
            font-size: 11px;
            transition: all 0.2s ease;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .detail:hover {
            background: rgba(76, 175, 80, 0.15);
            transform: translateX(3px);
        }

        .detail i {
            color: #4caf50;
            font-size: 12px;
        }

        /* Social Buttons - Small */
        .social-links {
            display: flex;
            gap: 8px;
            justify-content: center;
        }

        .social-btn {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            border: none;
            background: rgba(255, 255, 255, 0.08);
            color: #c8e6c9;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .social-btn:hover {
            background: rgba(76, 175, 80, 0.25);
            transform: translateY(-2px);
        }

        /* Footer - Compact */
        .app-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(18, 38, 24, 0.95);
            backdrop-filter: blur(10px);
            padding: 10px 15px;
            border-top: 1px solid rgba(76, 175, 80, 0.15);
            z-index: 100;
            box-shadow: 0 -2px 15px rgba(0, 20, 10, 0.2);
        }

        .footer-content {
            text-align: center;
            color: #a5d6a7;
            font-size: 11px;
        }

        .footer-content p {
            margin-bottom: 4px;
        }

        .footer-links {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            font-size: 10px;
        }

        .status.online {
            color: #4caf50;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* Toast - Small */
        .toast {
            position: fixed;
            bottom: 60px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: rgba(30, 50, 35, 0.95);
            backdrop-filter: blur(15px);
            padding: 10px 15px;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0, 20, 10, 0.3);
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 1000;
            border-left: 3px solid #4caf50;
            display: none;
            max-width: 90%;
            font-size: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .toast.show {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
            display: block;
        }

        .toast-content {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .toast-content i {
            color: #4caf50;
            font-size: 14px;
        }

        /* Floating Button - Small */
        .fab {
            position: fixed;
            bottom: 65px;
            right: 15px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2e7d32, #4caf50);
            color: white;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
            z-index: 99;
            transition: all 0.2s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .fab:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.5);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Compact Header -->
        <header class="app-header">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-server"></i>
                    <h1>Server Control</h1>
                </div>
                <div class="status-indicator">
                    <span class="status-dot"></span>
                    <span>Online</span>
                </div>
            </div>
        </header>

        <!-- Server Panels - Compact -->
        <h2 class="section-title"><i class="fas fa-th"></i> Servers</h2>
        
        <div class="servers-grid">
            <!-- Cookie Server -->
            <div class="server-card-container" data-server="cookie">
                <div class="card-banner">
                    <div class="gif-overlay"></div>
                    <div class="banner-overlay">
                        <div class="banner-title">
                            <h3>Cookie Server</h3>
                        </div>
                        <div class="banner-badge" data-url="http://prem-eu3.bot-hosting.net:20946/">
                            Open
                        </div>
                    </div>
                </div>
                
                <div class="server-card">
                    <div class="card-header">
                        <div class="server-icon">
                            <i class="fas fa-cookie-bite"></i>
                        </div>
                        <h3>Cookie Server</h3>
                         <span class="status-badge offline">24/7</span>
                    </div>
                    <div class="card-body">
                        <p class="server-description">
                            Hi! This is Cookie Server — Offline 24/7
                        </p>
                        <div class="server-stats">
                            <div class="stat">
                                <i class="fas fa-bolt"></i>
                                <span>Fast</span>
                            </div>
                            <div class="stat">
                                <i class="fas fa-shield-alt"></i>
                                <span>Secure</span>
                            </div>
                        </div>
                    </div>
                    <button class="server-btn open-server-btn" data-url="http://prem-eu3.bot-hosting.net:20946/">
                        <span class="btn-text">Open Server</span>
                        <i class="fas fa-external-link-alt"></i>
                        <span class="ripple"></span>
                    </button>
                </div>
            </div>

            <!-- End To End Server -->
            <div class="server-card-container" data-server="endtoend">
                <div class="card-banner">
                    <div class="gif-overlay"></div>
                    <div class="banner-overlay">
                        <div class="banner-title">
                            <h3>End To End Server</h3>
                        </div>
                        <div class="banner-badge" data-url="https://stunere2e.streamlit.app/">
                            Open
                        </div>
                    </div>
                </div>
                
                <div class="server-card">
                    <div class="card-header">
                        <div class="server-icon">
                            <i class="fas fa-exchange-alt"></i>
                        </div>
                        <h3>End To End Server</h3>
                        <span class="status-badge online">Active</span>
                    </div>
                    <div class="card-body">
                        <p class="server-description">
                            Hi! This is End To End Server for Inbox / Group
                        </p>
                        <div class="server-stats">
                            <div class="stat">
                                <i class="fas fa-comments"></i>
                                <span>Groups</span>
                            </div>
                            <div class="stat">
                                <i class="fas fa-inbox"></i>
                                <span>Inbox</span>
                            </div>
                        </div>
                    </div>
                    <button class="server-btn open-server-btn" data-url="https://stunere2e.streamlit.app/">
                        <span class="btn-text">Open Server</span>
                        <i class="fas fa-external-link-alt"></i>
                        <span class="ripple"></span>
                    </button>
                </div>
            </div>

            <!-- WhatsApp Server -->
            <div class="server-card-container" data-server="whatsapp">
                <div class="card-banner">
                    <div class="gif-overlay"></div>
                    <div class="banner-overlay">
                        <div class="banner-title">
                            <h3>WhatsApp Server</h3>
                        </div>
                        <div class="banner-badge" data-url="http://prem-eu1.bot-hosting.net:20488/">
                            Open
                        </div>
                    </div>
                </div>
                
                <div class="server-card">
                    <div class="card-header">
                        <div class="server-icon">
                            <i class="fab fa-whatsapp"></i>
                        </div>
                        <h3>WhatsApp Server</h3>
                        <span class="status-badge offline">24/7</span>
                    </div>
                    <div class="card-body">
                        <p class="server-description">
                            Hi! This is WhatsApp Offline Server — 24/7
                        </p>
                        <div class="server-stats">
                            <div class="stat">
                                <i class="fas fa-clock"></i>
                                <span>24/7</span>
                            </div>
                            <div class="stat">
                                <i class="fas fa-mobile-alt"></i>
                                <span>Mobile</span>
                            </div>
                        </div>
                    </div>
                    <button class="server-btn open-server-btn" data-url="http://prem-eu1.bot-hosting.net:20488/">
                        <span class="btn-text">Open Server</span>
                        <i class="fas fa-external-link-alt"></i>
                        <span class="ripple"></span>
                    </button>
                </div>
            </div>
        </div>

        <!-- Owner Section - Compact -->
        <div class="owner-section">
            <h2 class="section-title"><i class="fas fa-crown"></i> Owner</h2>
            <div class="owner-card">
                <div class="owner-header">
                    <div class="owner-avatar">
                        <i class="fas fa-user-circle"></i>
                        <div class="badge">
                            <i class="fas fa-crown"></i>
                        </div>
                    </div>
                    <div class="owner-info">
                        <h3>APK Owner</h3>
                        <div class="owner-tag">
                            <i class="fas fa-check-circle"></i>
                            <span>Verified</span>
                        </div>
                    </div>
                </div>
                <div class="owner-body">
                    <p class="owner-description">
                        Hi, I'm <span class="highlight">Stuner</span>, the Owner of this APK.
                    </p>
                    <div class="owner-details">
                        <div class="detail">
                            <i class="fas fa-code"></i>
                            <span>Developer</span>
                        </div>
                        <div class="detail">
                            <i class="fas fa-server"></i>
                            <span>Server Expert</span>
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
                    </div>
                </div>
            </div>
        </div>

        <!-- Floating Button -->
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
            <p>© 2026Server Dashboard v1.5</p>
            <div class="footer-links">
                <span class="status online">
                    <i class="fas fa-circle"></i>
                    All Systems Go
                </span>
            </div>
        </div>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Button Click Handler
            function handleButtonClick(e, url) {
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
                setTimeout(() => ripple.remove(), 400);
                
                // Open URL
                openServer(url);
            }

            // Banner Click
            document.querySelectorAll('.banner-badge').forEach(banner => {
                banner.addEventListener('click', function(e) {
                    e.stopPropagation();
                    handleButtonClick.call(this, e, this.getAttribute('data-url'));
                });
            });

            // Server Button Click
            document.querySelectorAll('.server-btn').forEach(button => {
                button.addEventListener('click', function(e) {
                    handleButtonClick.call(this, e, this.getAttribute('data-url'));
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
                }, 2000);
            }

            // Open Server Function
            function openServer(url) {
                showToast('Opening server...');
                
                // Loading effect
                const buttons = document.querySelectorAll('.open-server-btn, .banner-badge');
                buttons.forEach(btn => {
                    const originalText = btn.textContent;
                    
                    if(btn.classList.contains('banner-badge')) {
                        btn.textContent = 'Opening...';
                    } else {
                        btn.querySelector('.btn-text').textContent = 'Opening...';
                        btn.querySelector('.fa-external-link-alt').className = 'fas fa-spinner fa-spin';
                    }
                    
                    btn.disabled = true;
                    btn.style.opacity = '0.6';
                    
                    setTimeout(() => {
                        if(btn.classList.contains('banner-badge')) {
                            btn.textContent = originalText;
                        } else {
                            btn.querySelector('.btn-text').textContent = 'Open Server';
                            btn.querySelector('.fa-spinner').className = 'fas fa-external-link-alt';
                        }
                        btn.disabled = false;
                        btn.style.opacity = '1';
                    }, 1500);
                });
                
                // Open URL
                setTimeout(() => {
                    window.open(url, '_blank', 'noopener,noreferrer');
                }, 600);
            }

            // Refresh Button
            const refreshBtn = document.getElementById('refreshBtn');
            refreshBtn.addEventListener('click', function() {
                this.classList.add('fa-spin');
                showToast('Refreshing...');
                
                setTimeout(() => {
                    this.classList.remove('fa-spin');
                    
                    // Toggle status
                    document.querySelectorAll('.status-badge').forEach(badge => {
                        badge.style.transform = 'scale(1.1)';
                        setTimeout(() => {
                            badge.style.transform = 'scale(1)';
                            badge.classList.toggle('online');
                            badge.classList.toggle('offline');
                            badge.textContent = badge.classList.contains('online') ? 'Active' : '24/7';
                        }, 200);
                    });
                }, 1000);
            });

            // Social Buttons
            document.querySelectorAll('.social-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const social = this.getAttribute('data-social');
                    let url = '#';
                    
                    switch(social) {
                        case 'github': url = 'https://github.com/Stuner'; break;
                        case 'telegram': url = 'https://t.me/Stuner'; break;
                        case 'discord': url = 'https://discord.gg/stuner'; break;
                    }
                    
                    showToast(`Opening ${social}...`);
                    
                    setTimeout(() => {
                        window.open(url, '_blank');
                    }, 500);
                });
            });

            // Touch Feedback
            const cards = document.querySelectorAll('.server-card-container');
            cards.forEach(card => {
                card.addEventListener('touchstart', function() {
                    this.style.transform = 'scale(0.98)';
                });
                
                card.addEventListener('touchend', function() {
                    this.style.transform = '';
                });
            });

            // Animate on load
            setTimeout(() => {
                cards.forEach((card, index) => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(15px)';
                    
                    setTimeout(() => {
                        card.style.transition = 'all 0.3s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, index * 100);
                });
            }, 200);
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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-dark: #0a2f1d;
            --secondary-dark: #14532d;
            --card-green: #1e3a2d;
            --accent-teal: #0d9488;
            --accent-lime: #84cc16;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --text-primary: #f0fdf4;
            --text-secondary: #bbf7d0;
            --text-muted: #86efac;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, var(--primary-dark), #064e3b);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .back-link {
            color: var(--text-muted);
            text-decoration: none;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 20px;
            transition: color 0.2s;
        }
        
        .back-link:hover {
            color: var(--text-primary);
        }
        
        /* Header Styles */
        .header-image {
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 2px solid rgba(20, 83, 45, 0.5);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 8px;
            color: var(--text-primary);
        }
        
        .header p {
            color: var(--text-muted);
            font-size: 14px;
        }

        /* Login Page Styles */
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .login-card {
            background: rgba(30, 58, 45, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 30px;
            width: 100%;
            max-width: 420px;
            border: 1px solid rgba(13, 148, 136, 0.3);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
            text-align: center;
        }

        .login-header {
            margin-bottom: 25px;
        }

        .login-image {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 2px solid rgba(20, 83, 45, 0.5);
        }

        .login-form {
            margin-top: 20px;
        }
        
        .login-form input {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border: 1px solid rgba(13, 148, 136, 0.3);
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.2);
            color: var(--text-primary);
            font-size: 14px;
            transition: border 0.3s;
        }
        
        .login-form input:focus {
            outline: none;
            border-color: var(--accent-emerald);
        }
        
        .login-form button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, var(--accent-emerald), var(--accent-teal));
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 500;
            margin-top: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .login-form button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(16, 185, 129, 0.3);
        }

        /* Table Styles */
        .section-title {
            font-size: 20px;
            margin: 30px 0 15px 0;
            color: var(--text-primary);
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(13, 148, 136, 0.3);
        }
        
        .table-container {
            background: rgba(30, 58, 45, 0.8);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 30px;
            border: 1px solid rgba(13, 148, 136, 0.2);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        th {
            background: rgba(13, 148, 136, 0.15);
            color: var(--accent-teal);
            font-weight: 600;
            font-size: 14px;
        }
        
        td {
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        tr:hover {
            background: rgba(255, 255, 255, 0.03);
        }
        
        .empty-row {
            text-align: center;
            color: var(--text-muted);
            font-style: italic;
        }

        /* Button Styles */
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .btn-approve {
            background: linear-gradient(135deg, var(--accent-emerald), #0d9488);
            color: white;
        }
        
        .btn-reject {
            background: linear-gradient(135deg, var(--accent-rose), #dc2626);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }
        
        .action-form {
            display: inline;
        }
        
        .action-buttons {
            display: flex;
            gap: 8px;
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            color: var(--text-muted);
            font-size: 12px;
        }

        /* Animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .table-container, .login-card {
            animation: fadeIn 0.4s ease-out;
        }
    </style>
</head>
<body>
    {% if not logged_in %}
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <img src="https://i.pinimg.com/originals/cf/da/23/cfda23e905a14b316ca3eb230827e039.jpg" alt="Admin Security" class="login-image">
                <h1>Admin Login</h1>
                <p>Secure access control panel</p>
            </div>
            <form method="POST" class="login-form">
                <input type="password" name="password" placeholder="Enter admin password" required>
                <button type="submit">
                    <i class="fas fa-sign-in-alt"></i> Login
                </button>
            </form>
        </div>
    </div>
    {% else %}
    <div class="container">
        <a href="/" class="back-link">
            <i class="fas fa-arrow-left"></i> Back to Main
        </a>
        
        <img src="https://i.pinimg.com/originals/0c/b5/4f/0cb54f43a57ea25f6f1ee4ca4947f056.jpg" alt="Admin Dashboard" class="header-image">
        
        <div class="header">
            <h1>Admin Control Panel</h1>
            <p>Manage device authorizations and access control</p>
        </div>

        <h2 class="section-title">⏳ Pending Approvals</h2>
        <div class="table-container">
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
                            <div class="action-buttons">
                                <form method="POST" action="/admin/approve" class="action-form">
                                    <input type="hidden" name="device_id" value="{{ device }}">
                                    <button type="submit" class="btn btn-approve">
                                        <i class="fas fa-check"></i> Approve
                                    </button>
                                </form>
                                <form method="POST" action="/admin/reject" class="action-form">
                                    <input type="hidden" name="device_id" value="{{ device }}">
                                    <button type="submit" class="btn btn-reject">
                                        <i class="fas fa-times"></i> Reject
                                    </button>
                                </form>
                            </div>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="2" class="empty-row">No pending devices</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <h2 class="section-title">✅ Approved Devices</h2>
        <div class="table-container">
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
                            <form method="POST" action="/admin/reject" class="action-form">
                                <input type="hidden" name="device_id" value="{{ device }}">
                                <button type="submit" class="btn btn-reject">
                                    <i class="fas fa-ban"></i> Revoke
                                </button>
                            </form>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="2" class="empty-row">No approved devices</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <h2 class="section-title">❌ Rejected Devices</h2>
        <div class="table-container">
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
                            <form method="POST" action="/admin/approve" class="action-form">
                                <input type="hidden" name="device_id" value="{{ device }}">
                                <button type="submit" class="btn btn-approve">
                                    <i class="fas fa-check"></i> Approve
                                </button>
                            </form>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="2" class="empty-row">No rejected devices</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>Admin Panel • Secure Access System &copy; 2023</p>
        </div>
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
