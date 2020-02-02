emacs -batch -l "~/.emacs.d/init.el"  \
      -f org-clock-csv-batch-and-exit \
      ~/org/*.org \
      > clock.csv

python convert_csv_clock_to_json.py
