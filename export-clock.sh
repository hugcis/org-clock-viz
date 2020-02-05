emacs -batch -l "~/.emacs.d/init.el"  \
      -f org-clock-csv-batch-and-exit \
      ~/org/*.org \
      > static/data/clock.csv

python convert_csv_clock_to_json.py -d current_week \
       < static/data/clock.csv \
       > static/data/clock.json

export FLASK_APP=app.py
export FLASK_ENV=development
flask run
