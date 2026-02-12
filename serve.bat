@echo off
echo Starting order.life dev server at http://localhost:8000
python -m http.server 8000 --directory site
